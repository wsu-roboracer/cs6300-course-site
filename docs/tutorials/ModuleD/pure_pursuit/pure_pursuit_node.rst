.. _doc_tutorials_pure_pursuit_node:

Running Pure Pursuit
=====================

Where This Fits
----------------

Pure Pursuit is a **Path Follower** — it takes the recorded waypoints and the real-time localized pose from the particle filter, and steers the car along the path. In the future, other algorithms like RRT will also fill this role.

.. image:: ../particle_filter/img/localization_pipeline.svg
   :alt: Pipeline showing localization feeding into path planning — path follower highlighted
   :width: 100%
   :align: center

Once waypoints are recorded, the pure pursuit node can drive the car autonomously around the track using the particle filter for localization.

How It Works
------------

Pure Pursuit is a geometric path tracking algorithm. On each update:

1. The node reads the car's current pose from ``/pf/pose/odom``
2. It finds the **lookahead point** — a point on the path a fixed distance ahead of the car
3. It computes the steering angle to arc toward that lookahead point
4. It publishes drive commands on ``/drive``

The lookahead distance controls the trade-off between tracking accuracy and smoothness. A shorter lookahead follows the path more tightly; a longer lookahead produces smoother but wider turns.

.. note::

   The ``pure_pursuit`` package, launch file, config file, and ``pure_pursuit_node`` do not come pre-installed. You must build them yourself first --- see **Lab 6b - Pure Pursuit** in the Weber Assignments for step-by-step instructions on creating the launch file, config, and writing the node.

Prerequisites
-------------

- Pure Pursuit node built (see :ref:`doc_tutorials_building_pure_pursuit_node`)
- Waypoints recorded (see :ref:`doc_tutorials_waypoint_recording`)
- ``bringup`` running (Terminal 1)
- ``ros2 launch particle_filter localize_launch.py`` running (Terminal 2)
- ``waypoint_viz`` running to visualize the path and lookahead target (Terminal 3):

  .. code-block:: bash

     cd ~/f1tenth_ws
     source /opt/ros/humble/setup.bash
     source install/setup.bash
     ros2 run waypoint_viz waypoint_viz_node --ros-args \
       -p waypoint_file:=~/f1tenth_ws/src/pure_pursuit/maps/waypoints.csv

- RViz2 running with the particle filter config (Terminal 4):

  .. code-block:: bash

     rviz2 -d ~/f1tenth_ws/install/particle_filter/share/particle_filter/rviz/pf.rviz

- Initial pose set via **2D Pose Estimate**

Steps
-----

1️⃣ Launch Pure Pursuit (Terminal 5)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ros2 launch pure_pursuit pure_pursuit_launch.py

The car will begin following the recorded waypoints and loop the track continuously.

2️⃣ Watch the Lookahead in RViz2
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``pf.rviz`` layout already shows the waypoint path and lookahead displays. Once a **2D Pose Estimate** is set, a green sphere in RViz2 (``/waypoint_viz/lookahead``) shows exactly which waypoint pure pursuit is currently targeting — it moves along the orange path in real time as the car drives. This is the key debugging tool: if the lookahead dot behaves unexpectedly (jumps, stays still, or points backward), the problem is in the waypoint search logic, not the steering calculation.

Key Parameters
--------------

Tune pure pursuit performance by editing the config file:

.. code-block:: bash

   nano ~/f1tenth_ws/src/pure_pursuit/config/pure_pursuit.yaml

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Parameter
     - Default
     - Description
   * - ``lookahead_distance``
     - ``1.5``
     - Distance ahead on the path to steer toward (meters) — increase for smoother driving at speed
   * - ``speed``
     - ``1.0``
     - Forward drive speed (m/s)
   * - ``waypoint_file``
     - ``waypoints.csv``
     - Path to the recorded waypoints CSV

Troubleshooting
---------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Problem
     - Solution
   * - Car immediately stops or spins
     - Initial pose not set — set 2D Pose Estimate in RViz2 and re-launch
   * - Car cuts corners aggressively
     - Decrease ``lookahead_distance``
   * - Car oscillates side to side
     - Increase ``lookahead_distance``; reduce speed
   * - Car drifts off path over time
     - Particle filter may have diverged — re-set initial pose in RViz2
   * - No waypoints file found
     - Re-run waypoint recording; confirm path in ``pure_pursuit.yaml``


Additional Resources
--------------------

- `RoboRacer Lecture 10: Pure Pursuit <https://f1tenth-coursekit.readthedocs.io/en/latest/lectures/ModuleD/lecture10.html>`_
