# Lab 4: Follow the Gap

## I. Learning Goals

- Reactive methods for obstacle avoidance

## II. Overview

In this lab, you will implement a reactive algorithm for obstacle avoidance. While the base starter code defines an implementation of the F1TENTH Follow the Gap Algorithm, you are allowed to submit in C++, and encouraged to try different reactive algorithms or a combination of several. In total, the python code for the algorithm is only about 120 lines.

## III. Review of F1TENTH Follow the Gap

The lecture slides on F1TENTH Follow the gap is the best visual resource for understanding every step of the algorithm. However, the steps are outlined over here:

1. Obtain laser scans and preprocess them.
2. Find the closest point in the LiDAR ranges array.
3. Draw a safety bubble around this closest point and set all points inside this bubble to 0. All other non-zero points are now considered “gaps” or “free space”.
4. Find the max length “gap”, in other words, the largest number of consecutive non-zero elements in your ranges array.
5. Find the best goal point in this gap. Naively, this could be the furthest point away in your gap, but you can probably go faster if you follow the “Better Idea” method as described in lecture.
6. Actuate the car to move towards this goal point by publishing an `AckermannDriveStamped` to the /drive topic.

### IV. Implementation

Implement a gap follow algorithm to make the car drive autonomously around the CAE hall course. You can implement this node in either C++ or Python.

Test in the [f1tenth_gym_ros](https://github.com/f1tenth/f1tenth_gym_ros/tree/dev-jazzy) simulator on two CAE hall course maps: `levine_blocked`, the empty CAE hall loop with its doorways sealed, and `levine_obs`, the loop with its corner doorways bricked up and thirteen obstacles added (a slalom of boxes and an ellipse on the south hallway, two triangles and a box on the north hallway) that are relatively hard to navigate through. Pick one with `map_path: 'maps/levine_blocked'` or `map_path: 'maps/levine_obs'` in `config/sim.yaml`. Both come with a centerline, so the simulator counts your laps (`/ego_racecar/lap_count`, and a "completed lap" line in the bridge log). Your lab is graded on the same two maps: `levine_blocked` counter-clockwise from the simulator's stock start pose (`sx: -12.0, sy: 0.0, stheta: 0.0`), on the south hallway heading east, 12 m before the finish line, so all three laps are flying laps and the lap times are the ones your bridge log prints (`completed lap N, last lap X s`); `levine_obs` counter-clockwise too, from the east hallway just past its south corner (`sx: 9.96, sy: 2.8, stheta: 1.5708` in `config/sim.yaml`), heading north, so the north-hallway obstacles and three corners come first and only a full lap has to thread the south-hallway slalom. Test both directions: an obstacle that is easy from one side can be a trap from the other (the L-shaped wall on the north hallway is a dead-end pocket with the way through above it).

Your node must subscribe to `/scan` and publish `AckermannDriveStamped` on `/drive`, and it must work when started with a plain `ros2 run gap_follow <executable>`: it is graded with no parameter file, so bake your tuned bubble size, thresholds and speeds into the node's defaults. Tip: a gap is only worth aiming at if the car fits through it; the closest-point bubble alone does not tell you that.

### V. Getting Started

**This lab is done in teams**, and from here on every lab is. Your team shares one repository.

1. Every member opens the **Create my lab repository** button on the Canvas assignment and chooses your team. The first member creates the team repository and the rest are added to it. Accept the invitation GitHub sends you.
2. Clone it into the `src` folder of your ROS 2 workspace, then build and source the workspace.

All of you push to that one repository, so **pull before you push**. One submission is the whole team's submission, and every member gets the same grade.

### VI. Deliverables and Submission

**Deliverable 1**: Finish the `gap_follow` package in your team's repository, then commit and push. Your committed code should start and run in simulation smoothly; this includes building as a package with any dependencies declared in `package.xml`. The basic requirement is that your car should be able to drive three laps in a row of the `levine_blocked` map without touching a wall, and through at least 3 corners of the `levine_obs` map. You get 5 bonus points if your implementation is able to complete all 4 corners and keeps lapping through the map.

Use the names this lab gives you: package `gap_follow` with an executable that starts with `ros2 run gap_follow <executable>` (the skeleton's `reactive_node`), subscribing to `/scan` and publishing on `/drive`.

**Deliverable 2**: Take a video of your team's algorithm running on the real car — one video for the team. Upload your video to YouTube (unlisted) or Google Drive — for Drive, set sharing to **"Anyone with the link can view"** or we cannot grade it — and include the link in **`SUBMISSION.md`**. You may use different parameters (i.e. a separate launch file) for the on-car deployment.

### Submitting

1. Commit and push your work. Check on github.com that your latest commit is there.
2. Submit the URL of your team's repository on the Canvas assignment.

### VII. Grading Rubric

| Item | What is graded | Points |
|------|----------------|--------|
| Compilation | The package builds | 10 |
| Implemented Find-Max Gap | With a pillar ahead of the car, and in a corridor with the car close to one wall, your node steers toward the wider gap. Each situation is also tried mirrored | 30 |
| Implemented Find best point | At a dead end with the corridor continuing to one side, your node aims into the exit. Also tried mirrored | 30 |
| CAE hall blocked simulation | Three counter-clockwise laps of the `levine_blocked` map in a row without touching a wall. A run that ends early earns partial credit for the fraction of the three-lap distance covered | 10 |
| CAE hall obstacles simulation | The `levine_obs` map counter-clockwise from the east, through at least 3 corners without touching anything. 1 or 2 corners earn partial credit | 5 |
| Real-car CAE hall video | The link in `SUBMISSION.md`: YouTube unlisted, or Google Drive shared as "Anyone with the link can view" | 15 |

**Total: 100 Points**

Bonus: **5** points for a full clean lap of the `levine_obs` map, all 4 corners, counter-clockwise from the same start.

### VIII. Extra Resources

UNC Follow the Gap Video: https://youtu.be/ctTJHueaTcY
