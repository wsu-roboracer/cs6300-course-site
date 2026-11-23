# Lab 6 Sim - Waypoint Logger

## I. Learning Goals

- Work with a ROS 2 Python package: its folders, dependencies, and entry points
- Subscribe to a localization topic and extract pose data
- Write pose data to a CSV file in real time
- Understand how the particle filter provides map-relative position
- Prepare waypoint data for the Pure Pursuit algorithm

## II. Overview

Pure Pursuit needs a path to follow, and that path is a CSV file of poses (x, y, heading)
captured while you drive the track yourself. In this lab you build the **waypoint logger
node** that records them, and you do it in the simulator, alone.

You localize with the **particle filter**, not with the simulator's own odometry. The
simulator publishes perfect ground truth on `/ego_racecar/odom`, and logging that would be
easier - but it would teach you nothing you can use on the car, and the waypoints would be
cleaner than anything the car can reproduce. The particle filter publishes its estimate on
`/pf/pose/odom`, which is the same topic, the same message type, and the same noise your
node will read on the car in Lab 6 Car. Writing against it here means the car part is a
port rather than a rewrite.

| Part | Task | What You Learn |
|------|------|----------------|
| 1 | Get the repository and build the `pure_pursuit` package | ROS 2 package structure, `ament_python`, dependencies |
| 2 | Write the waypoint logger node | Subscriptions, Odometry messages, CSV file I/O |
| 3 | Record a lap in simulation | Launching the particle filter, localizing on a map, data collection |
| 4 | Verify and visualize the waypoints | Data validation, CSV inspection |

## III. Prerequisites

- A working ROS 2 workspace with the `f1tenth_gym_ros` simulator, as in Labs 2 through 5
- The particle filter built in your workspace (see the Particle Filter Localization area
  on the course site)
- The CAE hall map: set `map_path: 'maps/levine_blocked'` in the simulator's
  `config/sim.yaml`, the same map Lab 3 and Lab 4 use

**One repository for Lab 6 and Lab 7.** Your repository holds the `pure_pursuit` package
for both labs. In this lab you write the waypoint logger; in Lab 7 you add the Pure
Pursuit node to the same package, in the same repository.

## IV. Part 1 — Get the Repository and Build the Package

1. Open the **Create my lab repository** button on the Canvas assignment to get your own
   copy, then clone it into the `src` folder of your ROS 2 workspace.
2. Build and source the workspace, and check that the `pure_pursuit` package is found:

   ```bash
   cd ~/f1tenth_ws
   colcon build --packages-select pure_pursuit
   source install/setup.bash
   ros2 pkg list | grep pure_pursuit
   ```

## V. Part 2 — Write the Waypoint Logger Node

Fill in the TODOs in `pure_pursuit/pure_pursuit/waypoint_logger.py`.

1. **Subscribe** to `/pf/pose/odom` (message type: `nav_msgs/msg/Odometry`)
2. **Extract** the pose from each message: `position.x`, `position.y`, and the orientation
   quaternion's `z` and `w`
3. **Filter** poses by distance, so a car standing still does not write thousands of
   identical rows. Keep a pose only when it is at least **0.1 m** from the last one kept.
4. **Append** each kept pose to `pure_pursuit/maps/waypoints.csv` as `x, y, z, w` - four
   numbers per line, no header
5. **Flush** as you go, so a `Ctrl+C` does not lose the recording

### Hints

- The quaternion's `z` and `w` are enough to reconstruct the heading, because the car
  rotates about one axis only
- `math.hypot(x - last_x, y - last_y)` is the distance test
- Open the file once, in the constructor, rather than once per message

### Register the Entry Point

Add the node to `console_scripts` in `setup.py`, then rebuild:

```bash
cd ~/f1tenth_ws
colcon build --packages-select pure_pursuit
source install/setup.bash
```

## VI. Part 3 — Record a Lap in Simulation

1. Start the **simulator** with `map_path: 'maps/levine_blocked'`, the way you did in
   Lab 3 and Lab 4.
2. Launch the **particle filter** against that same map:

   ```bash
   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ros2 launch particle_filter localize_launch.py
   ```

3. Open **RViz2** with the particle filter config:

   ```bash
   rviz2 -d ~/f1tenth_ws/install/particle_filter/share/particle_filter/rviz/pf.rviz
   ```

   Set the **2D Pose Estimate** on the car's actual position so the filter converges.
   **The particle filter must be localized before you start recording** - if it is not,
   your waypoints are meaningless. A converged filter shows its particle cloud collapsed
   tightly around the car and `/pf/pose/odom` tracking it as you drive.

4. Run your **waypoint logger**:

   ```bash
   ros2 run pure_pursuit waypoint_logger
   ```

5. **Drive a complete lap** with keyboard teleop at a moderate, consistent speed.
6. When you return to where you started, press **Ctrl+C** to stop the logger.

**Tips for a good recording:**

- Drive at the speed you want Pure Pursuit to follow later
- Cover the whole track, and close the loop near where you started
- Avoid sharp corrections: they get recorded into the path and the car will copy them
- Watch the particle cloud. If the filter diverges mid-lap, discard the CSV and start over

## VII. Part 4 — Verify the Recording

```bash
wc -l pure_pursuit/maps/waypoints.csv      # several hundred rows for a full lap
head -3 pure_pursuit/maps/waypoints.csv    # four numbers per line, no header
```

A full lap at moderate speed produces **several hundred** waypoints. A very low count
usually means the particle filter was not localized, or your distance filter is too
coarse.

## VIII. Submitting

1. Commit and push your node, your `setup.py` change, the CSV, and your screenshot.
2. Record an unlisted YouTube video of the logger recording while you drive in the
   simulator, with RViz2 showing the localized particle filter.
3. **Submit two links in the Canvas text box**: the URL of your repository, and the URL of
   the video. A video that has to be downloaded to watch is not graded.

## IX. Deliverables

| # | Deliverable | Points |
|---|-------------|--------|
| 1 | `waypoint_logger.py`, with the entry point registered in `setup.py` | 25 |
| 2 | `pure_pursuit/maps/waypoints.csv` committed, holding a full lap: several hundred rows of `x, y, z, w`, no header, spaced at least 0.1 m apart | 30 |
| 3 | `images/logger_running.png`: RViz2 showing the particle filter localized and the logger recording as you drive | 20 |
| 4 | Demonstration video (unlisted YouTube) of a full lap being recorded in the simulator | 25 |

**Total: 100 Points**
