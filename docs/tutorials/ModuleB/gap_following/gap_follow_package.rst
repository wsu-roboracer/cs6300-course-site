.. _doc_tutorials_gap_follow_package:

Create Gap Following Package
=============================

To set up your gap following package within the driver stack container follow these steps:

1️⃣ Create the Gap Follow Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inside the driver stack container, navigate to your ROS 2 workspace ``~/f1tenth_ws/src`` and create a new package:

.. code-block:: bash

   cd ~/f1tenth_ws/src
   ros2 pkg create gap_follow --build-type ament_python --dependencies rclpy sensor_msgs std_msgs ackermann_msgs

.. note::

   **Dependencies:**

   - ``rclpy`` (ROS Client Library for Python)
   - ``sensor_msgs`` (Standard Sensor Messages)
   - ``std_msgs`` (Standard ROS Messages)
   - ``ackermann_msgs`` (Ackermann Drive Messages)

2️⃣ Modify package.xml
~~~~~~~~~~~~~~~~~~~~~~

Ensure ``package.xml`` includes dependencies such as ``rclpy``, ``sensor_msgs``, ``std_msgs``, and ``ackermann_msgs``. Open ``package.xml`` and verify:

.. code-block:: xml

   <depend>rclpy</depend>
   <depend>sensor_msgs</depend>
   <depend>std_msgs</depend>
   <depend>ackermann_msgs</depend>

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
   find_package(ackermann_msgs REQUIRED)

Ensure the ``add_executable`` or ``ament_target_dependencies`` includes these necessary dependencies.

4️⃣ Install Dependencies Using rosdep
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the following to install missing dependencies:

.. code-block:: bash

   cd ~/f1tenth_ws
   rosdep install --from-paths src --ignore-src -r -y

5️⃣ Implement the Gap Follow Node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You'll create a gap follow node that processes LiDAR data (``/scan``) to find the largest gap and publishes steering commands to navigate through it.

**Example: Python Gap Follow Node (gap_follow_node.py)**

Create a file inside ``gap_follow/gap_follow_node.py``:

.. raw:: html

    <iframe frameborder="0" scrolling="no" style="width:100%; height:1569px;" allow="clipboard-write" src="https://emgithub.com/iframe.html?target=https%3A%2F%2Fgithub.com%2FWeber-AGV%2Ff1tenth_lab4_template%2Fblob%2Fmain%2Fgap_follow%2Fscripts%2Freactive_node.py&style=default&type=code&showBorder=on&showLineNumbers=on&showFileMeta=on&showFullPath=on&showCopy=on"></iframe>

6️⃣ Make It Executable
~~~~~~~~~~~~~~~~~~~~~~

Modify ``setup.py`` inside ``gap_follow``:

.. code-block:: python

   entry_points={
       'console_scripts': [
           'gap_follow_node = gap_follow.gap_follow_node:main',
       ],
   },

7️⃣ Build & Run
~~~~~~~~~~~~~~~

Run the following:

.. code-block:: bash

   cd ~/f1tenth_ws
   colcon build --packages-select gap_follow
   source install/setup.bash
   ros2 run gap_follow gap_follow_node

C++ Alternative Implementation
-------------------------------

If you prefer to implement the Gap Follow node in C++, you can use the following starter code:

.. raw:: html

  <iframe frameborder="0" scrolling="no" style="width:100%; height:1569px;" allow="clipboard-write" src="https://emgithub.com/iframe.html?target=https%3A%2F%2Fgithub.com%2FWeber-AGV%2Ff1tenth_lab4_template%2Fblob%2Fmain%2Fgap_follow%2Fsrc%2Freactive_node.cpp&style=default&type=code&showBorder=on&showLineNumbers=on&showFileMeta=on&showFullPath=on&showCopy=on"></iframe>

**Note**: When using C++, ensure your package is created with ``--build-type ament_cmake`` and that your ``CMakeLists.txt`` includes the necessary dependencies (``rclcpp``, ``sensor_msgs``, ``ackermann_msgs``, etc.).
