# Lab 7 Car - Pure Pursuit

## I. Learning Goals

- Understand the Pure Pursuit geometric path tracking algorithm
- Implement a ROS 2 node that reads waypoints from CSV and follows the path
- Compute steering angles from a lookahead point
- Create a launch file with configurable parameters
- Tune lookahead distance and speed for smooth autonomous driving

## II. Overview

In Lab 6 you built a waypoint logger that records the car's path to a CSV file. In this lab you will build the **Pure Pursuit node** that reads those waypoints and drives the car autonomously along the recorded path.

Pure Pursuit is a geometric path tracking algorithm. On each update cycle:

1. Read the car's current pose from the particle filter (`/pf/pose/odom`)
2. Find the **lookahead point** — the point on the recorded path a fixed distance ahead of the car
3. Compute the **steering angle** to arc toward that lookahead point
4. Publish a drive command on `/drive`

| Part | Task | What You Learn |
|------|------|----------------|
| 1 | Create the config file and launch file | ROS 2 launch files, YAML parameters |
| 2 | Write the Pure Pursuit node | Path tracking, geometry, AckermannDriveStamped |
| 3 | Test on the robot | Tuning, localization, autonomous driving |

You keep working in your team's Lab 6 repository: this lab adds the Pure Pursuit node to the same `pure_pursuit` package. The parts you write are marked `TODO (Lab 7, ...)`:

```text
pure_pursuit/
├── setup.py                         Part 1
├── config/pure_pursuit.yaml         Part 1 (you create it)
├── launch/pure_pursuit_launch.py    Part 1 (you create it)
├── maps/waypoints.csv               recorded in Lab 6
└── pure_pursuit/
    ├── waypoint_logger.py           written in Lab 6
    └── pure_pursuit_node.py         Part 2
SUBMISSION.md                        Lab 7 section: video link and write-up
```

This lab is done in teams, in the same team repository as Lab 6.

## III. Prerequisites

- Completed **Lab 6**: your repository has a working `waypoint_logger.py` and a recorded `pure_pursuit/maps/waypoints.csv`
- Particle filter configured and working

## IV. Getting Started

There is no new repository for this lab. On the car, pull your team's latest work and rebuild:

```bash
cd ~/f1tenth_ws/src/lab6
git pull
cd ~/f1tenth_ws
colcon build --packages-select pure_pursuit
source install/setup.bash
```

All of you push to the one repository, so **pull before you push**.

## V. Part 1 — Config File and Launch File

### Create the Config File

Create `pure_pursuit/config/pure_pursuit.yaml` in your repository:

```yaml
pure_pursuit_node:
  ros__parameters:
    lookahead_distance: 1.5
    speed: 1.0
    waypoint_file: "waypoints.csv"
```

> **Note:** The top-level key `pure_pursuit_node:` in this YAML must match the node's name in two other places: `super().__init__('pure_pursuit_node')` in your Python class, and `name='pure_pursuit_node'` in the launch file. If any of these three don't match, ROS 2 won't load the parameters and your node will silently use the default values.

| Parameter | Description |
|-----------|-------------|
| `lookahead_distance` | How far ahead on the path to steer toward (meters). Larger = smoother but wider turns. Smaller = tighter tracking but more oscillation. |
| `speed` | Forward drive speed in m/s. Start low (0.5) for testing. |
| `waypoint_file` | Name of the CSV file in the `maps/` directory |

### Create the Launch File

Create `pure_pursuit/launch/pure_pursuit_launch.py` in your repository:

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('pure_pursuit'),
        'config',
        'pure_pursuit.yaml'
    )

    return LaunchDescription([
        Node(
            package='pure_pursuit',
            executable='pure_pursuit_node',
            name='pure_pursuit_node',
            parameters=[config],
            output='screen'
        )
    ])
```

### Update setup.py

Finish the two Lab 7 `TODO`s in `pure_pursuit/setup.py`.

Install the config, launch, and map files by adding these lines to the `data_files` list:

```python
(os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
(os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
(os.path.join('share', package_name, 'maps'), glob('maps/*.csv')),
```

Register the pure pursuit node in `console_scripts`, alongside the `waypoint_logger` you registered in Lab 6:

```python
entry_points={
    'console_scripts': [
        'waypoint_logger = pure_pursuit.waypoint_logger:main',
        'pure_pursuit_node = pure_pursuit.pure_pursuit_node:main',
    ],
},
```

## VI. Part 2 — Write the Pure Pursuit Node

Finish `pure_pursuit/pure_pursuit/pure_pursuit_node.py`. Your node must:

1. **Load parameters** — read `lookahead_distance`, `speed`, and `waypoint_file` from the parameter server
2. **Load waypoints from CSV** — read the waypoint file and store all poses as a list of `(x, y, z, w)` tuples
3. **Subscribe** to `/pf/pose/odom` (`nav_msgs/msg/Odometry`) for the car's current position
4. **Publish** on `/drive` (`ackermann_msgs/msg/AckermannDriveStamped`) to control the car
5. **In the callback**, implement the Pure Pursuit algorithm:
   - Find the **closest waypoint** to the car's current position
   - Starting from that closest waypoint, search forward along the path to find the first waypoint that is at least `lookahead_distance` away — this is the **lookahead point**
   - **Transform** the lookahead point from map frame to the car's local frame (the car needs to know if the point is to its left or right)
   - Compute the **steering angle** using the Pure Pursuit formula
   - Publish the drive command with the computed steering angle and configured speed

### The Pure Pursuit Formula

Given a lookahead point transformed into the car's local frame where `y` is the lateral offset (positive = left):

```
steering_angle = 2 * y / L^2
```

Where `L` is the actual distance to the lookahead point. This comes from the geometry of the circular arc that connects the car to the lookahead point.

### Coordinate Transform Hint

To transform a map-frame point `(gx, gy)` into the car's local frame given the car's pose `(cx, cy, heading)`:

```python
import math

# Translate
dx = gx - cx
dy = gy - cy

# Rotate into car's frame
local_x = dx * math.cos(-heading) - dy * math.sin(-heading)
local_y = dx * math.sin(-heading) + dy * math.cos(-heading)
```

To get the heading from quaternion `(z, w)`:

```python
heading = 2.0 * math.atan2(z, w)
```

### Wrapping the Path

When searching for the lookahead point, if you reach the end of the waypoint list, wrap around to the beginning. This allows the car to drive continuous laps.

### Build

```bash
cd ~/f1tenth_ws
colcon build --packages-select pure_pursuit
source install/setup.bash
```

## VII. Part 3 — Test on the Robot

1. Start **bringup** (Terminal 1)
2. Launch the **particle filter** (Terminal 2):

   ```bash
   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ros2 launch particle_filter localize_launch.py
   ```

3. Start **waypoint_viz** to see the recorded path and live lookahead target in RViz2 (Terminal 3):

   ```bash
   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ros2 run waypoint_viz waypoint_viz_node --ros-args \
     -p waypoint_file:=~/f1tenth_ws/src/lab6/pure_pursuit/maps/waypoints.csv
   ```

4. Open **RViz2** with the pre-configured particle filter layout (Terminal 4):

   ```bash
   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   rviz2 -d ~/f1tenth_ws/install/particle_filter/share/particle_filter/rviz/pf.rviz
   ```

   Set the **2D Pose Estimate** so the particle filter is localized before launching pure pursuit

5. Launch **Pure Pursuit** (Terminal 5):

   ```bash
   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ros2 launch pure_pursuit pure_pursuit_launch.py
   ```

6. The car should begin following the recorded waypoints. The green sphere in RViz2 shows the current lookahead target moving along the path in real time

> **Safety:** Start with a low speed (0.5 m/s) in the config file. Be ready to kill the node (Ctrl+C) or e-stop if the car behaves unexpectedly.

### Tuning

If the car doesn't track well, adjust parameters in `pure_pursuit.yaml` and rebuild:

| Problem | Fix |
|---------|-----|
| Car cuts corners aggressively | Decrease `lookahead_distance` |
| Car oscillates side to side | Increase `lookahead_distance`; reduce `speed` |
| Car drifts off path over time | Re-set initial pose in RViz2 (particle filter may have diverged) |
| Car immediately stops or spins | Initial pose not set — set 2D Pose Estimate and re-launch |

## VIII. Submitting

1. Record the video, and fill in the Lab 7 section of `SUBMISSION.md`.
2. Commit and push your work, including the parameters you settled on in `pure_pursuit.yaml`. Check on github.com that your latest commit is there.
3. Submit the URL of your team's repository on the Lab 7 Canvas assignment: the same URL you submitted for Lab 6. One submission covers the whole team.

## IX. Deliverables

Everything is graded from your team's repository.

| # | Deliverable | Points |
|---|-------------|--------|
| 1 | `pure_pursuit_node.py` | 20 |
| 2 | `pure_pursuit_launch.py` and `pure_pursuit.yaml` | 10 |
| 3 | `setup.py`, with the entry point and data files | 10 |
| 4 | Video link in `SUBMISSION.md`: the car autonomously following the recorded waypoints for at least one full lap (screen recording of RViz2 + real car). YouTube, unlisted | 40 |
| 5 | Write-up in `SUBMISSION.md` (3-5 sentences): What lookahead distance and speed did you settle on? What happened when you changed them? | 20 |

**Total: 100 Points**
