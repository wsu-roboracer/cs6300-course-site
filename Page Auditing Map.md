

| Source | Current location | Goes to | Notes |
| :---: | :---: | :---: | :---: |
| CS6300 | Learn | Course site | Course site |
| CS6300 | Getting Started/Start Here | Delete | Course orientation |
| CS6300 | Overview/Introduction | Course site | Course context |
| CS6300 | Overview/Syllabus | Delete | Course-specific |
| CS6300 | Setup/VescSetup | Duplicate | Overlaps with Build VESC documentation |
| CS6300 | Setup/LidarSetup | Duplicate | Overlaps with Build LiDAR/driver-stack documentation |
| CS6300 | Setup/RoboRacerDriverStack | Duplicate | Overlaps directly with Build driver-stack documentation |
| CS6300 | Setup/CalibrateOdom | Duplicate | Overlaps with Build odometry calibration |
| CS6300 | Setup/NoMachine | Review | May be useful to both audiences |
| CS6300 | Setup/Install-RealSenseD435i | Review | Determine whether this is general robot setup or course-specific |
| CS6300 | Setup/OpenCV | Review | Determine whether this is a course prerequisite or general setup |
| CS6300 | Setup/RealsenseROS | Review | Determine whether this is general sensor setup or course-specific |
| CS6300 | Setup/Slam | Course site | Course instruction |
| CS6300 | Setup/Nav2 | Course site | Course instruction |
| CS6300 | Modules/ModuleA | Course site | Course module |
| CS6300 | Modules/ModuleB | Course site | Course module |
| CS6300 | Modules/ModuleC | Course site | Course module |
| CS6300 | Modules/ModuleD | Course site | Course module |
| CS6300 | Modules/ModuleE | Course site | Course module |
| CS6300 | Modules/ModuleF | Course site | Course module |
| CS6300 | Modules/ModuleG | Course site | Course module |
| CS6300 | Modules/MaterialDownload | Course site | Course material |
| CS6300 | ModuleA/Tutorial1 | Course site | Course tutorial |
| CS6300 | ModuleA/Tutorial2 | Course site | Course tutorial |
| CS6300 | ModuleB/WallFollowing | Course site | Compare with Build wall-following documentation |
| CS6300 | ModuleB/FollowTheGap | Course site | Compare with Build gap-finding documentation |
| CS6300 | ModuleC/Slam | Course site | Course material |
| CS6300 | ModuleC/Nav2Navigation | Course site | Course material |
| CS6300 | ModuleD/ParticleFilterLocalization | Course site | Course material |
| CS6300 | ModuleD/PurePursuit | Course site | Course material |
| CS6300 | WeberAssignments/Labs | Course site | Course labs |
| CS6300 | Assignments/Labs | Course site | Course labs |
| CS6300 | Assignments/Races | Course site | Course activity/assessment |
| CS6300 | Assignments/FinalProject | Course site | Course assessment |
| CS6300 | Assignments/GradingRubrics | Course site | Course assessment |

| Source | Current location | Goes to | Notes |
| ----- | ----- | ----- | ----- |
| Build | getting\_started/intro | Build manual | Build-manual introduction |
| Build | getting\_started/build\_car | Build manual | RoboRacer construction |
| Build | getting\_started/build\_car/bom | Build manual | Bill of materials |
| Build | getting\_started/build\_car/lower\_level\_chassis | Build manual | Physical construction |
| Build | getting\_started/build\_car/upper\_level\_chassis | Build manual | Physical construction |
| Build | getting\_started/build\_car/autonomy\_elements | Build manual | Hardware/components |
| Build | getting\_started/build\_car/additional\_components | Build manual | Hardware/components |
| Build | getting\_started/build\_car/all\_together | Build manual | Complete build |
| Build | getting\_started/software\_setup | Build manual | General robot software setup |
| Build | getting\_started/software\_setup/software\_host | Build manual | Host-machine setup |
| Build | getting\_started/software\_setup/software\_jetson | Build manual | Jetson setup |
| Build | getting\_started/software\_setup/software\_advance | Build manual | Advanced software configuration |
| Build | getting\_started/software\_setup/optional\_software\_nx | Build manual | Optional Jetson software |
| Build | getting\_started/firmware | Duplicate / Review | Overlaps with CS6300 setup |
| Build | getting\_started/firmware/firmware\_vesc | Duplicate | Overlaps directly with CS6300 VESC setup |
| Build | getting\_started/firmware/drive\_workspace | Duplicate | Overlaps directly with CS6300 driver-stack setup |
| Build | getting\_started/firmware/drive\_workspace\_docker | Build manual | General driver-stack installation |
| Build | getting\_started/driving | Build manual | General robot operation |
| Build | getting\_started/driving/drive\_manual | Build manual | Manual driving |
| Build | getting\_started/driving/drive\_autonomous | Review | Potential course overlap |
| Build | getting\_started/driving/drive\_calib\_odom | Duplicate | Overlaps directly with CS6300 odometry calibration. With extra info |
| Build | going\_forward/intro | Build manual | General documentation |
| Build | going\_forward/algorithms | Review | Educational/algorithmic material may overlap with CS6300 |
| Build | going\_forward/algorithms/wall\_following | Duplicate | Overlaps with CS6300 ModuleB/WallFollowing |
| Build | going\_forward/algorithms/gap\_finding | Duplicate | Overlaps with CS6300 ModuleB/FollowTheGap |
| Build | going\_forward/algorithms/waypoints | Review | Could be relevant to course instruction |
| Build | going\_forward/drive\_rosbag | Review | Technical/reference material |
| Build | going\_forward/simulator | Duplicate / Review | Useful to both audiences |
| Build | going\_forward/simulator/sim\_install | Duplicate / Review | Installation may be shared |
| Build | going\_forward/simulator/sim\_use | Duplicate / Review | Course may use simulator |
| Build | going\_forward/simulator/sim\_info | Duplicate / Review | Technical simulator reference |
| Build | going\_forward/simulation\_archive | Delete / Archive | Archived material; should not automatically migrate |
| Build | autoware/intro | Build manual | General Autoware setup |
| Build | getting\_started/faq | Build manual | General RoboRacer troubleshooting |
| Build | support/contact | Build manual | General project support |
| Build | support/acknowledgment | Build manual | Project information |

| Topic | CS6300 page | Build page | Decision to discuss |
| ----- | ----- | ----- | ----- |
| VESC | Setup/VescSetup | getting\_started/firmware/firmware\_vesc | Decide on canonical technical procedure |
| LiDAR | Setup/LidarSetup | getting\_started/firmware/drive\_workspace | Decide whether CS6300 links to Build documentation |
| Driver stack | Setup/RoboRacerDriverStack | getting\_started/firmware/drive\_workspace | Strong candidate for Build as canonical source |
| Odometry | Setup/CalibrateOdom | getting\_started/driving/drive\_calib\_odom | Strong candidate for Build as canonical source |
| NoMachine | Setup/NoMachine | Build software/Jetson setup | Determine whether course-specific instructions are needed |
| RealSense | Setup/Install-RealSenseD435i | Build software/sensor setup | Determine whether setup is general or course-specific |
| OpenCV | Setup/OpenCV | Build software setup | Determine whether it belongs in general Build setup |
| RealSense ROS | Setup/RealsenseROS | Build software/sensor setup | Determine whether setup is general or course-specific |
| Wall following | ModuleB/WallFollowing | going\_forward/algorithms/wall\_following | Compare content; avoid two independent versions if possible |
| Follow the Gap | ModuleB/FollowTheGap | going\_forward/algorithms/gap\_finding | Compare content; avoid two independent versions if possible |
| Simulator | Course material | going\_forward/simulator | Course site may provide context/link to Build documentation |
| Autoware | Course material, if applicable | autoware/intro | Determine whether CS6300 actually uses this |

