# Lab 1 - Introduction to ROS 2

## I. Learning Goals

- Get familiar with the ROS 2 workflow
- Write nodes with publishers, subscribers, and parameters
- Understand the structure of a ROS 2 package: its files and its dependencies
- Write a launch file

## II. Overview

In this lab you will finish a ROS 2 Python package called `lab1_pkg`. It has two nodes:

- `talker` publishes drive commands built from two parameters.
- `relay` listens to those commands and republishes them with the values tripled.

You will also write a launch file that starts both nodes, and answer three written questions.

Your repository already contains the package with the parts you must write marked `TODO`:

```text
lab1_pkg/
├── package.xml            Part 1
├── setup.py               Part 1 and Part 3
├── lab1_pkg/
│   ├── talker.py          Part 2
│   └── relay.py           Part 2
└── launch/
    └── lab1_launch.py     Part 3
SUBMISSION.md              Part 4
tests/check_lab1.py        scores your work
```

Use the names this lab gives you: package `lab1_pkg`, nodes `talker` and `relay`, topics `drive` and `drive_relay`, and launch file `lab1_launch.py`. The check script finds your work by these names.

This lab is done individually.

## III. Prerequisites

- Completed **Tutorial 1 - ROS 2 Intro and Turtlesim**
- A machine with ROS 2 Humble installed

## IV. Getting Started

1. Create your repository with the **Create my lab repository** button on the Canvas assignment, then accept the invitation GitHub sends you.
2. Create a workspace and clone your repository into its `src` folder:

   ```bash
   mkdir -p ~/lab1_ws/src
   cd ~/lab1_ws/src
   git clone <your repository URL>
   ```

3. Install the package's dependencies and build:

   ```bash
   cd ~/lab1_ws
   source /opt/ros/humble/setup.bash
   rosdep install --from-paths src --ignore-src -y
   colcon build
   source install/setup.bash
   ```

The package builds as it is, but it does nothing yet. Rebuild and source again after every change:

```bash
cd ~/lab1_ws
colcon build
source install/setup.bash
```

## V. Part 1 — The Package

1. In `package.xml`, declare the dependency on `ackermann_msgs`, the package that provides the `AckermannDriveStamped` message. Then run the `rosdep install` command from Getting Started again to install it.
2. In `setup.py`, register two executables, `talker` and `relay`, that run the `main()` functions in `talker.py` and `relay.py`.

Once this works, `ros2 pkg executables lab1_pkg` lists both.

## VI. Part 2 — The Nodes

You can see the fields of the message you will publish with:

```bash
ros2 interface show ackermann_msgs/msg/AckermannDriveStamped
```

### talker

Finish `talker.py` so that the node:

- declares two parameters, `v` and `d`, each defaulting to `0.0`
- publishes an `AckermannDriveStamped` message on the `drive` topic, with `drive.speed` set to `v` and `drive.steering_angle` set to `d`
- publishes from a timer with a period of 0.001 seconds
- reads the parameters each time it publishes, so a change made while it runs takes effect

Test it:

```bash
ros2 run lab1_pkg talker --ros-args -p v:=1.5 -p d:=0.25
```

In a second terminal:

```bash
ros2 topic echo /drive
ros2 param set /talker v 2.5
```

> **Tip:** `v` and `d` are floating-point parameters. Write `2.0`, not `2`, or ROS rejects the value.

### relay

Finish `relay.py` so that the node:

- subscribes to the `drive` topic
- for each message, publishes a new `AckermannDriveStamped` message on the `drive_relay` topic, with the speed and the steering angle each multiplied by 3

Test it by running `talker` in one terminal, `relay` in a second, and `ros2 topic echo /drive_relay` in a third.

## VII. Part 3 — The Launch File

1. Finish `launch/lab1_launch.py` so that it starts both nodes and sets the talker's `v` and `d` parameters.
2. In `setup.py`, add the `launch` folder to `data_files` so the launch file is installed with the package.

Rebuild, then start both nodes with one command:

```bash
ros2 launch lab1_pkg lab1_launch.py
```

## VIII. Part 4 — ROS 2 Commands and Written Questions

With the launch file running, try these commands in a second terminal:

```bash
ros2 topic list
ros2 topic info /drive
ros2 topic echo /drive
ros2 node list
ros2 node info /talker
ros2 node info /relay
```

Then answer the three questions in `SUBMISSION.md`.

## IX. Check Your Work

Stop any nodes you have running, then run the check script:

```bash
cd ~/lab1_ws
colcon build
source install/setup.bash
python3 src/<your repository folder>/tests/check_lab1.py
```

It starts your nodes, tests them, and prints your score for Parts 1 to 3. Run it as often as you like.

## X. Submitting

1. Commit and push your work. Check on github.com that your latest commit is there.
2. Submit the URL of your repository on the Canvas assignment.

## XI. Grading Rubric

| Part | What is graded | Points |
|------|----------------|--------|
| 1 | The package: `ackermann_msgs` is declared and both executables are registered | 25 |
| 2 | The nodes: `talker` and `relay` behave as described | 25 |
| 3 | The launch file: it is installed and starts both nodes | 25 |
| 4 | Written questions in `SUBMISSION.md` | 25 |

**Total: 100 Points**

Parts 1 to 3 are scored by `tests/check_lab1.py`. Part 4 is graded by hand.
