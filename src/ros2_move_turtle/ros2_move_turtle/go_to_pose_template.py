#!/usr/bin/env python3
"""Template for the direct Turtlesim go-to-pose controller."""

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Pose


class GoToPose(Node):
    LINEAR_GAIN = 1.0
    ANGULAR_GAIN = 4.0
    MAX_LINEAR_SPEED = 1.5
    MAX_ANGULAR_SPEED = 2.0

    def __init__(self):
        super().__init__('go_to_pose')

        # TODO: Declare and read the target pose and tolerance parameters.
        # Convert angular values from degrees to radians.

        self.position_reached = False
        self.finished = False
        self.command = Twist()

        # TODO: Create the Twist publisher on /turtle1/cmd_vel.
        # TODO: Create the Pose subscriber on /turtle1/pose.
        # TODO: Create a 0.05 s timer to publish the stored command.

    def update_pose(self, pose: Pose):
        """Calculate and store the command from the current turtle pose."""
        # TODO: Return without calculating a new command when finished.
        # TODO: Implement position control.
        # TODO: Switch to orientation control inside the position tolerance.
        # TODO: Implement final-orientation control.
        # TODO: Store a zero command and set finished when the pose is reached.
        pass

    @staticmethod
    def angle_error(error):
        """Return an angle normalized between -pi and pi."""
        # TODO: Normalize the angle with atan2, sin, and cos.
        pass

    def publish_velocity(self):
        """Publish the command stored by the subscriber callback."""
        # TODO: Publish self.command.
        pass


def main(args=None):
    rclpy.init(args=args)
    node = GoToPose()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # TODO: Cancel the timer and publish a final zero command safely.
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
