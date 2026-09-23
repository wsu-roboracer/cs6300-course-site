.. _doc_tutorials_find_best_point_disparity:

Finding the Best Point: Disparity Selection
============================================

When environments get more complex — with tighter spaces and more obstacles — basic "farthest point" methods can become less reliable. **Disparity methods** offer a smarter way to steer through tight environments.

🛠 What is a Disparity?
-----------------------

- A **disparity** is a **large jump** between two consecutive LiDAR distance readings.
- It typically happens at the **edge of an obstacle**.

For example:

.. list-table::
   :header-rows: 1
   :widths: 20 30

   * - Angle
     - Distance (m)
   * - 10°
     - 2.5
   * - 11°
     - 2.5
   * - 12°
     - 0.5

A big drop from 2.5m to 0.5m → indicates an obstacle edge!

🧠 Why Use Disparity?
---------------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Problem
     - How Disparity Solves It
   * - Farthest point may not be safest
     - Disparity finds edges and aims between them
   * - Can't detect narrow gaps
     - Disparity highlights tight spaces
   * - Unclear safest direction
     - Disparity clarifies open regions

✅ **Disparity methods naturally guide the car between obstacles**, rather than just toward distant points.

🛠 How It Works
---------------

Step 1: Focus on the Largest Gap
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After preprocessing LiDAR data and masking close obstacles, select the largest gap.

Step 2: Detect Disparities
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compare each consecutive range. If the distance changes by more than a **disparity threshold**, mark it.

Step 3: Find the Open Region
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the detected disparities to find spaces between obstacles.

Step 4: Aim for the Middle
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pick a point halfway between two disparities.

✏️ Python Example (Disparity-Based Selection)
----------------------------------------------

.. code-block:: python

   def find_best_point_disparity(self, ranges, start_idx, end_idx, disparity_threshold=0.5):
       """
       Find the best point within a gap using disparity detection.

       Disparities (large jumps in distance) indicate obstacle edges.
       We aim for the middle of the free space between disparities.

       Args:
           ranges (np.array): Processed LiDAR data
           start_idx (int): Starting index of the gap
           end_idx (int): Ending index of the gap
           disparity_threshold (float): Minimum distance change to count as disparity

       Returns:
           best_point_idx (int): Index of the selected steering point
       """
       gap_ranges = ranges[start_idx:end_idx+1]

       disparities = []
       for i in range(len(gap_ranges) - 1):
           if abs(gap_ranges[i] - gap_ranges[i+1]) > disparity_threshold:
               disparities.append(i)

       if len(disparities) >= 2:
           # Aim for the middle between the first two disparities
           middle_idx_in_gap = (disparities[0] + disparities[1]) // 2
           best_point_idx = start_idx + middle_idx_in_gap
       else:
           # Fallback to farthest point if no clear disparities
           best_point_idx = self.find_best_point(ranges, start_idx, end_idx)

       return best_point_idx

✅ This logic gracefully falls back to farthest point if no disparities are found.

📊 Visual Diagram
-----------------

.. code-block:: text

   Obstacle Left     Free Space       Obstacle Right
          |               |               |
          v               v               v
   [0.4] [0.5] [2.5] [2.5] [2.5] [0.6] [0.5]

   Big disparity -->    Free space    <-- Big disparity

- Disparity detection finds obstacle edges.
- We aim toward the center of the safe free space.

⚡ Advantages Over Farthest Point
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Farthest Point
     - Disparity Method
   * - May steer near obstacles
     - Steers between obstacles
   * - Works best in wide-open areas
     - Works better in tight environments
   * - Can be fooled by noise
     - Disparity uses clear jumps

🚀 Summary
----------

- Detect sudden changes (disparities) in LiDAR data.
- Use disparities to find open spaces.
- Aim between obstacles for safer, smarter navigation.
- Improves performance in cluttered or narrow environments.

✅ **Disparity-based selection is more robust in complex, tight environments!**

Additional Resources
--------------------

- `RoboRacer Lecture 5: Follow the Gap: Obstacle Avoidance <https://f1tenth-coursekit.readthedocs.io/en/latest/lectures/ModuleB/lecture05.html>`_
