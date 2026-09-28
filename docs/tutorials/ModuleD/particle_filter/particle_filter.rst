.. _doc_tutorials_particle_filter:

Particle Filter Localization
=============================

Where This Fits
----------------

The particle filter is the **localization** component of the autonomous driving pipeline. It answers *"Where am I on this map?"* so that other nodes can make decisions about where to go.

.. image:: img/localization_pipeline.svg
   :alt: Pipeline showing localization (particle filter) feeding into path planning (waypoint logger and path follower)
   :width: 100%
   :align: center

The left side (**Localization**) is what this tutorial covers — taking LiDAR and odometry data, comparing it against a saved map, and producing a localized pose. The right side (**Path Planning & Control**) uses that pose to record waypoints (Lab 6a) and follow them autonomously (Lab 6b).

Why a Standalone Particle Filter?
-----------------------------------

In the Nav2 tutorials you used **AMCL** — Nav2's built-in particle filter — for localization. AMCL is tightly integrated with Nav2's planner, controller, and behavior tree, making it ideal for point-and-click navigation.

This tutorial introduces the **f1tenth/particle_filter**, a standalone localization package. Both AMCL and this particle filter solve the same problem — *"where am I on this map?"* — using the same core algorithm (Monte Carlo Localization). The difference is how they're used:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * -
     - Nav2 AMCL
     - f1tenth/particle_filter
   * - **Integration**
     - Part of the Nav2 stack (lifecycle managed)
     - Standalone node (runs independently)
   * - **TF published**
     - ``map`` → ``odom``
     - ``map`` → ``base_link``
   * - **Use case**
     - Nav2 navigation (planner + controller)
     - Custom controllers (pure pursuit, follow the gap, etc.)
   * - **Ray casting**
     - Standard CPU
     - RangeLibc with GPU acceleration (CUDA on Jetson)

**Why learn both?** Nav2 handles the full navigation pipeline for you — but in robotics and racing, you often need direct control over the car's behavior. A standalone particle filter gives you localized pose data that you can feed into your own algorithms (pure pursuit, MPC, custom raceline followers) without the overhead of Nav2's planner and controller. This is how competitive F1TENTH teams operate: lightweight localization + custom control for maximum speed.

Once you have a saved map, you can use a **particle filter** (Monte Carlo Localization) to localize the vehicle within that map in real time. This tutorial uses the `f1tenth/particle_filter <https://github.com/f1tenth/particle_filter>`_ package with **RangeLibc** for fast ray casting.

.. note::

   **RangeLibc** is a compiled Python library — it is imported automatically by the particle filter node at startup. You do not need to run it separately. As long as it was built correctly (see :ref:`doc_tutorials_slamtoolbox` for the fix script), it will work transparently in the background.

How It Works
------------

The particle filter maintains a set of hypotheses (particles) about where the car might be on the map. Each particle represents a possible pose (x, y, heading). On each LiDAR scan, the filter:

1. **Resamples** — particles with higher weights are duplicated; poor matches are discarded.
2. **Predicts** new particle positions using wheel odometry (with added noise).
3. **Weights** each particle by how well its simulated LiDAR scan matches the real scan.
4. **Normalizes** — adjusts weights so they sum to 1.0 (applies squash factor to prevent particle collapse).

Over time the particles converge on the vehicle's true location.

Publishing
~~~~~~~~~~~

After each MCL cycle completes, the filter computes the **weighted average** of all particles — this becomes the best estimated pose. It then publishes that pose and several visualization outputs so that other nodes and RViz2 can use the result:

- **Localized Pose** (``/pf/pose/odom``) — the primary output. Your pure pursuit node, waypoint logger, or any other node that needs to know where the car is subscribes to this topic.
- **TF Transform** (``map`` → ``laser``) — tells ROS where the car is relative to the map so that LiDAR scans and the map align in RViz2.
- **Particle Cloud** (``/pf/viz/particles``) — all particle hypotheses displayed as arrows in RViz2 for debugging.
- **Best Pose** (``/pf/viz/inferred_pose``) — a single arrow in RViz2 showing the estimated pose.

Publishing happens every cycle (~30-40 Hz), giving downstream nodes a continuous stream of localization data.

.. image:: img/mcl_simple.svg
   :alt: Simplified particle filter cycle: Predict, Weight, Resample, Publish
   :width: 100%
   :align: center

For a deeper look at each step with code examples, see :ref:`doc_tutorials_particle_filter_code`.

Topics
------

.. raw:: html

   <h4 style="color: #2563eb;">Subscribed (Inputs)</h4>

.. raw:: html

   <p><strong style="color: #2563eb;">/scan</strong> — <code>sensor_msgs/LaserScan</code></p>

..

   LiDAR scan data. Downsampled by ``angle_step`` before use in the Weight step.

.. raw:: html

   <p><strong style="color: #2563eb;">/vesc/odom</strong> — <code>nav_msgs/Odometry</code></p>

..

   Wheel odometry from the VESC. Used in the Predict step to move particles.

.. raw:: html

   <p><strong style="color: #2563eb;">/initialpose</strong> — <code>geometry_msgs/PoseWithCovarianceStamped</code></p>

..

   Initial pose set via RViz2's "2D Pose Estimate" button. A one-time action
   that scatters particles around the clicked location.

.. raw:: html

   <p><strong style="color: #2563eb;">/map</strong> — <code>nav_msgs/OccupancyGrid</code></p>

..

   Saved map loaded into RangeLibc at startup for ray casting. Fetched via
   service call from the map server.

Each input feeds a specific step of the MCL cycle:

.. image:: img/mcl_inputs.svg
   :alt: MCL cycle with inputs showing which data feeds each step
   :width: 100%
   :align: center

.. raw:: html

   <h4 style="color: #7c3aed;">Published (Outputs)</h4>

.. raw:: html

   <p><strong style="color: #7c3aed;">/pf/pose/odom</strong> — <code>nav_msgs/Odometry</code> (<strong>Localized Pose</strong>)</p>

..

   The filter's best estimate of where the car is on the map. This is what
   your pure pursuit node or waypoint logger subscribes to. Includes
   position (x, y), heading, speed, and a covariance matrix indicating
   confidence.

.. raw:: html

   <p><strong style="color: #7c3aed;">TF: map → laser</strong> (<strong>TF Transform</strong>)</p>

..

   Tells ROS the car's position on the map by publishing a transform
   directly from ``map`` to ``laser``. This is a shortcut — a standard
   ROS TF tree would go ``map`` → ``odom`` → ``base_link`` → ``laser``,
   but this particle filter skips the intermediate frames. Without this
   transform, the map and LiDAR scans would not align in RViz2.

.. raw:: html

   <p><strong style="color: #7c3aed;">/pf/viz/particles</strong> — <code>geometry_msgs/PoseArray</code> (<strong>Particle Cloud</strong>)</p>

..

   The current set of particle hypotheses, displayed as arrows in RViz2.
   A tight cluster means the filter is confident. A spread-out cloud means
   it is still searching. Useful for diagnosing localization issues.

.. raw:: html

   <p><strong style="color: #7c3aed;">/pf/viz/inferred_pose</strong> — <code>geometry_msgs/PoseStamped</code> (<strong>Best Pose</strong>)</p>

..

   A single arrow in RViz2 showing the weighted average pose. This is the
   same value published on ``/pf/pose/odom`` but as a simpler message type
   for easy visualization.

The full picture — inputs feeding the MCL cycle, and outputs published after each cycle:

.. image:: img/mcl_overview.svg
   :alt: Full MCL diagram with inputs, cycle steps, and published outputs
   :width: 100%
   :align: center

Run Steps
---------

1️⃣ Point to Your Map
~~~~~~~~~~~~~~~~~~~~~~

The particle filter ships with a default map (``lab_map_clean``) already configured. If this is your map, **no action is needed** — skip to Step 2.

.. image:: img/lab_map_clean.png
   :alt: Default lab_map_clean occupancy grid map
   :width: 80%
   :align: center

.. note::

   **Using a different map?** If you need to point the particle filter at a different map, expand the steps below.

   1. Copy your map file into the package's ``maps/`` directory:

      .. code-block:: bash

         cp ~/f1tenth_ws/src/f1tenth_system/f1tenth_stack/maps/my_map.pgm \
            ~/f1tenth_ws/src/f1tenth_system/particle_filter/maps/

   2. Create a YAML metadata file based on the existing template:

      .. code-block:: bash

         cp ~/f1tenth_ws/src/f1tenth_system/particle_filter/maps/lab_map_clean.yaml \
            ~/f1tenth_ws/src/f1tenth_system/particle_filter/maps/my_map.yaml

   3. Edit ``my_map.yaml`` to match your map:

      .. code-block:: yaml

         image: my_map.pgm
         resolution: 0.05
         origin: [-19.8, -36.1, 0]
         negate: 0
         occupied_thresh: 0.65
         free_thresh: 0.25

   4. Update ``localize.yaml`` to use your map name:

      .. code-block:: bash

         code ~/f1tenth_ws/src/f1tenth_system/particle_filter/config/localize.yaml

      Find the ``map_server`` section and change the map name:

      .. code-block:: yaml

         map_server:
           ros__parameters:
             map: 'my_map'

   5. Rebuild the package so the map files are installed to the share directory:

      .. code-block:: bash

         cd ~/f1tenth_ws
         colcon build --packages-select particle_filter
         source install/setup.bash

2️⃣ Bringup (Terminal 1)
~~~~~~~~~~~~~~~~~~~~~~~~~

Start the car stack as usual:

.. code-block:: bash

   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   bringup

3️⃣ Launch the Particle Filter (Terminal 2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ros2 launch particle_filter localize_launch.py

.. note::

   ``localize_launch.py`` handles the map server and lifecycle transitions internally — you do not need to run ``nav2_map_server`` separately.

4️⃣ Open RViz2 (Terminal 3)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd ~/f1tenth_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   rviz2 -d ~/f1tenth_ws/install/particle_filter/share/particle_filter/rviz/pf.rviz

This loads a pre-configured RViz2 layout with the map, particle cloud, and inferred pose displays already set up. No manual configuration needed.

5️⃣ Set the Initial Pose
~~~~~~~~~~~~~~~~~~~~~~~~~

The particle filter starts with particles spread randomly across the map. You must tell it roughly where the car is to begin localization:

- In RViz2, click **2D Pose Estimate** in the toolbar
- Click on the map where the car is located
- Drag in the direction the car is facing, then release

The particles will converge around your selected location.

.. note::

   The more accurately you set the initial pose, the faster the filter will converge. If the particles do not converge, try setting the pose again from a clearer location on the map.

6️⃣ Drive to Localize
~~~~~~~~~~~~~~~~~~~~~~

Drive the car using the PlayStation controller. As the car moves, the particle cloud will tighten and track the vehicle's position on the map. The best estimated pose is published on ``/pf/pose/odom``.

Key Parameters
--------------

Tune the particle filter by editing:

.. code-block:: bash

   code ~/f1tenth_ws/src/f1tenth_system/particle_filter/config/localize.yaml

The key parameters are:

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``max_particles``
     - ``4000``
     - Number of particles — more particles = more accuracy but higher CPU cost
   * - ``angle_step``
     - ``18``
     - LiDAR downsample factor — higher = faster but less accurate
   * - ``range_method``
     - ``rmgpu``
     - Ray casting method (see below)
   * - ``motion_dispersion_theta``
     - ``0.25``
     - Heading noise — increase if filter diverges at speed

``range_method`` Options
~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Method
     - Performance
     - Notes
   * - ``rmgpu``
     - Fastest
     - Requires RangeLibc compiled with CUDA — use on Jetson Orin
   * - ``cddt``
     - Fast
     - CPU only — recommended fallback if no CUDA
   * - ``pcddt``
     - Fast
     - Pruned variant of cddt
   * - ``rm``
     - Moderate
     - CPU only, no precomputation
   * - ``bl``
     - Slowest
     - Brute force — use only for debugging

.. note::

   If you built RangeLibc using the ``fix_range_libc.sh`` script on the Jetson Orin, ``rmgpu`` should work. If you see CUDA errors at runtime, fall back to ``cddt`` by editing ``range_method`` in ``~/f1tenth_ws/src/f1tenth_system/particle_filter/config/localize.yaml`` and setting ``rangelib_variant`` to ``4``.

Troubleshooting
---------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Problem
     - Solution
   * - Particles spread across the whole map
     - Set the initial pose again using 2D Pose Estimate in RViz2
   * - Filter diverges while driving
     - Increase ``motion_dispersion_theta``; slow down; re-set pose
   * - CUDA errors on launch
     - Change ``range_method`` to ``cddt`` and ``rangelib_variant`` to ``4``
   * - ``/map`` not available
     - Ensure map_server is running and the map path is correct
   * - Particles not moving
     - Confirm ``/vesc/odom`` is publishing; check odometry topic name
