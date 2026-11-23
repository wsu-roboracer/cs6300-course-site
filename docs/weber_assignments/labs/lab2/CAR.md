# Lab 2 Car - Automatic Emergency Braking

## I. Learning Goals

- Move a working ROS 2 node from the simulator onto real hardware
- Remap topics for a different platform without rewriting the node
- See what a real lidar returns that a simulated one does not: noise, dropouts, and stray readings
- Understand where a safety node sits in the car's command chain, and what outranks it
- Test a safety-critical system on a vehicle without damaging it

## II. Overview

In Lab 2 Sim you wrote a safety node and showed it braking in the simulator. In this lab your
team runs that node on a real RoboRacer in the CAE hallway, and discovers which of your
tuning survived the move.

This is the half the simulator cannot teach you. Your iTTC maths does not change. What
changes is everything feeding it: the lidar has noise and dropouts, odometry comes from
wheel speed rather than ground truth, and the car carries momentum that no reset button
undoes.

| Part | Task | What You Learn |
| --- | --- | --- |
| 1 | Port the node to the car's topics | Platform differences, remapping, parameters |
| 2 | Bench test with the wheels off the ground | Safe hardware bring-up, verifying before driving |
| 3 | Tune against a real lidar in the hallway | Sensor noise, false positives, thresholds |
| 4 | Record the demonstration and hand in the video | Evidencing a safety-critical result |

**This lab is done in teams, in class.** Your team runs one node - pick the one that worked
best in Lab 2 Sim, and say in your write-up whose it was. There is no new repository: you work
in the Lab 2 Sim repository of whichever team member's node you chose.

## III. Prerequisites

- Your node passes `tests/check_lab2.py` in Lab 2 Sim. Do not bring an unfinished node to the car.
- You have completed the car bring-up tutorial and can drive the car with the controller.
- Your team has been assigned a car and a session.

## IV. Part 1 - Port the Node to the Car

Three topics matter, and only one of them changes.

| What | Simulator (Lab 2 Sim) | The car (Lab 2 Car) |
| --- | --- | --- |
| Lidar | `/scan` | `/scan` - unchanged |
| Odometry | `/ego_racecar/odom` | **`/odom`** |
| Drive command | `/drive` | `/drive` - unchanged |

The car's odometry comes from `vesc_to_odom_node`, which publishes `nav_msgs/Odometry` on
`/odom`. The message type is the same as the simulator's, so `twist.twist.linear.x` is still
where you read the speed - only the topic name moved.

Make the topic a parameter rather than editing the string, so that one node runs on both
platforms:

```bash
ros2 run safety_node safety_node.py --ros-args -p odom_topic:=/odom
```

Then confirm what you are actually subscribed to, before the wheels ever turn:

```bash
ros2 topic list                    # is /odom there, and /scan?
ros2 topic hz /scan                # the Hokuyo should be about 40 Hz
ros2 topic echo /odom --once       # does twist.twist.linear.x move when you push the car?
ros2 node info /safety_node        # are your subscriptions connected to the real topics?
```

A node subscribed to `/ego_racecar/odom` on the car does not error. It sits there reading a
speed of zero forever, which means your iTTC never drops and your node never brakes. Check
the connection, do not assume it.

### What outranks your node

The car runs an `ackermann_mux` that chooses between command sources by priority:

| Input | Topic | Priority |
| --- | --- | --- |
| Joystick | `/teleop` | **100** |
| Navigation | `/drive` | 10 |

Your node publishes on `/drive`, at priority 10. **The controller outranks it.** Holding the
throttle on the controller overrides anything your safety node says, which is exactly why
the person holding the controller is the real emergency stop in this lab, and why they keep
hold of it for every run.

The mux also drops an input that goes quiet for more than 0.2 s. A node that publishes one
brake command and then stops talking will have its input timed out, and the car will take
commands from whatever else is publishing. Keep publishing your zero-speed command for as
long as the hazard is there.

Because the controller cannot be braked by your node, something else has to drive the car
forward for the demo. Use a simple constant-speed node - a few lines publishing
`AckermannDriveStamped` with a fixed low speed on `/drive` - and let your safety node
publish zero speed on the same topic when iTTC drops. Commit it as
`scripts/drive_forward.py` so the instructor can start it.

## V. Part 2 - Bench Test First

**Do this before the car ever drives.** Put the car on a stand or a box with all four wheels
clear of the ground, start bring-up and your nodes, and walk a board or a notebook toward
the lidar.

- The wheels should spin while nothing is in front of the car.
- They should stop when the board comes inside your braking distance.
- They should start again when you take it away, if your node releases the brake.

If the wheels do not stop on the bench, they will not stop on the floor. Fix it here, where
the car cannot go anywhere, and only then put it down.

**Record this one too.** The bench test is on the rubric, and it is the easiest clip in the
lab to get: the car cannot run away from you while you film it.

## VI. Part 3 - Tune in the Hallway

Work up to speed. Start at **1.0 m/s** and raise it only when the car brakes cleanly at the
speed you are already at.

**Safety procedure for every run:**

1. One team member holds the controller for the entire run, thumb on the throttle, and drives
   the car manually to abort - the joystick outranks `/drive`.
2. One team member watches the hallway and calls out people walking into it.
3. Clear the hallway before each run, and announce the run.
4. Nobody stands between the car and the wall it is braking for.
5. Start the car at least 5 m from the wall so there is room to brake.

Expect two failures, in this order:

**It brakes in an empty hallway.** Real lidar scans contain `inf`, `nan`, dropouts, and
occasional short readings that no obstacle produced. One bad beam at 0.3 m with the car at
2 m/s is an iTTC of 0.15 s, and a node that trusts any single beam brakes for it. Your check
script fed you `inf` and `nan`, so you handle those - but it did not feed you a plausible-
looking wrong reading. Look at how many beams agree before you brake, and over how many
scans.

**It brakes too late.** The simulator stops instantly. A real car has mass, a drivetrain that
takes time to reverse, and tires that slide on a dusty floor. Braking at an iTTC that was
comfortable in simulation can still end against the wall. Measure the stopping distance you
actually get and set your threshold from that, not from the simulator's.

Record what you changed and why. That is most of your write-up.

## VII. Part 4 - The Demonstration, Recorded

You demonstrate this in class, with your team's car, and you **record it**. The video is what
you hand in: it is what gets graded, and it is the only part of this lab that survives the
session. One video for the team.

Record these four, in one session, and put them in the same upload as your bench test clip
from Part 2 - five things in total. One continuous video is easiest, but separate clips are
fine as long as they all arrive at the same link:

1. **No false positives** - the car drives at least 10 m down a clear hallway at your
   demonstration speed without braking.
2. **It stops for a wall** - the car drives at a wall and stops without touching it.
3. **It stops for an obstacle that appears** - a team member steps into the hallway in front
   of the moving car, at a distance you have already tested, and the car stops.
4. **It is reading the car, not the simulator** - `ros2 node info` for your node, with its
   subscriptions connected to `/scan` and `/odom`. Hold the terminal on screen long enough to
   read it.

Film in landscape, get the whole hallway and the car in frame, and say out loud what each run
is meant to show. A video where nobody can tell whether the car stopped or merely ran out of
hallway cannot be graded.

Upload it to YouTube as **unlisted**, then **paste the link into the text box on the Canvas
assignment**, along with your repository URL. The link goes on the Canvas submission, not in
`SUBMISSION.md`.

**YouTube only, and unlisted.** Not Google Drive, not a file, not a OneDrive or Box link: a video that has to be downloaded before it can be watched does not get graded. Unlisted means anyone with the link can watch it but it does not show up in search, so you are not publishing it to the world.

The instructor is there while you run it, and will ask what your threshold is and why, and what
you changed from your Lab 2 Sim values. Have an answer - but the grade comes off the video, so a
run nobody recorded did not happen.

## VIII. Submitting

1. Commit the ported node, your `drive_forward.py`, and any launch file or parameter file you
   used on the car.
2. Fill in the **Lab 2 Car** section of `SUBMISSION.md`: whose node you ran, your final
   parameters, and what the real lidar made you change. The video link does not go in there.
3. Commit and push. Check on github.com that your latest commit is there.
4. One team member submits on the Canvas assignment, pasting **both** the repository URL and
   the video link into the text box. One submission is the whole team's submission, and every
   member gets the same grade.

## IX. Grading Rubric

| Item | What is graded | Points |
| --- | --- | --- |
| Ported and connected | In the video: `ros2 node info` shows your node subscribed to `/scan` and `/odom`, not the simulator's topics | 15 |
| Bench test | In the video: the wheels stop for an obstacle with the car on a stand | 10 |
| No false positives | In the video: 10 m of clear hallway at demonstration speed with no braking | 25 |
| Stops for a wall | In the video: the car drives at a wall and stops without touching it | 25 |
| Stops for an obstacle that appears | In the video: the car stops for someone stepping into the hallway | 15 |
| Write-up | The **Lab 2 Car** section of `SUBMISSION.md`: final parameters, and what the real lidar changed | 10 |

**Total: 100 Points**

Everything but the write-up is graded from your team's video, so if a run is not on the video
it earns nothing - even if the instructor watched it happen.

Bonus: **5** points for a clean demonstration at 3.0 m/s or faster, on the video.
