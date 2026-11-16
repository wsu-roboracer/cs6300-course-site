# Lab 5 - SLAM Mapping

## I. Learning Goals

- Map an environment using SLAM Toolbox
- Understand occupancy grid maps (`.pgm` / `.yaml`)
- Save a map and verify that it loads

## II. Overview

In this lab you will use the RoboRacer to map the CAE hallway loop, save the map, and verify that the saved map loads correctly. You will use this map for localization in Lab 6a and Lab 6b.

| Part | Task | What You Learn |
|------|------|----------------|
| 1 | Map the hallway with SLAM Toolbox | Occupancy grids, SLAM |
| 2 | Save and verify the map | Map files, the map server, RViz2 |

This lab is done in teams. Your team's repository holds everything you hand in:

```text
maps/             lab_map.pgm and lab_map.yaml go here
images/           your two screenshots go here
SUBMISSION.md     shows the screenshots; check it on github.com before you submit
```

## III. Prerequisites

Before starting this lab, make sure you have:

- Completed the **SLAM tutorial** (you know how to drive, save, and verify a map)

## IV. Getting Started

1. Every member opens the **Create my lab repository** button on the Canvas assignment and chooses your team. The first member creates the team repository and the rest are added to it. Accept the invitation GitHub sends you.
2. Clone it on the car, in your home folder:

   ```bash
   cd ~
   git clone <your repository URL> lab5
   ```

This repository is not a ROS package, so it does not go in your workspace's `src` folder. All of you push to the one repository, so **pull before you push**.

## V. Part 1 — Map the Environment

Use SLAM Toolbox to create a map of the CAE hallway loop.

1. Connect the PlayStation controller and start **bringup** on the car.
2. Launch **SLAM Toolbox** in a second terminal.
3. Open **RViz2** and drive the car through the entire hallway loop using the joystick. Make sure the loop is closed.
4. Take a screenshot of RViz2 showing the completed map while SLAM Toolbox is still running. Save it as `images/slam_running.png` in your repository.

## VI. Part 2 — Save and Verify the Map

1. Save the map:

   ```bash
   mkdir -p ~/f1tenth_ws/src/f1tenth_system/f1tenth_stack/maps
   ros2 run nav2_map_server map_saver_cli -f ~/f1tenth_ws/src/f1tenth_system/f1tenth_stack/maps/lab_map
   ```

2. Verify the files exist (`lab_map.pgm` and `lab_map.yaml`).
3. Stop SLAM Toolbox and bringup.
4. **Verify** the map loads correctly by running the standalone map server and checking it in RViz2.
5. Take a screenshot of RViz2 showing the loaded map. Save it as `images/map_loaded.png` in your repository.
6. Copy the map files into your repository. Keep the originals where they are; Labs 6a and 6b load the map from there.

   ```bash
   cp ~/f1tenth_ws/src/f1tenth_system/f1tenth_stack/maps/lab_map.* ~/lab5/maps/
   ```

> **Tip:** Refer to the Saving the Map tutorial in the course documentation for the full step-by-step walkthrough if needed.

## VII. Submitting

1. Commit and push the map files and both screenshots:

   ```bash
   cd ~/lab5
   git add maps images
   git commit -m "Add map and screenshots"
   git push
   ```

2. Open `SUBMISSION.md` on github.com and check that both screenshots show.
3. Submit the URL of your team's repository on the Canvas assignment. One submission covers the whole team.

## VIII. Deliverables

| # | Deliverable | Points |
|---|-------------|--------|
| 1 | Map files (`lab_map.pgm` and `lab_map.yaml`) committed to `maps/` | 40 |
| 2 | Screenshot of RViz2 showing the completed map with the loop closed, taken while SLAM Toolbox is running | 30 |
| 3 | Screenshot of RViz2 showing the saved map loaded by the standalone map server | 30 |

**Total: 100 Points**
