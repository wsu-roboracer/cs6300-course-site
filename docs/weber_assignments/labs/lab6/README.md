# Lab 6a - Waypoint Logger for Pure Pursuit

## I. Learning Goals

- Create a ROS 2 Python package from scratch
- Subscribe to a localization topic and extract pose data
- Write pose data to a CSV file in real time
- Understand how the particle filter provides map-relative position
- Prepare waypoint data for the Pure Pursuit algorithm

## II. Overview

In the Pure Pursuit pipeline, the car needs a pre-recorded path to follow. That path is a CSV file of poses (x, y, heading) captured while you manually drive the track. In this lab you will build the **waypoint logger node** that records those poses.

The particle filter publishes the car's estimated position on the map at ~30-40 Hz on `/pf/pose/odom`. Your node will subscribe to that topic and append each pose to a CSV file. The resulting file will be used in the next lab (Pure Pursuit) to drive the car autonomously.

| Part | Task | What You Learn |
|------|------|----------------|
| 1 | Create the `pure_pursuit` package | ROS 2 package structure, `ament_python`, dependencies |
| 2 | Write the waypoint logger node | Subscriptions, Odometry messages, CSV file I/O |
| 3 | Record a lap of waypoints | Running nodes, particle filter localization, data collection |
| 4 | Verify and visualize the waypoints | Data validation, CSV inspection |

## III. Prerequisites

- Completed **Lab 5** (SLAM — you have a saved map)
- Particle filter configured and working (see the Particle Filter tutorial)
- Comfortable creating files and editing Python on the robot

## IV. Part 1 — Create the Package

Create a new ROS 2 Python package on the robot:

```bash
cd ~/f1tenth_ws/src
ros2 pkg create pure_pursuit --build-type ament_python --dependencies rclpy nav_msgs geometry_msgs visualization_msgs std_msgs
```

Create a directory for your waypoint CSV files:

```bash
mkdir -p ~/f1tenth_ws/src/pure_pursuit/maps
```

## V. Part 2 — Write the Waypoint Logger Node

Create the file `pure_pursuit/pure_pursuit/waypoint_logger.py`. Your node must:

1. **Subscribe** to `/pf/pose/odom` (message type: `nav_msgs/msg/Odometry`)
2. **Open a CSV file** for writing when the node starts (save to `~/f1tenth_ws/src/pure_pursuit/maps/waypoints.csv`)
3. **In the callback**, extract the pose from each Odometry message and write a row to the CSV:
   - `x` — `msg.pose.pose.position.x`
   - `y` — `msg.pose.pose.position.y`
   - `z` — `msg.pose.pose.orientation.z` (quaternion z, used to reconstruct heading)
   - `w` — `msg.pose.pose.orientation.w` (quaternion w)
4. **Filter by minimum distance** — only record a new waypoint if the car has moved at least **0.1 meters** from the last recorded point. Recording at full 30-40 Hz frequency while the car is slow or jerky produces noisy, densely-clustered waypoints that make pure pursuit oscillate. Spacing waypoints by distance instead of time solves this without post-processing.
5. **Print a confirmation** so you know poses are being recorded (e.g., print every 50th pose to avoid flooding the terminal)
6. **Close the CSV file cleanly** when the node shuts down (Ctrl+C)

### Hints

- Use Python's built-in `csv` module or simply write comma-separated strings
- The CSV should have **no header row** — just the four values per line: `x, y, z, w`
- The Odometry message definition is in `nav_msgs.msg`. Import it with:

  ```python
  from nav_msgs.msg import Odometry
  ```

- To handle clean shutdown, close the file in a `try/finally` block or override `destroy_node()`
- For the minimum distance filter, compute Euclidean distance using `math.hypot(x - self.last_x, y - self.last_y)` and skip the write if it is less than `0.1`. Track `self.last_x` and `self.last_y` and update them only when a waypoint is actually written

### Live Visualization (Provided Code)

Your waypoint logger can publish markers to RViz2 so you can see the path growing in real time as you drive. The `pf.rviz` layout already has these displays configured — no RViz setup needed.

Add these imports to your `waypoint_logger.py`:

```python
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import ColorRGBA
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy, QoSHistoryPolicy
```

Add this to your `__init__` method:

```python
latched_qos = QoSProfile(
    depth=1,
    durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
    reliability=QoSReliabilityPolicy.RELIABLE,
    history=QoSHistoryPolicy.KEEP_LAST,
)
self.marker_pub = self.create_publisher(MarkerArray, '/waypoint_viz/waypoints', latched_qos)
self.path_pub = self.create_publisher(Path, '/waypoint_viz/path', latched_qos)
self.path_msg = Path()
self.path_msg.header.frame_id = 'map'
self.marker_array = MarkerArray()
```

Add this method to your class — call it each time you record a waypoint (after writing to the CSV):

```python
def publish_waypoint_viz(self, x, y, z, w):
    """Publishes the current list of waypoints to RViz for live visualization."""
    m = Marker()
    m.header.frame_id = 'map'
    m.header.stamp = self.get_clock().now().to_msg()
    m.ns = 'waypoints'
    m.id = len(self.marker_array.markers)
    m.type = Marker.SPHERE
    m.action = Marker.ADD
    m.pose.position.x = x
    m.pose.position.y = y
    m.scale.x = 0.1
    m.scale.y = 0.1
    m.scale.z = 0.1
    m.color = ColorRGBA(r=1.0, g=1.0, b=0.0, a=1.0)
    m.pose.orientation.w = 1.0
    self.marker_array.markers.append(m)
    self.marker_pub.publish(self.marker_array)

    ps = PoseStamped()
    ps.header.frame_id = 'map'
    ps.pose.position.x = x
    ps.pose.position.y = y
    ps.pose.orientation.z = z
    ps.pose.orientation.w = w
    self.path_msg.poses.append(ps)
    self.path_msg.header.stamp = self.get_clock().now().to_msg()
    self.path_pub.publish(self.path_msg)
```

In your odom callback, after writing to the CSV, call:

```python
self.publish_waypoint_viz(x, y, z, w)
```

You should see yellow dots and an orange path line building in RViz2 as you drive.

### Register the Entry Point

Edit `setup.py` in the `pure_pursuit` package. Add your node to the `console_scripts` list:

```python
entry_points={
    'console_scripts': [
        'waypoint_logger = pure_pursuit.waypoint_logger:main',
    ],
},
```

### Build

```bash
cd ~/f1tenth_ws
colcon build --packages-select pure_pursuit
source install/setup.bash
```

## VI. Part 3 — Record a Lap

1. Start **bringup** (Terminal 1)
2. Launch the **particle filter** (Terminal 2):

   ```bash
   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ros2 launch particle_filter localize_launch.py
   ```

3. Open **RViz2** with the particle filter config (Terminal 3):

   ```bash
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   rviz2 -d ~/f1tenth_ws/install/particle_filter/share/particle_filter/rviz/pf.rviz
   ```

   Set the **2D Pose Estimate** so the particle filter is localized. **The particle filter must be localized before you start recording** — if it is not, your waypoints will be meaningless.

4. Run your **waypoint logger** (Terminal 4):

   ```bash
   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ros2 run pure_pursuit waypoint_logger
   ```

   If you implemented the live visualization code, you should see yellow dots and an orange path appearing in RViz2 as soon as the car moves.

5. Using the PlayStation controller, **drive a complete lap** of the track at a moderate, consistent speed
6. When you return to the starting position, press **Ctrl+C** to stop the logger

**Tips for a good recording:**

- Drive at the speed you want the car to follow autonomously later
- Cover the entire track — drive all sections at least once
- Close the loop — finish near where you started
- Avoid sharp jerks or corrections, as they will be recorded into the path

## VII. Part 4 — Verify the Recording

Check that your CSV was created and contains data:

```bash
wc -l ~/f1tenth_ws/src/pure_pursuit/maps/waypoints.csv
```

With the minimum distance filter implemented, a full lap at moderate speed should produce **several hundred waypoints**. If the count is very low, the particle filter may not have been localized — re-run with the initial pose set.

If you recorded without the distance filter and the file has too many points (tens of thousands), you can thin it down after the fact:

```bash
awk 'NR % 5 == 0' waypoints.csv > waypoints_clean.csv
```

This keeps every 5th row — a quick way to reduce density without re-recording.

Inspect the first few lines:

```bash
head -5 ~/f1tenth_ws/src/pure_pursuit/maps/waypoints.csv
```

You should see four comma-separated numbers per line (x, y, orientation_z, orientation_w).

## VIII. Deliverables

| # | Deliverable | Points |
|---|-------------|--------|
| 1 | Screenshot of your `waypoint_logger.py` source code | 25 |
| 2 | Screenshot of the terminal showing the logger running and recording poses as you drive | 25 |
| 3 | The `waypoints.csv` file submitted to Canvas | 25 |
| 4 | Screenshot of `wc -l` and `head -5` output showing the CSV has several hundred rows of valid data | 25 |

**Total: 100 Points**
