# Inventory of All Photos and Videos Needed for Labs 1 - 6b

## Lab 1: Introduction to ROS 2

| **Required Visual** | **Place Near** | **Hardware and Lab Access Needed** |
| --- | --- | --- |
| **Screenshot of successfully running Docker container** | **Section 2.2** | **Computer with Docker installed and the course Docker image available** |
| **Replace current text with a screenshot of successful ros2 topic list output** | **Section 3: ROS 2 Basics**<br>**Under “You should see 2 topics listed” replace that text with an actual image** | **Computer with ROS 2 environment** |
| **Screenshot of the running talker/listener nodes and their output** | **Section 5: Creating Nodes with Publishers and Subscribers** | **Computer with ROS 2 environment** |
| **Screenshot of successful output on:**<br>**ros2 topic list**<br>**ros2 topic info drive**<br>**ros2 topic echo drive**<br>**ros2 node list**<br>**ros2 node info talker**<br>**ros2 node info relay** | **Section 7: ROS 2 Commands** | **Computer with ROS 2 environment and completed Lab 1 nodes** |

## Lab 2: Automatic Emergency Braking

| **Required Visual** | **Place Near** | **Hardware and Lab Access Needed** |
| --- | --- | --- |
| **Screenshot of what each Message type looks like:**<br>**LaserScan (specifically ranges)**<br>**Odometry**<br>**AckermannDriveStamped** | **Overview Section**<br>**Under each related message type text description** | **Computer with ROS 2 environment and completed Lab 1 nodes** |
| **Bad Example: Short video/GIF of the robot stopping abruptly** | **Section IV: Automatic Emergency Braking with iTTC**<br>**After the expected braking behavior is explained** | **Prepared RoboRacer, charged battery, LiDAR, AEB node with intentionally poor parameters, obstacle, indoor test space** |
| **Good Example: Short video/GIF of the robot gradually slowing down and stopping in a controlled way** | **Section IV: Automatic Emergency Braking with iTTC**<br>**After the expected braking behavior is explained**<br>**\*! Could also be formatted as a side by side comparison, this is probably best** | **Same robot, obstacle, and test area; correctly tuned AEB node** |
| **\*? Do we need an image of the car reacting to a false positive?** | **Section IV: Automatic Emergency Braking with iTTC**<br>**After the expected braking behavior is explained** | **Same robot, obstacle, and test area; tuned for a false positive** |
| **Screenshot showing incoming /scan data** | **Section IV: Automatic Emergency Braking with iTTC**<br>**After /scan, odometry, and /drive is introduced** | **Powered robot with LiDAR; computer connected to the robot** |

## Lab 3: Wall Following

| **Required Visual** | **Place Near** | **Hardware and Lab Access Needed** |
| --- | --- | --- |
| **Screenshot showing wall measurements in LaserScan data** | **Section III: Wall Following, after steps 1–3** | **Powered robot with LiDAR; RViz** |
| **Bad Example: Short video/GIF of poor PID tuning causing oscillation, drift, or unsafe steering. Maybe show a naive follower steering into the doorway** | **Section III: Wall Following or at Implementation** | **Prepared robot, LiDAR, wall-following route, intentionally poor PID values** |
| **Good Example: Short video/GIF of a correctly tuned robot that follows the wall at a stable distance, correctly recognizing doorways** | **Section III: Wall Following or at Implementation** | **Same robot and route; correctly tuned Wall Following node** |

## Lab 4: Follow the Gap

| **Required Visual** | **Place Near** | **Hardware and Lab Access Needed** |
| --- | --- | --- |
| **RViz screenshot (annotated?) showing LiDAR data and the safety bubble** | **Section III: Review of F1TENTH Follow the Gap**<br>**After step 3 (“Draw a safety bubble”)** | **Robot with LiDAR; computer with RViz; obstacles in scan data** |
| **Image (annotated?) showing the selected gap and goal point** | **Section III: Review of F1TENTH Follow the Gap**<br>**After step 5 (“Find the best goal point”)** | **Recorded or live LiDAR data** |
| **Bad Example: Robot with poor gap selection navigating the hall with difficulty** | **Implementation** | **Prepared robot, obstacle course, incomplete/poor Follow the Gap settings** |
| **Good Example: Robot choosing good gaps and navigating the hall safely through at least 3 corners, bonus if 4 corners + continues**<br>**\*there are 2 maps, do we need videos of both?** | **Implementation** | **Same robot and course; completed Follow the Gap node** |

## Lab 5: SLAM and Nav2 Navigation

| **Required Visual** | **Place Near** | **Hardware and Lab Access Needed** |
| --- | --- | --- |
| **RViz short video/GIF showing the map growing while the robot moves** | **IV. Part 1 - Map the Environment**<br>**After step 3** | **Robot running SLAM; LiDAR; computer with RViz** |
| **Screenshot comparing an incomplete/poor map with a complete usable map** | **IV. Part 1 - Map the Environment**<br>**After the map review or map-saving step** | **Existing map data or recorded mapping sessions** |
| **Screenshot of the saved map files and RViz displaying the loaded map** | **IV. Part 1 - Map the Environment**<br>**After the map loading step** | **Computer with saved map files; Nav2 configured** |
| **\*? Screenshot of workflow for adding the displays** | **V. Part 2 - 2D Goal Pose Navigation**<br>**All of step 4** | **Close any running SLAM, map server, or RViz2 processes from Part 1. Start fresh** |
| **RViz screenshot showing the 2D Pose Estimate tool and particle cloud** | **V. Part 2 - 2D Goal Pose Navigation**<br>**After step 5** | **Robot running localization; saved map; RViz** |
| **Short video/GIF showing a goal selected in RViz and the robot reaching it** | **V. Part 2 - 2D Goal Pose Navigation**<br>**After step 7** | **Robot running Nav2; mapped test area; RViz** |
| **\*? Screenshot of workflow for adding the panel** | **VI. Part 3 - Waypoint Navigation**<br>**All steps** | **Computer with ROS 2, RViz2, Nav2, and the nav2_rviz_plugins package running.** |
| **Show what getting the waypoint coordinates for your map looks like** | **VII. Part 4 - Programmatic Waypoint Navigation**<br>**After step 5** | **Computer with ROS 2, RViz2, and Nav2 running.** |
| **Short video/GIF of robot navigating through the set waypoints**<br>**\*? Could include bad example as well as needed** | **VII. Part 4 - Programmatic Waypoint Navigation**<br>**After step 7** | **Prepared robot, saved map, LiDAR, controller, computer with ROS 2/RViz2/Nav2, and the completed waypoint_nav node.** |

## Lab 6a: Waypoint Logger for Pure Pursuit

| **Required Visual** | **Place Near** | **Hardware and Lab Access Needed** |
| --- | --- | --- |
| **Screenshot showing waypoint-recording confirmation output** | **V. Part 2 - Write the Waypoint Logger Node**<br>**After step 5** | **Computer with waypoint logger running** |
| **Show the expected yellow dots and orange path line building in RViz2 as you drive** | **V. Part 2 - Write the Waypoint Logger Node**<br>**After the text describing the expected dots and line** | **Robot publishing odometry; waypoint logger; RViz** |
| **Could repeat above image as needed**<br>**RViz screenshot/GIF showing the expected yellow dots and orange path line building in RViz2 as you drive** | **VI. Part 3 - Record a Lap**<br>**After step 4** | **Robot publishing odometry; waypoint logger; RViz** |
| **Short video/GIF showing the robot completing a steady lap while recording**<br>**\*! Could include bad example as needed, but was unsure for this lab** | **VI. Part 3 - Record a Lap**<br>**After step 5** | **Prepared robot, controller, repeatable track, localized particle filter** |
| **Screenshot of the saved CSV and a small sample of waypoint coordinates** | **VII. Part 4 - Verify the Recording** | **Computer with saved waypoint file** |

## Lab 6b: Pure Pursuit

| **Required Visual** | **Place Near** | **Hardware and Lab Access Needed** |
| --- | --- | --- |
| **Screenshot of pure_pursuit.yaml showing lookahead_distance, speed, and waypoint_file** | **IV. Part 1 - Config File and Launch File**<br>**After Create the Config File** | **Computer with Lab 6a waypoints.csv output and the pure_pursuit package** |
| **Screenshot of pure_pursuit_launch.py showing the YAML configuration passed to the Pure Pursuit node** | **IV. Part 1 - Config File and Launch File**<br>**After Create the Launch File** | **Computer with the pure_pursuit package and its launch/config files** |
| **RViz screenshot showing the recorded path and the live lookahead target** | **VI. Part 3 - Test on the Robot**<br>**After step 3** | **Prepared robot, particle filter running, Lab 6a waypoint file, computer with RViz** |
| **RViz screenshot showing the green sphere/lookahead target moving ahead of the robot on the recorded path** | **VI. Part 3 - Test on the Robot**<br>**After step 5/6** | **Same robot, path, and track; correctly tuned Pure Pursuit configuration** |
| **Bad Example: Short video/GIF showing the robot not tracking well** | **VI. Part 3 - Test on the Robot**<br>**After tuning** | **Same robot, path, and track; poorly tuned Pure Pursuit configuration** |
| **Good Example: Short video/GIF showing the robot smoothly following the recorded route** | **VI. Part 3 - Test on the Robot**<br>**After tuning** | **Same robot, path, and track; correctly tuned Pure Pursuit configuration** |
