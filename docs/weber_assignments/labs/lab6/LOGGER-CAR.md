# Lab 6 Car - Waypoint Logger

## I. Learning Goals

- Work with a ROS 2 Python package: its folders, dependencies, and entry points
- Subscribe to a localization topic and extract pose data
- Write pose data to a CSV file in real time
- Understand how the particle filter provides map-relative position
- Prepare waypoint data for the Pure Pursuit algorithm

## II. Overview

In the Pure Pursuit pipeline, the car needs a pre-recorded path to follow. That path is a CSV file of poses (x, y, heading) captured while you manually drive the track. In this lab you will build the **waypoint logger node** that records those poses.

The particle filter publishes the car's estimated position on the map at ~30-40 Hz on `/pf/pose/odom`. Your node will subscribe to that topic and append each pose to a CSV file. The resulting file will be used in the next lab (Pure Pursuit) to drive the car autonomously.

| Part | Task | What You Learn |
|------|------|----------------|
| 1 | Get the repository and build the `pure_pursuit` package | ROS 2 package structure, `ament_python`, dependencies |
| 2 | Write the waypoint logger node | Subscriptions, Odometry messages, CSV file I/O |
| 3 | Record a lap of waypoints | Running nodes, particle filter localization, data collection |
| 4 | Verify and visualize the waypoints | Data validation, CSV inspection |

**One repository for Lab 6 and Lab 7.** Your team's repository holds the `pure_pursuit` package for both labs. In this lab you write the waypoint logger; in Lab 7 you add the Pure Pursuit node to the same package, in the same repository. Its instructions are in `PURSUIT-CAR.md`.

```text
pure_pursuit/
├── package.xml                      dependencies are already declared
├── setup.py                         Lab 6 Part 2, and Lab 7
├── maps/waypoints.csv               Lab 6 Part 3 records it here
└── pure_pursuit/
    ├── waypoint_logger.py           Lab 6 Part 2
    └── pure_pursuit_node.py         Lab 7
images/                              your screenshot goes here
SUBMISSION.md                        sections for Lab 6 and Lab 7
```

This lab is done in teams. Your team shares one repository.

## III. Prerequisites

- Completed **Lab 5** (SLAM — you have a saved map)
- Particle filter configured and working (see the Particle Filter tutorial)
- Comfortable creating files and editing Python on the robot

## IV. Part 1 — Get the Repository and Build the Package

1. Every member opens the **Create my lab repository** button on the Canvas assignment and chooses your team. The first member creates the team repository and the rest are added to it. Accept the invitation GitHub sends you. Lab 7 uses this same repository.
2. On the car, clone it into your workspace's `src` folder as `lab6`:

   ```bash
   cd ~/f1tenth_ws/src
   git clone <your repository URL> lab6
   ```

3. Build the package:

   ```bash
   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   colcon build --packages-select pure_pursuit
   source install/setup.bash
   ```

Look through `pure_pursuit/package.xml` and `pure_pursuit/setup.py` before you start: they are the same kind of package you built in Lab 1, with its dependencies already declared. All of you push to the one repository, so **pull before you push**.

## V. Part 2 — Write the Waypoint Logger Node

Finish `pure_pursuit/pure_pursuit/waypoint_logger.py`. Your node must:

1. **Subscribe** to `/pf/pose/odom` (message type: `nav_msgs/msg/Odometry`)
2. **Open a CSV file** for writing when the node starts (save to `~/f1tenth_ws/src/lab6/pure_pursuit/maps/waypoints.csv`, which is `CSV_PATH` in the skeleton)
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

Finish the Lab 6 `TODO` in `pure_pursuit/setup.py` by adding your node to the `console_scripts` list. Leave the Lab 7 `TODO`s for Lab 7.

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
wc -l ~/f1tenth_ws/src/lab6/pure_pursuit/maps/waypoints.csv
```

With the minimum distance filter implemented, a full lap at moderate speed should produce **several hundred waypoints**. If the count is very low, the particle filter may not have been localized — re-run with the initial pose set.

If you recorded without the distance filter and the file has too many points (tens of thousands), you can thin it down after the fact:

```bash
awk 'NR % 5 == 0' waypoints.csv > waypoints_clean.csv
```

This keeps every 5th row — a quick way to reduce density without re-recording.

Inspect the first few lines:

```bash
head -5 ~/f1tenth_ws/src/lab6/pure_pursuit/maps/waypoints.csv
```

You should see four comma-separated numbers per line (x, y, orientation_z, orientation_w).

## VIII. Submitting

1. Save a screenshot of the terminal with the logger recording as `images/logger_running.png`.
2. Commit and push your code, the CSV, and the screenshot:

   ```bash
   cd ~/f1tenth_ws/src/lab6
   git add pure_pursuit images
   git commit -m "Lab 6: waypoint logger and recorded lap"
   git push
   ```

3. Open `SUBMISSION.md` on github.com and check that the screenshot shows.
4. Submit the URL of your team's repository on the Lab 6 Canvas assignment. One submission covers the whole team.

Keep the repository: Lab 7 continues in it, and reads the waypoints you recorded here.

## IX. Deliverables

Everything is graded from your team's repository.

| # | Deliverable | Points |
|---|-------------|--------|
| 1 | `waypoint_logger.py`, with the entry point registered in `setup.py` | 25 |
| 2 | `images/logger_running.png`: the terminal showing the logger running and recording poses as you drive | 25 |
| 3 | `pure_pursuit/maps/waypoints.csv` committed | 25 |
| 4 | The CSV holds a full lap: several hundred rows of `x, y, z, w`, no header, spaced at least 0.1 m apart | 25 |

**Total: 100 Points**
