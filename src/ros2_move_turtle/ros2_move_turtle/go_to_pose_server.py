#!/usr/bin/env python3
"""Servei ROS 2 simple per moure la tortuga fins a una pose objectiu."""

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
        self.position_tolerance = self.declare_parameter('position_tolerance', 0.10).value
        tolerance_deg = self.declare_parameter('angle_tolerance_deg', 2.0).value
        self.angle_tolerance = math.radians(tolerance_deg)

        self.target_x = 0.0
        self.target_y = 0.0
        self.target_theta = 0.0
        self.pose_received = False
        self.position_reached = False
        self.finished = True
        self.shutting_down = False
        self.command = Twist()
        self.motion_done = threading.Event()
        callback_group = ReentrantCallbackGroup()

        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.update_pose, 10,
            callback_group=callback_group)
        self.timer = self.create_timer(
            0.05, self.publish_velocity, callback_group=callback_group)
        self.service = self.create_service(
            RunPose, '/run_pose', self.run_pose, callback_group=callback_group)
        self.get_logger().info('GoToPose server ready on /run_pose.')

    def run_pose(self, request, response):
        if not self.finished:
            response.success = False
            response.message = 'Another motion is already running.'
            return response
        if not self.pose_received:
            response.success = False
            response.message = 'Turtle pose is not available.'
            return response

        self.target_x = float(request.target_x)
        self.target_y = float(request.target_y)
        self.target_theta = math.radians(request.target_theta_deg)
        self.position_reached = False
        self.finished = False
        self.command = Twist()
        self.motion_done.clear()
        self.get_logger().info(
            f'New target: x={self.target_x:.2f}, y={self.target_y:.2f}, '
            f'theta={request.target_theta_deg:.1f} deg')

        if not self.motion_done.wait(timeout=self.MOTION_TIMEOUT):
            self.finished = True
            self.command = Twist()
            response.success = False
            response.message = 'Motion timeout.'
            return response

        if self.shutting_down:
            response.success = False
            response.message = 'Server interrupted.'
            return response

        response.success = True
        response.message = 'Target pose reached successfully.'
        return response

    def update_pose(self, pose):
        self.pose_received = True
        if self.finished:
            return

        linear = 0.0
        if not self.position_reached:
            dx = self.target_x - pose.x
            dy = self.target_y - pose.y
            distance = math.hypot(dx, dy)
            if distance <= self.position_tolerance:
                self.position_reached = True
                self.command = Twist()
                return
            error = self.angle_error(math.atan2(dy, dx) - pose.theta)
            linear = self.LINEAR_GAIN * distance * max(0.0, math.cos(error))
        else:
            error = self.angle_error(self.target_theta - pose.theta)
            if abs(error) <= self.angle_tolerance:
                self.finished = True
                self.command = Twist()
                self.motion_done.set()
                self.get_logger().info('Target pose reached.')
                return

        angular = self.ANGULAR_GAIN * error
        self.command.linear.x = max(0.0, min(linear, self.MAX_LINEAR_SPEED))
        self.command.angular.z = max(
            -self.MAX_ANGULAR_SPEED, min(angular, self.MAX_ANGULAR_SPEED))

    @staticmethod
    def angle_error(error):
        return math.atan2(math.sin(error), math.cos(error))

    def publish_velocity(self):
        self.publisher.publish(self.command)


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
        node.shutting_down = True
        node.finished = True
        node.command = Twist()
        node.publish_velocity()
        node.motion_done.set()
        executor.shutdown(timeout_sec=1.0)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
