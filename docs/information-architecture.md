# CS 6300 Course Site Information Architecture

## Purpose

The CS 6300 course site serves students completing the RoboRacer course and labs.
It should organize learning material in the order students use it: a tutorial introduces
a topic, the linked lecture provides supporting concepts, and the following lab applies
the topic.

Robot assembly, repair, hardware configuration, and troubleshooting belong in the
separate Robot Build/Repair Manual. The course site links to that manual rather than
copying its content.

## Proposed Navigation

```text
Start Here
Modules
  Module A: Introduction to ROS 2 and Autonomous Driving Foundations
  Module B: Reactive Methods
  Module C: Mapping and Localization
  Module D: Planning and Control
Build/Repair Manual (external link)
Course Resources
  Syllabus
  Grading
  Contact
```

`Start Here` is the student's first page. It explains the course sequence, identifies
the required software and prepared-robot prerequisites, and links to the Build/Repair
Manual when a student needs build, repair, or hardware setup information.

The Build/Repair Manual is a top-level external link. Each course page that requires
robot hardware or configuration includes a concise link to the relevant manual page
instead of duplicating build instructions.

## Module Hierarchy

### Module A: Introduction to ROS 2 and Autonomous Driving Foundations

1. Tutorial 1: ROS 2 and Turtlesim
   - Link to Lecture 1: Introduction to Autonomous Driving
2. Lab 1: Introduction to ROS 2
3. Tutorial 2: Automatic Emergency Braking
   - Link to Lecture 2: Automatic Emergency Braking
4. Lab 2: Automatic Emergency Braking

### Module B: Reactive Methods

1. Tutorial 3: Wall Following
   - Link to Lecture 4: Laplace Domain Dynamics and PID
2. Lab 3: Wall Following
3. Tutorial 4: Follow the Gap
   - Link to Lecture 5: Follow the Gap: Obstacle Avoidance
4. Lab 4: Follow the Gap

### Module C: Mapping and Localization

1. Tutorial 5: SLAM
   - Link to Lecture 9: Introduction to Graph-based SLAM
2. Tutorial 6: Nav2
3. Lab 5: SLAM and Nav2 Navigation

### Module D: Planning and Control

1. Tutorial 7: Particle Filter Localization
2. Tutorial 8: Pure Pursuit
   - Link to Lecture 10: Pure Pursuit
3. Lab 6a: Waypoint Logger for Pure Pursuit
4. Lab 6b: Pure Pursuit

## Student Path

Students follow this course path from their first visit through the final listed lab:

```text
Start Here
  -> Module A: Tutorial 1 -> Lab 1 -> Tutorial 2 -> Lab 2
  -> Module B: Tutorial 3 -> Lab 3 -> Tutorial 4 -> Lab 4
  -> Module C: Tutorial 5 -> Tutorial 6 -> Lab 5
  -> Module D: Tutorial 7 -> Tutorial 8 -> Lab 6a -> Lab 6b
```

Each tutorial is placed immediately before the lab that uses it. The linked lecture is
supporting material, not an additional navigation path: students can open it from the
tutorial when they need the underlying concepts.

## Build/Repair Manual Boundary

The course site links to the Build/Repair Manual for:

- Mechanical assembly and replacement procedures
- Electrical wiring, batteries, power, and motor-controller hardware
- Sensor installation and hardware diagnostics
- Robot image installation, robot-wide configuration, and repair procedures
- Hardware and network troubleshooting

The course site retains only the lab-specific commands and instructions students need
to complete course work on a prepared robot.

## Rationale

This structure gives students one predictable pattern in every module: learn through a
tutorial, consult the related lecture as needed, then complete the lab. It removes the
current ambiguity between course material and robot-maintenance material, keeps labs
focused on deliverables, and prevents two sites from maintaining duplicate build
instructions. It also makes instructor-authored tutorials the canonical course content;
supplemental RoboRacer material can be linked from the relevant tutorial rather than
copied or maintained as a fork.
