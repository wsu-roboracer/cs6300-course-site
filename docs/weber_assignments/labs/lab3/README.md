# Lab 3: Wall Following

## I. Learning Goals

- PID Controllers
- Driving the car autonomously via Wall Following

## II. Review of PID in the time domain

A PID controller is a way to maintain certain parameters of a system around a specified set point. PID controllers are used in a variety of applications requiring closed-loop control, such as in the VESC speed controller on your car.

The general equation for a PID controller in the time domain, as discussed in lecture, is as follows:

$$ u(t)=K_{p}e(t)+K_{i}\int_{0}^{t}e(t^{\prime})dt^{\prime}+K_{d}\frac{d}{dt}(e(t)) $$

Here, $K_p$, $K_i$, and $K_d$ are constants that determine how much weight each of the three components (proportional, integral, derivative) contribute to the control output $u(t)$. $u(t)$ in our case is the steering angle we want the car to drive at. The error term $e(t)$ is the difference between the set point and the parameter we want to maintain around that set point.

## III. Wall Following

In the context of our car, the desired distance to the wall should be our set point for our controller, which means our error is the difference between the desired and actual distance to the wall. This raises an important question: how do we measure the distance to the wall, and at what point in time? One option would simply be to consider the distance to the left, inner wall at the current time $t$ (let's call it $D_t$). Let's consider a generic orientation of the car with respect to the left, inner wall and suppose the angle between the car's x-axis and the axis in the direction along the wall is denoted by $\alpha$. We will obtain two laser scans (distances) to the wall: one 90 degrees to the left of the car's x-axis (beam b in the figure), and one (beam a) at an angle $\theta$ ( $0<\theta\leq70$ degrees) to the first beam. Suppose these two laser scans return distances a and b, respectively.

![fig1](https://raw.githubusercontent.com/f1tenth/f1tenth_lab3_template/main/img/wall_following_lab_figure_1.png)

*Figure 1: Distance and orientation of the car relative to the wall*

Using the two distances $a$ and $b$ from the laser scan, the angle $\theta$ between the laser scans, and some trigonometry, we can express $\alpha$ as

$$ \alpha=\mbox{tan}^{-1}\left(\frac{a\mbox{cos}(\theta)-b}{a\mbox{sin}(\theta)}\right) $$

We can then express $D_t$ as

$$ D_t=b\mbox{cos}(\alpha) $$

to get the current distance between the car and the left, inner wall. What's our error term $e(t)$, then? It's simply the difference between the desired distance and actual distance! For example, if our desired distance is 0.5 meters from the wall, then $e(t)$ becomes $0.5-D_t$.

However, we have a problem on our hands. Remember that this is a race: your car will be traveling at a high speed and therefore will have a non-instantaneous response to whatever speed and servo control you give to it. If we simply use the current distance to the wall, we might end up turning too late, and the car may crash. Therefore, we must look to the future and project the car ahead by a certain lookahead distance (let's call it $L$). Our new distance $D_{t+1}$ will then be

$$D_{t+1}=D_t+L\mbox{sin}(\alpha)$$

![fig1](https://raw.githubusercontent.com/f1tenth/f1tenth_lab3_template/main/img/wall_following_lab_figure_2.png)

*Figure 2: Finding the future distance from the car to the wall*

We're almost there. Our control algorithm gives us a steering angle for the VESC, but we would also like to slow the car down around corners for safety. We can compute the speed in a step-like fashion based on the steering angle, or equivalently the calculated error, so that as the angle exceeds progressively larger amounts, the speed is cut in discrete increments. For this lab, a good starting point for the speed control algorithm is:

- If the steering angle is between 0 degrees and 10 degrees, the car should drive at 1.5 meters per second (or more).
- If the steering angle is between 10 degrees and 20 degrees, the speed should be 1.0 meters per second.
- Otherwise, the speed should be 0.5 meters per second.

So, in summary, here's what we need to do:

1. Obtain two laser scans (distances) a and b.
2. Use the distances a and b to calculate the angle $\alpha$ between the car's $x$-axis and the left, inner wall.
3. Use $\alpha$ to find the current distance $D_t$ to the car, and then $\alpha$ and $D_t$ to find the estimated future distance $D_{t+1}$ to the wall.
4. Run $D_{t+1}$ through the PID algorithm described above to get a steering angle.
5. Use the steering angle you computed in the previous step to compute a safe driving speed.
6. Publish the steering angle and driving speed to the `/drive` topic in simulation.

## IV. Implementation

Implement wall following to make the car drive autonomously around the CAE hall course. Follow the left, inner wall of CAE hall while driving counter-clockwise. You can implement this node in either C++ or Python.

Test in the [f1tenth_gym_ros](https://github.com/f1tenth/f1tenth_gym_ros/tree/dev-jazzy) simulator on the CAE hall course map by changing the `map_path` in `sim.yaml` to `'maps/levine_blocked'`. This map is the CAE hall loop with its doorways sealed, so the car cannot wander out. Your lab is graded on that same map. Halfway down the west hallway a pair of facing door recesses opens up; to two beams a doorway looks like a corner, so a naive follower steers into it. Think about how your node can tell the two apart (a corner has a wall ahead, a doorway does not). The map comes with a centerline, so the simulator counts your laps (`/ego_racecar/lap_count`, and a "completed lap" line in the bridge log).

Your node must subscribe to `/scan` and publish `AckermannDriveStamped` on `/drive`, and it must work when started with a plain `ros2 run wall_follow <executable>`: it is graded with no parameter file, so bake your tuned gains, desired distance and speeds into the node's defaults.

## V. Getting Started

This lab is done individually.

1. Create your repository with the **Create my lab repository** button on the Canvas assignment, then accept the invitation GitHub sends you.
2. Clone it into the `src` folder of your ROS 2 workspace, then build and source the workspace.

## VI. Deliverables and Submission

**Deliverable 1**: Finish the `wall_follow` package in your repository, then commit and push. Your committed code should start and run in simulation smoothly; this includes building as a package with any dependencies declared in `package.xml`.

Use the names this lab gives you: package `wall_follow` with an executable that starts with `ros2 run wall_follow <executable>` (the skeleton's `wall_follow_node`), subscribing to `/scan` and publishing on `/drive`.

**Deliverable 2**: Make a screen cast of running your wall following node in the simulation: at least one full counter-clockwise lap of the CAE hall course, following the left, inner wall. Upload your video to YouTube (unlisted) or Google Drive — for Drive, set sharing to **"Anyone with the link can view"** or we cannot grade it — and include the link in **`SUBMISSION.md`**.

### Submitting

1. Commit and push your work. Check on github.com that your latest commit is there.
2. Submit the URL of your repository on the Canvas assignment.

## VII. Grading Rubric

| Item | What is graded | Points |
|------|----------------|--------|
| Compilation | The package builds | 10 |
| Implemented PID | In a straight corridor, your node steers the right way when the car is too close to one wall, too close to the other, or turned toward either wall, whichever wall you follow | 40 |
| Tuned PID | One counter-clockwise lap of the CAE hall course, starting on the south hallway heading east, without touching a wall. A run that ends early earns partial credit for the fraction of the loop covered | 40 |
| Video | The link in `SUBMISSION.md`: YouTube unlisted, or Google Drive shared as "Anyone with the link can view" | 10 |

**Total: 100 Points**
