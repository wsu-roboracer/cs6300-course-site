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

## III. Prerequisites

Before starting this lab, make sure you have:

- Completed the **SLAM tutorial** (you know how to drive, save, and verify a map)

## IV. Part 1 — Map the Environment

Use SLAM Toolbox to create a map of the CAE hallway loop.

1. Connect the PlayStation controller and start **bringup** on the car.
2. Launch **SLAM Toolbox** in a second terminal.
3. Open **RViz2** and drive the car through the entire hallway loop using the joystick. Make sure the loop is closed.
4. Take a screenshot of RViz2 showing the completed map while SLAM Toolbox is still running.

## V. Part 2 — Save and Verify the Map

1. Save the map:

   ```bash
   mkdir -p ~/f1tenth_ws/src/f1tenth_system/f1tenth_stack/maps
   ros2 run nav2_map_server map_saver_cli -f ~/f1tenth_ws/src/f1tenth_system/f1tenth_stack/maps/lab_map
   ```

2. Verify the files exist (`lab_map.pgm` and `lab_map.yaml`).
3. Stop SLAM Toolbox and bringup.
4. **Verify** the map loads correctly by running the standalone map server and checking it in RViz2.
5. Take a screenshot of RViz2 showing the loaded map.

> **Tip:** Refer to the Saving the Map tutorial in the course documentation for the full step-by-step walkthrough if needed.

## VI. Deliverables

| # | Deliverable | Points |
|---|-------------|--------|
| 1 | Map files (`lab_map.pgm` and `lab_map.yaml`) submitted to Canvas | 40 |
| 2 | Screenshot of RViz2 showing the completed map with the loop closed, taken while SLAM Toolbox is running | 30 |
| 3 | Screenshot of RViz2 showing the saved map loaded by the standalone map server | 30 |

**Total: 100 Points**
