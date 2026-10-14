"""Lab 1: republish drive commands with speed and steering angle tripled."""

import rclpy
from rclpy.node import Node

# TODO (Part 2): import AckermannDriveStamped from ackermann_msgs.msg


class Relay(Node):

    def __init__(self):
        super().__init__('relay')

        # TODO (Part 2): create a publisher for AckermannDriveStamped messages
        # on the `drive_relay` topic

        # TODO (Part 2): subscribe to the `drive` topic with self.drive_callback

    def drive_callback(self, msg):
        # TODO (Part 2): build a new AckermannDriveStamped message whose speed
        # and steering angle are 3 times the incoming ones, then publish it
        pass


def main(args=None):
    rclpy.init(args=args)
    node = Relay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
