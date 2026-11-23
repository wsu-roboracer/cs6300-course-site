"""Lab 6: record the car's poses from the particle filter to a CSV file."""

import csv
import math
import os

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node

# Where the waypoints are saved. Lab 7 reads them from this folder.
CSV_PATH = os.path.expanduser('~/f1tenth_ws/src/lab6/pure_pursuit/maps/waypoints.csv')

# Only record a new waypoint once the car has moved at least this far (meters).
MIN_SPACING = 0.1


class WaypointLogger(Node):

    def __init__(self):
        super().__init__('waypoint_logger')

        # TODO (Lab 6, Part 2): open CSV_PATH for writing and keep a csv.writer for it.
        # Create the maps/ folder first if it does not exist.

        # TODO (Lab 6, Part 2): subscribe to /pf/pose/odom (Odometry) with
        # self.odom_callback

        # TODO (Lab 6, Part 2): set up whatever you need to track the last recorded
        # position and count the waypoints written.

        # Optional: the live RViz2 visualization from the README goes here.

    def odom_callback(self, msg):
        # TODO (Lab 6, Part 2): read x and y from msg.pose.pose.position, and z and w
        # from msg.pose.pose.orientation.

        # TODO (Lab 6, Part 2): skip this pose if it is less than MIN_SPACING from the
        # last waypoint you recorded (math.hypot).

        # TODO (Lab 6, Part 2): write x, y, z, w as one CSV row, with no header row.

        # TODO (Lab 6, Part 2): log a confirmation every 50th waypoint, so you can see
        # it is recording without flooding the terminal.
        pass

    def destroy_node(self):
        # TODO (Lab 6, Part 2): close the CSV file so the last rows are saved.
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = WaypointLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
