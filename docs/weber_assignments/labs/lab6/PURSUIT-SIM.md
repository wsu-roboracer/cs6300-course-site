# Lab 7 Sim - Pure Pursuit

## I. Learning Goals

- Understand the Pure Pursuit geometric path tracking algorithm
- Implement a ROS 2 node that reads waypoints from CSV and follows the path
- Compute steering angles from a lookahead point
- Create a launch file with configurable parameters
- Tune lookahead distance and speed for smooth autonomous driving

## II. Overview

In Lab 6 you recorded a CSV of poses while driving the track yourself. In this lab you
build the **Pure Pursuit node** that reads those waypoints and drives the path
autonomously, and you do it in the simulator, alone, before your team runs it on a car in
Lab 7 Car.

Pure Pursuit is a geometric algorithm. On each cycle the node finds the point on the
recorded path roughly one lookahead distance ahead of the car, transforms it into the
car's own frame, and steers along the arc that reaches it.

You localize with the **particle filter** on `/pf/pose/odom`, the same topic you logged
against in Lab 6 and the same one the car publishes. Nothing in this node should read
`/ego_racecar/odom`: a node tuned against perfect ground truth falls apart the first time
it meets a real position estimate.

| Part | Task | What You Learn |
|------|------|----------------|
| 1 | Create the config file and launch file | ROS 2 launch files, YAML parameters |
| 2 | Write the Pure Pursuit node | Path tracking, geometry, `AckermannDriveStamped` |
| 3 | Test and tune in simulation | Lookahead distance, speed, stability |

## III. Prerequisites

- Your Lab 6 repository, with the `pure_pursuit` package and your recorded
  `maps/waypoints.csv`. There is no new repository: you keep working in the one you
  already have.
- The simulator set to the map you recorded on: `map_path: 'maps/levine_blocked'` in
  `config/sim.yaml`
- The particle filter built and launching against that same map

If your Lab 6 CSV is short, noisy, or was recorded while the filter was not localized, fix
that first. Pure Pursuit cannot drive a path better than the path it was given.

## IV. Getting Started

```bash
cd ~/f1tenth_ws
colcon build --packages-select pure_pursuit
source install/setup.bash
```

## V. Part 1 — Config File and Launch File

1. Create `pure_pursuit/config/pure_pursuit.yaml` with three parameters:

   - `lookahead_distance` - how far ahead on the path to aim, in meters
   - `speed` - the commanded speed, in meters per second
   - `waypoints_file` - the path to your CSV

2. Create `pure_pursuit/launch/pure_pursuit_launch.py`, which starts your node and loads
   that YAML.
3. Update `setup.py` so both the launch file and the config directory are installed as
   data files, and the node is registered in `console_scripts`. A launch file that is not
   installed cannot be launched.

## VI. Part 2 — Write the Pure Pursuit Node

Fill in the TODOs in `pure_pursuit/pure_pursuit/pure_pursuit_node.py`.

1. **Load** the waypoints from the CSV at startup, into a list of `(x, y)` points
2. **Subscribe** to `/pf/pose/odom` for the car's current pose
3. **Find the lookahead point**: the first waypoint at least `lookahead_distance` away from
   the car, searching forward along the path
4. **Transform** it into the car's frame
5. **Compute** the steering angle
6. **Publish** `AckermannDriveStamped` on `/drive` with that angle and the configured speed

### The Pure Pursuit Formula

With the lookahead point transformed into the car's frame, where `y` is the lateral offset
(positive to the left):

```
steering_angle = 2 * y / L^2
```

`L` is the actual distance to the lookahead point. This falls out of the geometry of the
circular arc from the car to that point.

### Wrapping the Path

The path is a loop, so the search for the lookahead point has to wrap from the end of the
list back to the start. A node that stops steering at the last row drives straight into a
wall on lap two.

### Build

```bash
cd ~/f1tenth_ws
colcon build --packages-select pure_pursuit
source install/setup.bash
```

## VII. Part 3 — Test and Tune in Simulation

1. Start the simulator on `levine_blocked`.
2. Launch the particle filter and set the **2D Pose Estimate** so it converges, exactly as
   in Lab 6. The filter must be localized before you start, or the node will steer toward
   a path it is not actually on.
3. Launch your node:

   ```bash
   ros2 launch pure_pursuit pure_pursuit_launch.py
   ```

4. Watch it drive, in RViz2 and in the simulator window.

### Tuning

Start slow - 1.0 m/s and a lookahead of about 1.0 m - and raise the speed only once it
completes clean laps.

- **Lookahead too short**: the car oscillates, sawing back and forth across the path
- **Lookahead too long**: the car cuts corners and drifts wide of the recorded line
- **Faster speeds** generally want a longer lookahead

Record what you tried. The write-up asks for it, and the numbers you settle on here are
the starting point your team tunes from on the car.

## VIII. Submitting

1. Commit and push your node, launch file, config, and `setup.py` changes.
2. Record an unlisted YouTube video of the car completing at least one full autonomous lap
   in the simulator, with RViz2 showing the localized particle filter and the path.
3. Fill in the write-up section of `SUBMISSION.md`.
4. **Submit two links in the Canvas text box**: the URL of your repository, and the URL of
   the video.

## IX. Deliverables

| # | Deliverable | Points |
|---|-------------|--------|
| 1 | `pure_pursuit_node.py`, taking its pose from `/pf/pose/odom` | 20 |
| 2 | `pure_pursuit_launch.py` and `pure_pursuit.yaml` | 10 |
| 3 | `setup.py`, with the entry point and data files | 10 |
| 4 | Demonstration video (unlisted YouTube): at least one full autonomous lap in the simulator, following your recorded waypoints | 35 |
| 5 | Write-up in `SUBMISSION.md` (3-5 sentences): what lookahead distance and speed did you settle on, and what happened when you changed them? | 25 |

**Total: 100 Points**
