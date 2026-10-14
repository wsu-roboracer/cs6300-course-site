"""Lab 1: publish drive commands built from two ROS parameters."""

import rclpy
from rclpy.node import Node

# TODO (Part 2): import AckermannDriveStamped from ackermann_msgs.msg


class Talker(Node):

    def __init__(self):
        super().__init__('talker')

        # TODO (Part 2): declare two parameters, `v` and `d`, each defaulting to 0.0

        # TODO (Part 2): create a publisher for AckermannDriveStamped messages
        # on the `drive` topic

        # TODO (Part 2): create a timer that calls self.publish_drive every
        # 0.001 seconds

    def publish_drive(self):
        # TODO (Part 2): read the current values of `v` and `d`. Read them here,
        # not in __init__, so a change made with `ros2 param set` takes effect.

        # TODO (Part 2): build an AckermannDriveStamped message with
        # drive.speed set to v and drive.steering_angle set to d, then publish it
        pass


def main(args=None):
    rclpy.init(args=args)
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
