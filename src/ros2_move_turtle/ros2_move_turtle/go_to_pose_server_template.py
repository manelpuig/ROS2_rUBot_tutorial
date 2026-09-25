#!/usr/bin/env python3
"""Template for a go-to-pose controller offered as a ROS 2 service."""

import math
import threading

import rclpy
from geometry_msgs.msg import Twist
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from turtle_interfaces.srv import RunPose
from turtlesim.msg import Pose


class GoToPoseServer(Node):
    LINEAR_GAIN = 1.0
    ANGULAR_GAIN = 4.0
    MAX_LINEAR_SPEED = 1.5
    MAX_ANGULAR_SPEED = 2.0
    MOTION_TIMEOUT = 30.0

    def __init__(self):
        super().__init__('go_to_pose_server')

        # TODO: Declare and read the tolerance parameters.
        # TODO: Initialize the target, state indicators, and zero Twist command.
        self.motion_done = threading.Event()
        callback_group = ReentrantCallbackGroup()

        # TODO: Create the publisher, subscriber, timer, and /run_pose service.
        # Give the subscriber, timer, and service the callback group above.

    def run_pose(self, request, response):
        """Receive a target, wait for the movement, and return its result."""
        # TODO: Reject the request if another movement is active.
        # TODO: Store the requested target and start a new movement.
        # TODO: Wait for motion_done with MOTION_TIMEOUT.
        # TODO: Fill response.success and response.message.
        return response

    def update_pose(self, pose: Pose):
        """Calculate and store the velocity command."""
        # TODO: Reuse the controller logic developed in go_to_pose.py.
        # Set motion_done when the complete target pose is reached.
        pass

    @staticmethod
    def angle_error(error):
        # TODO: Normalize the angle between -pi and pi.
        pass

    def publish_velocity(self):
        # TODO: Publish the stored command.
        pass


def main(args=None):
    rclpy.init(args=args)
    node = GoToPoseServer()
    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        # TODO: Stop the turtle and release a waiting service callback.
        executor.shutdown(timeout_sec=1.0)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
