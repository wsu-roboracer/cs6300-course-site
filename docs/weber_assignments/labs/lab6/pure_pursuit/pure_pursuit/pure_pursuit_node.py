"""Lab 6b: follow the waypoints recorded in Lab 6a with Pure Pursuit."""

import csv
import math
import os

import rclpy
from ackermann_msgs.msg import AckermannDriveStamped
from ament_index_python.packages import get_package_share_directory
from nav_msgs.msg import Odometry
from rclpy.node import Node


class PurePursuitNode(Node):

    def __init__(self):
        # This name must match the top-level key in config/pure_pursuit.yaml
        # and name= in the launch file, or the parameters are not loaded.
        super().__init__('pure_pursuit_node')

        # TODO (Lab 6b, Part 2): declare three parameters and read their values:
        #   lookahead_distance  default 1.5
        #   speed               default 1.0
        #   waypoint_file       default 'waypoints.csv'

        # TODO (Lab 6b, Part 2): load the waypoints. The CSV is installed to the
        # package's share folder, under maps/:
        #   os.path.join(get_package_share_directory('pure_pursuit'), 'maps', <waypoint_file>)
        # Each row is x, y, z, w, with no header. Store them in self.waypoints
        # as a list of (x, y, z, w) tuples of floats.
        self.waypoints = []

        # TODO (Lab 6b, Part 2): create a publisher for AckermannDriveStamped on /drive

        # TODO (Lab 6b, Part 2): subscribe to /pf/pose/odom (Odometry) with
        # self.odom_callback

    def odom_callback(self, msg):
        # TODO (Lab 6b, Part 2): read the car's position and heading from msg.
        # heading = 2.0 * math.atan2(z, w)

        # TODO (Lab 6b, Part 2): find the index of the waypoint closest to the car.

        # TODO (Lab 6b, Part 2): search forward from that index for the first waypoint
        # at least lookahead_distance from the car. Wrap past the end of the
        # list back to the start, so the car keeps lapping.

        # TODO (Lab 6b, Part 2): transform the lookahead point into the car's frame,
        # so local_y > 0 means it is to the car's left.

        # TODO (Lab 6b, Part 2): compute steering_angle = 2 * local_y / L**2, where L
        # is the distance to the lookahead point. Guard against L near 0.

        # TODO (Lab 6b, Part 2): publish an AckermannDriveStamped with that steering
        # angle and the configured speed.
        pass


def main(args=None):
    rclpy.init(args=args)
    node = PurePursuitNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
