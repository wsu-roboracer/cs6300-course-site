.. _doc_tutorials_wall_follow_package:

Create Wall Following Package
==============================

To set up your wall following package within the driver stack container follow these steps:

1️⃣ Create the Wall Follow Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inside the driver stack container, navigate to your ROS 2 workspace ``~/f1tenth_ws/src`` and create a new package:

.. code-block:: bash

   cd ~/f1tenth_ws/src
   ros2 pkg create wall_follow_package --build-type ament_python --dependencies rclpy sensor_msgs std_msgs

.. note::

   **Dependencies**

   - ``rclpy`` (ROS Client Library for Python)
   - ``sensor_msgs`` (Standard Messages for Sensors)

2️⃣ Modify package.xml
~~~~~~~~~~~~~~~~~~~~~~

Ensure ``package.xml`` includes dependencies like ``rclpy``, ``sensor_msgs``, and ``std_msgs``. Open ``package.xml`` and add:

.. code-block:: xml

   <depend>rclpy</depend>
   <depend>sensor_msgs</depend>
   <depend>std_msgs</depend>

If you're using C++ instead of Python, also ensure you have:

.. code-block:: xml

   <depend>rclcpp</depend>
   <depend>tf2_ros</depend>
   <depend>geometry_msgs</depend>

3️⃣ Modify CMakeLists.txt (If Using C++)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're using C++, modify ``CMakeLists.txt`` to include:

.. code-block:: cmake

   find_package(rclcpp REQUIRED)
   find_package(sensor_msgs REQUIRED)
   find_package(std_msgs REQUIRED)

Ensure the ``add_executable`` or ``ament_target_dependencies`` includes the necessary dependencies.

4️⃣ Install Dependencies Using rosdep
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the following to install missing dependencies:

.. code-block:: bash

   cd ~/f1tenth_ws
   rosdep install --from-paths src --ignore-src -r -y

5️⃣ Implement the Wall Follow Node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You'll create a wall follow node that listens to LiDAR data (``/scan``) and publishes steering commands to stay near a wall.

**Example: Python Wall Follow Node (wall_follow_node.py)**

Create a file inside ``wall_follow_package/wall_follow_node.py``:

.. raw:: html

    <iframe frameborder="0" scrolling="no" style="width:100%; height:2346px;" allow="clipboard-write" src="https://emgithub.com/iframe.html?target=https%3A%2F%2Fgithub.com%2FWeber-AGV%2Ff1tenth_lab3_template%2Fblob%2Fmain%2Fwall_follow%2Fscripts%2Fwall_follow_node.py&style=default&type=code&showBorder=on&showLineNumbers=on&showFileMeta=on&showFullPath=on&showCopy=on"></iframe>

6️⃣ Make It Executable
~~~~~~~~~~~~~~~~~~~~~~

Modify ``setup.py`` inside ``wall_follow_package``:

.. code-block:: python

   entry_points={
       'console_scripts': [
           'wall_follow_node = wall_follow_package.wall_follow_node:main',
       ],
   },

7️⃣ C++ Alternative (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the following:

.. code-block:: bash

   cd ~/f1tenth_ws
   colcon build --packages-select wall_follow_package
   source install/setup.bash
   ros2 run wall_follow_package wall_follow_node

Alternative: C++ Wall Follow Node Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Students who prefer C++ can use this starter code instead. Create a file ``wall_follow_node.cpp``:

.. raw:: html

   <iframe frameborder="0" scrolling="yes" style="width:100%; height:2283px;" allow="clipboard-write" src="https://emgithub.com/iframe.html?target=https%3A%2F%2Fgithub.com%2FWeber-AGV%2Ff1tenth_lab3_template%2Fblob%2Fmain%2Fwall_follow%2Fsrc%2Fwall_follow_node.cpp&style=default&type=code&showBorder=on&showLineNumbers=on&showFileMeta=on&showFullPath=on&showCopy=on"></iframe>


