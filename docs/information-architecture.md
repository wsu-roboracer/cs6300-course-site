# CS 6300 Course Site Information Architecture

## Proposed Navigation

```text
Modules
  Module A: Introduction to ROS 2 and Autonomous Driving Foundations
  Module B: Reactive Methods
  Module C: Mapping and Localization
  Module D: Planning and Control
Build/Repair Manual (external link)
```

## Page Hierarchy

### Module A: Introduction to ROS 2 and Autonomous Driving Foundations

1. Tutorial 1: ROS 2 and Turtlesim
   - Link to RoboRacer's Lecture 1: Introduction to Autonomous Driving
2. Lab 1: Introduction to ROS 2
3. Tutorial 2: Automatic Emergency Braking
   - Link to RoboRacer's Lecture 2: Automatic Emergency Braking
4. Lab 2: Automatic Emergency Braking

### Module B: Reactive Methods

1. Tutorial 3: Wall Following
   - Link to RoboRacer's Lecture 4: Laplace Domain Dynamics and PID
2. Lab 3: Wall Following
3. Tutorial 4: Follow the Gap
   - Link to RoboRacer's Lecture 5: Follow the Gap: Obstacle Avoidance
4. Lab 4: Follow the Gap

### Module C: Mapping and Localization

1. Tutorial 5: SLAM
   - Link to RoboRacer's Lecture 9: Introduction to Graph-based SLAM
2. Tutorial 6: Nav2
3. Lab 5: SLAM and Nav2 Navigation

### Module D: Planning and Control

1. Tutorial 7: Particle Filter Localization
2. Tutorial 8: Pure Pursuit
   - Link to RoboRacer's Lecture 10: Pure Pursuit (Unsure currently about this, check!)
3. Lab 6a: Waypoint Logger for Pure Pursuit
4. Lab 6b: Pure Pursuit

## Student Path

Students follow this course path from their first visit through the final lab:

```text
  -> Module A: Tutorial 1 -> Lab 1 -> Tutorial 2 -> Lab 2
  -> Module B: Tutorial 3 -> Lab 3 -> Tutorial 4 -> Lab 4
  -> Module C: Tutorial 5 -> Tutorial 6 -> Lab 5
  -> Module D: Tutorial 7 -> Tutorial 8 -> Lab 6a -> Lab 6b
```

Each tutorial is placed immediately before the lab that uses it. Any relevant RoborRacer's 
lecture is linked within the matching tutorial section.

## Build/Repair Manual Boundary

The course site links to the Build/Repair Manual for any additional build or repair information.
This is linked to keep the site course focused. Ideally students should not need to utilize the Build/
Repair Manual.

The course site retains only the lab-specific commands and instructions students need
to complete course work on a pre-prepared robot.

## Rationale

This structure allows students to move from top down. It provides students with a predictable
and clear path throughout each module:
1. Learn from the tutorials and consult the related linked lectures as needed
2. Complete the related lab

This removes the confusion of having to scroll and jump between sections of the site to figure out 
the correct path to follow. It keeps all related tutorials and labs in the same module section. The
removal of the "Setup" section and the transition to linked rather than embedded RoboRacer lectures
prevents the need to maintain duplicate information that is copied or forked across sites. The removal
of RoboRacer's modules, races, and final project makes students actual deliverables more clear.

