#!/usr/bin/env python3
"""Lab 2: brake the car when a collision is imminent."""

import numpy as np  # noqa: F401  (you will need this)
import rclpy
from ackermann_msgs.msg import AckermannDriveStamped  # noqa: F401
from nav_msgs.msg import Odometry  # noqa: F401
from rclpy.node import Node
from sensor_msgs.msg import LaserScan  # noqa: F401


class SafetyNode(Node):
    """Handles emergency braking."""

    def __init__(self):
        super().__init__('safety_node')

        # The car's current longitudinal speed in m/s, updated by odom_callback.
        self.speed = 0.0

        # TODO: create a publisher for AckermannDriveStamped messages on /drive

        # TODO: subscribe to /scan (LaserScan) with self.scan_callback

        # TODO: subscribe to /ego_racecar/odom (Odometry) with self.odom_callback

    def odom_callback(self, odom_msg):
        # TODO: store the car's speed. It is the x component of the linear
        # velocity: odom_msg.twist.twist.linear.x
        pass

    def scan_callback(self, scan_msg):
        # TODO: work out the angle of every beam from scan_msg.angle_min and
        # scan_msg.angle_increment. Angle 0 is straight ahead.

        # TODO: calculate the iTTC of every beam: the range divided by how fast
        # the car is closing on that beam, speed * cos(angle). A beam the car
        # is not closing on has no time to collision.

        # TODO: ignore readings that are inf or nan

        # TODO: if the smallest iTTC is below your threshold, publish an
        # AckermannDriveStamped message with drive.speed set to 0.0 to brake
        pass


def main(args=None):
    rclpy.init(args=args)
    safety_node = SafetyNode()
    try:
        rclpy.spin(safety_node)
    except KeyboardInterrupt:
        pass
    finally:
        safety_node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
