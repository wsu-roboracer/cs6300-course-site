.. _doc_tutorials_wall_follow_pid_steering:

Steering Adjustment Using PID
==============================

Overview
--------

In **autonomous wall following**, maintaining a consistent distance from the wall requires smooth and responsive steering control. Instead of using simple proportional control that can cause oscillations, a **Proportional-Integral-Derivative (PID) controller** provides **precise steering adjustments** based on distance error and its rate of change.

This approach ensures **stable wall tracking** with minimal oscillations, improving both navigation accuracy and vehicle stability.

1️⃣ Why Use PID Control for Steering?
--------------------------------------

Simple proportional control (steering angle = K × error) may cause:

- **Oscillations**, where the car weaves back and forth along the wall.
- **Overshooting**, where corrections are too aggressive.
- **Steady-state error**, where the car never quite reaches the desired distance.
- **Poor response to curves**, causing the car to hit walls on turns.

A **PID controller** provides:

✅ **Smooth steering adjustments** based on distance error.

✅ **Predictive control**, adjusting before the car drifts too far.

✅ **Elimination of steady-state error** through integral action.

✅ **Stable tracking**, minimizing oscillations and overshooting.

2️⃣ PID Control Formula for Steering Adjustment
------------------------------------------------

The **error** is defined as the difference between desired and actual distance to the wall:

.. math::

   e(t) = D_{\text{desired}} - D_{\text{actual}}

The **steering angle** output is calculated using:

.. math::

   \theta = K_p e(t) + K_i \int e(t) dt + K_d \frac{de(t)}{dt}

Where:

- :math:`\theta` = Steering angle (positive = turn away from wall, negative = turn toward wall).
- :math:`K_p` = Proportional gain (reacts to the distance error).
- :math:`K_i` = Integral gain (corrects accumulated distance errors).
- :math:`K_d` = Derivative gain (predicts future distance changes).
- :math:`e(t)` = Distance error.

3️⃣ How Each Term Contributes
------------------------------

Proportional Term (P)
~~~~~~~~~~~~~~~~~~~~~

The **proportional term** provides immediate response to distance error:

**If car is too close to wall** → Steer **away from wall** proportionally.

**If car is too far from wall** → Steer **toward wall** proportionally.

**If car is at desired distance** → **No steering correction** needed.

Integral Term (I)
~~~~~~~~~~~~~~~~~

The **integral term** eliminates steady-state error by accumulating past errors:

**Persistent error on one side** → **Gradually increase steering** to correct.

**Helps maintain exact desired distance** over long periods.

**Prevents drift** on straight walls.

Derivative Term (D)
~~~~~~~~~~~~~~~~~~~

The **derivative term** predicts future errors by monitoring rate of change:

**If drifting away from wall rapidly** → **Steer aggressively** toward wall.

**If approaching wall rapidly** → **Steer aggressively** away from wall.

**If distance is stable** → **Minimal derivative correction** (avoid jittery steering).

**Reduces overshoot** and dampens oscillations.

4️⃣ Example: PID-Based Steering Control
----------------------------------------

Scenario: Maintaining Distance While Wall Following
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Desired Distance** = **0.5 meters**
- **Actual Distance** = **0.7 meters** (too far from wall)
- **Proportional Gain** = :math:`K_p` = 1.5
- **Integral Gain** = :math:`K_i` = 0.05
- **Derivative Gain** = :math:`K_d` = 0.8
- **Distance is increasing at** 0.1 m/s (drifting away)

**Step 1: Compute the Error**

.. math::

   e(t) = 0.5 - 0.7 = -0.2 \text{ meters}

(Negative error means too far from wall)

**Step 2: Compute Steering Angle**

.. math::

   \theta = (1.5 \times -0.2) + (0.05 \times \int -0.2 dt) + (0.8 \times -0.1)

If the accumulated **integral error** over time is **-1.0**, then:

.. math::

   \theta = (1.5 \times -0.2) + (0.05 \times -1.0) + (0.8 \times -0.1)

.. math::

   \theta = -0.3 + (-0.05) + (-0.08) = -0.43 \text{ radians}

Thus, the vehicle will **steer toward the wall by 0.43 radians (≈ 24.6°)**, bringing it back to the desired distance.

5️⃣ Handling Curves and Corners
--------------------------------

Wall following becomes challenging in curves. The **lookahead distance** :math:`D_{t+1}` helps predict future distance:

.. math::

   D_{t+1} = D_t + L\sin(\alpha)

Where:

- :math:`D_t` = Current distance to wall
- :math:`L` = Lookahead distance (typically 1-2 meters)
- :math:`\alpha` = Angle between car's heading and wall

Using :math:`D_{t+1}` instead of :math:`D_t` in the PID error calculation allows:

✅ **Early correction** before entering a curve.

✅ **Smoother navigation** through corners.

✅ **Prevention of wall collisions** on tight turns.

6️⃣ Considerations & Tuning
---------------------------

🛠 **Tuning Kp (Proportional Gain)**

- **Kp too high** → Aggressive steering, oscillations, instability.
- **Kp too low** → Slow response, poor tracking, drifts off course.
- **Start with:** :math:`K_p` = 1.0 to 2.0

🛠 **Tuning Ki (Integral Gain)**

- **Ki too high** → Overshoot, slow settling time.
- **Ki too low** → Steady-state error remains.
- **Start with:** :math:`K_i` = 0.01 to 0.1

🛠 **Tuning Kd (Derivative Gain)**

- **Kd too high** → Sensitive to noise, jittery steering.
- **Kd too low** → Overshooting, slow damping.
- **Start with:** :math:`K_d` = 0.5 to 1.0

🚗 **Tuning Strategy**

1. Set :math:`K_i = 0` and :math:`K_d = 0`, tune :math:`K_p` until response is reasonable but oscillatory.
2. Add :math:`K_d` to **dampen oscillations** and improve stability.
3. Add :math:`K_i` to **eliminate steady-state error** if car consistently stays too close or too far.
4. **Test on curves** and adjust gains for smooth corner navigation.

7️⃣ Integrating Speed Control
-----------------------------

For optimal performance, **adjust speed based on steering angle**:

.. code-block:: python

   if abs(steering_angle) < 0.174:  # < 10 degrees
       speed = 1.5  # m/s (straight sections)
   elif abs(steering_angle) < 0.349:  # < 20 degrees
       speed = 1.0  # m/s (gentle curves)
   else:
       speed = 0.5  # m/s (sharp turns)

This prevents:

- **Loss of control** in sharp turns at high speed.
- **Wall collisions** when steering aggressively.
- **Inefficient slow driving** on straight sections.

8️⃣ Summary
-----------

✅ **PID steering control provides smooth and stable wall following**.

✅ **The derivative term predicts and prevents oscillations**.

✅ **The integral term eliminates steady-state distance errors**.

✅ **Lookahead distance helps navigate curves safely**.

✅ **Speed adjustment based on steering angle improves safety**.

Additional Resources
--------------------

- `RoboRacer Lecture 4: Laplace Domain Dynamics and PID <https://f1tenth-coursekit.readthedocs.io/en/latest/lectures/ModuleB/lecture04.html>`_
