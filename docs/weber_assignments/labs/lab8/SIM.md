# Lab 8 Sim - Motion Planning

> Adapted from the RoboRacer (F1TENTH) Lab 6: Motion Planning, MIT License. See `LICENSE`.

## I. Learning Goals

- Motion Planning basic concepts
  * Configuration space vs. Workspace: you should understand the difference between configuration space and workspace, and the advantages and disadvantages of planning in each of them.
  * Free space vs. Obstacle space: you should understand the difference between free space and obstacle space.
  * Occupancy grids and Costmaps: you should understand what occupancy grids and costmaps are, how to use them, and how to create them.
- Motion Planning algorithms
  * Sampling based algorithms: RRT and its variants.
  * Why sample: how grid search (BFS, Dijkstra, A*) scales with the dimension of the state space, and why a sampling planner does not.
  * Probabilistic completeness vs. asymptotic optimality: what RRT guarantees, and what rewiring buys you in RRT*.

## II. Overview

The goal of this lab is to provide you with tools that will help you in a head-to-head race on a race track. After finishing this lab, your car should be able to do something like [this](https://www.youtube.com/watch?v=llHCRqwIllM).

Before you start this lab, work through **[An Introduction to Sampling-Based Motion Planning with RRT*](https://roboracer.ai/learn/rrt/)**, the RoboRacer interactive tutorial written for this lab. It is about 20 minutes plus a quiz, and its figures run live: you drag the start and the goal and paint walls while [BFS, Dijkstra, A* and greedy search](https://roboracer.ai/learn/rrt/#grid) expand side by side; you grow [an RRT](https://roboracer.ai/learn/rrt/#rrt) while changing the step size and the goal bias and toggling the Voronoi regions; you watch [RRT*](https://roboracer.ai/learn/rrt/#rrtstar) pick the cheapest parent and rewire its neighbors, and run RRT against RRT* on the same samples with a cost-convergence chart. Its [cheat sheet](https://roboracer.ai/learn/rrt/#sheet) is the page to keep open while you code, and its [quiz](https://roboracer.ai/learn/rrt/#quiz) is a good check that you understood the parts this lab grades.

Then read the [paper](https://arxiv.org/pdf/1105.1186.pdf). Pay close attention to sections 3.1, 3.2, Algorithm 3, 3.3, Algorithm 6.

### Why Sample Instead of Searching a Grid?

Grid search needs a cell for every combination of state variables, so the number of cells explodes as you add dimensions: fine for x and y, hopeless once heading, velocity and steering angle join them. A sampling planner drops points into the continuous space instead, so its cost scales with the number of samples you draw rather than with the resolution of every axis. That is why we plan with RRT here instead of running A* over a fine grid.

The grid-search part of the tutorial is still worth your time: the occupancy grid you build below is the same data structure those algorithms walk, and A* is still the right tool once the state space is small enough.

| Algorithm | Expands with | Complete | Optimal | Use it for |
| --- | --- | --- | --- | --- |
| BFS | FIFO queue | yes | only if every step costs the same | unweighted grids |
| Dijkstra | min-heap on `g` | yes | if every cost is non-negative | weighted grids, distances everywhere |
| A* | min-heap on `g + h` | yes | if `h` never overestimates | one goal, with a good distance estimate |
| Greedy | min-heap on `h` | yes, on a finite grid | no | quick, rough answers |
| RRT | random tree | probabilistically | no | a first path in a continuous space |
| RRT* | random tree, rewired | probabilistically | asymptotically | improving that path as samples accumulate |
| RRT-Connect | two trees meeting | probabilistically | no | the fastest first path |
| Informed RRT* | RRT*, sampling inside an ellipse | probabilistically | asymptotically | faster convergence once a path exists |
| Car-like RRT | drivable arcs | not with fixed arcs | no | paths the car can actually follow |

The bottom three rows are your menu for the extra credit in Part C.

### RRT Pseudocode

![rrt_algo](imgs/rrt_algo.png)

The pseudocode of the basic version of RRT is listed as above. Every iteration is five steps:

1. **Sample** a random point `x_rand` in the free space.
2. **Nearest**: find the tree node `x_nearest` closest to it.
3. **Steer** from `x_nearest` toward `x_rand` by the step size $\eta$ to get `x_new`.
4. **Collision check** the edge from `x_nearest` to `x_new`.
5. **Add** `x_new` to the tree if that edge is free.

Step 2 is what sets the complexity: O(n log n) in the number of nodes with a k-d tree, O(n^2) with a linear scan over the tree. RRT is *probabilistically complete* - draw enough samples and it finds a path if one exists - but it is **not** optimal, and the paths it returns are jagged, so they need smoothing before you drive them. Its tree grows fastest at the nodes with the largest Voronoi regions, which is exactly what pushes it out into unexplored space.

You can find all the details of the functions used by RRT in the paper. If you're implementing RRT*, or another version of RRT, read the RRT* section of the provided paper, and do some research to figure out how to modify the basic version of RRT.

### F1TENTH RRT vs. Generic RRT

In general, RRT is often used as a global planner where the tree is kept throughout the time steps. Whenever there is a new obstacle, and the occupancy grid changes, the tree will change accordingly. In our case, RRT is used as a local planner for obstacle avoidance. This is due to the fact that we don't have a well-defined starting point and goal point when we're racing on a track and we want to run continuous laps. In our implementation, we are only keeping a tree for the current time step in an area around the car. You could try to keep one tree that populates the map throughout the time steps, but speed is going to be an issue if you don't optimize how you're finding nodes, and traversing the tree.

For more details, you can check the slides from class for more details on the local planning scheme.

## III. Coding assignment

You can choose to implement RRT in either the workspace or configuration space. Since we're working with a car-like robot, the workspace will be the car's position in the world, and the configuration space will be whatever you decided to add on top of that (heading angle, velocity, etc.).

### Implementing an Occupancy Grid

You'll need to implement an occupancy grid for collision checking. Think about what is available to you (the map, the Laserscan messages, etc.), and construct a occupancy grid using those information. You can choose to either implement a binary occupancy grid (a grid cell is either 0 for unoccupied, or 1 for occupied), or use a probabilistic occupancy grid (a grid cell has values between 0 and 1 for probability that it is occupied). You could choose to implement either an occupancy grid in the car's local frame (our recommendation), or in the map's global frame. Depending on the size of the map that you use, think about how to compute updates to the occupancy grid and storing/using the occupancy grid efficiently. Since we're using RRT as a local planner, as in it comes up with a new path at every time step, you need to run everything relatively fast.  You'll also want to visualize the occupancy grid to ensure its correctness. You don't have to implement a multi-layer one like the one shown in the Figure.

![grid](imgs/grid.png)


Figure 2

### Working in the simulator and on the car

By this point, you should be pretty comfortable using the simulator to test your code. The ground truth pose of the car is available in the simulator, this would be useful for testing your algorithm in the simulator. When you test on the car, make sure you start slow, and increase your speed gradually. You'll see the effectiveness of your algorithm at a higher speed.

### Trajectory Execution

After you've found a path to your goal with RRT, there are different algorithms that you could use to follow that trajectory. The most obvious solution is the Pure Pursuit you wrote in Lab 7. Picking the waypoint out of the path for pure pursuit will be the most important part if you decided to go down this route. You want a balance between having the car steering smoothly, and at the same time, reactive enough to avoid obstacles. Also, up-sampling the path for pure pursuit to pick out a waypoint is a good way to go.

### Hints

Think about how you could change the way that you're sampling the free space to speed up the process of finding a path to the goal. Also think about how the restrict the area in which you're sampling to make sure you don't have too big of a tree. Besides RRT*, there are other versions of RRT that takes into consideration of other variables (the dynamics of the car for example). After you're done with the basic version of RRT, you should do some research and implement a better version of RRT.

Make sure you visualize the tree you've expanded, and the path you've chosen as the trajectory.

Concrete numbers to start from, from the tutorial's [cheat sheet](https://roboracer.ai/learn/rrt/#sheet):

- **Inflate the obstacles** in the occupancy grid by half the car's width plus a margin. Then a collision-free edge really is drivable, and your planner stops returning paths that clip a doorway with the car's corner.
- **Collision-check the edge, not just its endpoint.** Walk each edge in steps of half a grid cell - on a 5 cm grid, 2.5 cm - and test every cell you land in. Checking only `x_new` lets an edge jump straight through a thin wall.
- **Bias the sampling toward the goal.** Sample the goal itself 5 to 10% of the time instead of a random point; it pulls the tree toward the goal and cuts the number of samples you need.
- **Pick the step size $\eta$ with the gaps in mind.** Long steps cover ground quickly but fail more collision checks near walls; short steps thread narrow gaps but need many more nodes.
- **Smooth the path before you drive it.** Shortcut smoothing takes two waypoints on the path and, if the straight line between them is collision-free, drops everything in between. It turns RRT's zig-zag into something pure pursuit can actually track.
- **Mind the budget.** The tree is rebuilt on every scan, so a plan gets a few tens of milliseconds, not seconds: sampling, nearest-neighbor queries, collision checks and publishing all have to fit inside that.


## IV. Part C: RRT* (Extra credit)

![rrt](imgs/rrt.png)

Figure 3

You'll be rewarded extra credit (10%) for implementing RRT*, or another modified version of RRT (if you do, make a good argument on why it deserves extra credit). On top of the basic version of RRT, RRT* uses a cost function, and rewiring the tree, to find a better path to the goal. When the tree has expanded infinite number of nodes, RRT*'s solution is close to optimal. Figure 3 shows the difference in the tree expanded and path found between RRT and RRT*. The skeleton code provided has sections for functions in RRT* as well.

RRT* keeps the five steps above and adds three, between the collision check and the next sample:

6. **Near set**: collect the tree nodes within a radius $r$ of `x_new`.
7. **Choose the cheapest parent** out of that set - the node that minimizes the cost to reach `x_new`, which is not always the nearest one.
8. **Rewire**: for every node in the near set, if reaching it through `x_new` is cheaper than its current path, make `x_new` its parent instead.

The radius shrinks as the tree grows:

$$ r = \min\left(\gamma\left(\frac{\log n}{n}\right)^{1/d}, r_{max}\right) $$

where $n$ is the number of nodes and $d$ the dimension of the space, so each round still only looks at roughly $\log n$ neighbors and RRT* stays O(n log n) - more work per node than RRT, but the same order. Step 8 is where RRT* implementations usually break: a rewire changes the cost of every node in the rewired neighbor's subtree, and forgetting to propagate that leaves stale costs that quietly spoil every parent choice afterwards. A few hundred RRT* nodes are already enough to give visibly straighter paths than RRT, so you do not need a huge tree to show the difference in your video.

## V. How Your Planner Is Graded

The course staff grade your planner in the simulator on **`levine_obs`**, the simulator's Levine map with obstacles (the one from lab 4), counter-clockwise like every Levine run. Pick it on your laptop with `map_path: 'maps/levine_obs'` in `config/sim.yaml`, and set the start pose of the run you want to try:

| Graded run | `sx`, `sy`, `stheta` | What ends it |
| --- | --- | --- |
| Straight path | `8.08`, `8.67`, `3.1416` (the north hallway just out of the north-east corner, heading west) | 16 m along the hallway, under both triangles, 1.4 m before the L-shaped wall |
| Turn | `9.96`, `2.8`, `1.5708` (the east hallway, heading north: lab 4's start) | 3 m after the north-east corner, before the first triangle |
| Full lap | `9.96`, `2.8`, `1.5708` (the turn's start) | one whole lap past every obstacle: the triangles, the L-shaped wall (the way through is above its bar; below it is a dead end), the boxes of the south hallway, the ellipse and the box at the south-east corner |

The full lap is run first, and the turn and the straight path are stretches of it: when your lap gets past the end of one of them without touching anything, that run gets its full points and its time from the lap, and is not run again. Only a stretch your lap does not get past is run on its own, from the start pose in the table.

A run also ends at the first touch of a wall or an obstacle, or after 12 s without progress (the lap also after 180 s); a run that ends early earns partial credit for the fraction of its stretch, or of the lap, covered.

**One launch file.** The course staff start your code with `lab8_pkg/launch/levine_launch.py`, and nothing else, for every run:

```bash
ros2 launch lab8_pkg levine_launch.py
```

It is yours to edit: set `EXECUTABLE` to the node you wrote (`rrt_node.py` for Python, `rrt_node` for C++), put your tuned values in `PARAMETERS` (or give it a `.yaml` file), and start as many nodes as you like, in either language. Start your own nodes only: the simulator is already running. Without the launch file the staff fall back to `ros2 run lab8_pkg <executable>` with no parameter file, so tuned values must then be your node's defaults.

**Ship your waypoints with your package.** RRT plans locally towards a goal taken from a global path: put your CSV files in `lab8_pkg/waypoints/`; the skeleton's `CMakeLists.txt` installs that folder, and your node finds it with `get_package_share_directory('lab8_pkg')` (Python, `ament_index_python.packages`) or `ament_index_cpp::get_package_share_directory("lab8_pkg")` (C++). A path like `/home/you/sim_ws/...` only exists on your laptop: on the grading machine your node would die at start-up.


## VI. Deliverables and Submission

**This lab is done in teams.** Your team shares one repository.

1. Every member opens the **Create my lab repository** button on the Canvas assignment and chooses your team. The first member creates the team repository and the rest are added to it. Accept the invitation GitHub sends you.
2. Clone it into the `src` folder of your ROS 2 workspace (in the simulator, and on the car), then build and source the workspace.

All of you push to that one repository, so **pull before you push**. One submission is the whole team's submission, and every member gets the same grade.

- **Deliverable 1**: Commit your `lab8_pkg` package to your team's repository, waypoints included. Your committed code should run smoothly in simulation on `levine_obs`: a full counter-clockwise lap past every obstacle, without touching a wall or an obstacle (the straight path under both triangles and the north-east corner are also graded on their own).
- **Deliverable 2**: Submit links to two videos in **`SUBMISSION.md`** (YouTube, unlisted): your RRT running in the simulator with the tree and the chosen path visualized in RViz, and the real car running RRT in the CAE hallway.

### Submitting

1. Commit and push your work, waypoints included. Check on github.com that your latest commit is there.
2. Submit the URL of your team's repository on the Canvas assignment.

**The course staff find your work by name.** Package `lab8_pkg`, launch file `levine_launch.py` (or, without it, an executable it can start with `ros2 run lab8_pkg <executable>`, the skeleton's `rrt_node`), taking its pose from `/ego_racecar/odom`, reading `/scan` and publishing `AckermannDriveStamped` on `/drive`. Otherwise, your work cannot be run for grading and your submission may get the wrong grade.

**Only the topics the lab needs.** Your nodes may read the simulator's localization (`/ego_racecar/odom`, `/tf`), `/scan` and `/initialpose`, and publish on `/drive`, `/tf` and topics only your own nodes use (path and waypoint markers). The course staff check the ROS graph while your code runs: a node that reads the lap counter or the collision flag, or publishes on a topic the simulator listens to (`/initialpose`, which teleports the car, `/ego_racecar/odom`, the lap counter, ...) scores 0 on every run.

## VII. Grading Rubric
- Compilation: **30** Points (the package builds)
- Performance on straight path: **20** Points (graded in simulation: the north hallway of `levine_obs` under both triangles, without touching anything; full points when your full lap gets past it cleanly, otherwise a run of its own where ending early earns partial credit for the fraction covered)
- Performance on turn: **20** Points (graded in simulation, the same way: the north-east corner of `levine_obs`)
- Full lap of the obstacle map: **10** Points (graded in simulation, the same way: one counter-clockwise lap of `levine_obs` past every obstacle)
- Demonstration video: **20** Points (unlisted YouTube, submitted in the Canvas text box: your RRT running in the simulator with the tree and the chosen path visualized in RViz)

**Total: 100 Points**

**Extra credit:** RRT* or another improved RRT, worth up to ten further points, graded
from the code and the video.

The car is graded in Lab 8 Car, not here.

## VIII. Extra Resources

- [An Introduction to Sampling-Based Motion Planning with RRT*](https://roboracer.ai/learn/rrt/) - the interactive RoboRacer tutorial for this lab: grid search, why sampling scales, RRT, RRT*, the variants, a [cheat sheet](https://roboracer.ai/learn/rrt/#sheet), and a [quiz](https://roboracer.ai/learn/rrt/#quiz) of 42 questions across five topics (ten of them ask you to click on a picture).
- Karaman and Frazzoli, [Sampling-based algorithms for optimal motion planning](https://arxiv.org/abs/1105.1186) (2011) - the RRT* paper. Sections 3.1-3.3 and Algorithms 3 and 6 are the ones this lab asks for.
- LaValle, [Rapidly-exploring random trees: a new tool for path planning](http://msl.cs.illinois.edu/~lavalle/papers/Lav98c.pdf) (1998) - the original RRT.
- Kuffner and LaValle, [RRT-Connect: an efficient approach to single-query path planning](https://www.cs.cmu.edu/afs/cs/academic/class/15494-s14/readings/kuffner_icra2000.pdf) (2000) - two trees growing toward each other.
- Gammell, Srinivasa and Barfoot, [Informed RRT*](https://arxiv.org/abs/1404.2334) (2014) - once a path exists, sample only inside the ellipse that could still improve it.
- Kunz and Stilman, [Kinodynamic RRTs with fixed time step and best-input extension are not probabilistically complete](https://doi.org/10.1007/978-3-319-16595-0_14) (2014) - read this before you build a car-like RRT out of fixed-length arcs.
- Hart, Nilsson and Raphael, [A formal basis for the heuristic determination of minimum cost paths](https://doi.org/10.1109/TSSC.1968.300136) (1968) - A*.
- Becker, [RRT, RRT* & Random Trees](https://www.youtube.com/watch?v=Ob3BIJkQJEw) - a short video walkthrough.
