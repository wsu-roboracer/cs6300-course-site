---
site_page: tutorials/ModuleA/aeb/index
---

Automatic emergency braking stops the car before it hits something. In this area you read lidar scans, work out the time to collision, and publish a command that brakes the car.

Work through the tutorial before you start Lab 2.

Lab 2 comes in two halves, and you hand in each one separately:

- **Lab 2 Sim** is yours alone, in the simulator. You write the safety node, then record a video of it braking for a wall and driving a clear hallway without braking. A check script in your repository scores the code, so you know where you stand before you submit.
- **Lab 2 Car** is your team's, on a real RoboRacer, in class. You port the node to the car, bench test it with the wheels off the ground, tune it against a real lidar in the CAE hallway, and record your team's demonstration.

Both halves are handed in the same way, and both use one repository: your Lab 2 Sim repository, or the one belonging to whichever team member's node your team runs. You submit its URL with a video link filled into `SUBMISSION.md`.

Get the braking logic right in the simulator, where a crash costs you a reset. The car is where you find out what a real lidar returns that a simulated one never does.
