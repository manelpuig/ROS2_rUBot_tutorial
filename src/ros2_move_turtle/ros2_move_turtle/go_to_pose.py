#!/usr/bin/env python3
"""Mou la tortuga fins a una posició i després ajusta l'orientació."""

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
        # Atributs del node, configurables com a paràmetres ROS.
        self.target_x = self.declare_parameter('target_x', 8.0).value
        self.target_y = self.declare_parameter('target_y', 3.0).value
        self.target_theta = math.radians(self.declare_parameter('target_theta_deg', 90.0).value)
        self.position_tolerance = self.declare_parameter('position_tolerance', 0.10).value
        self.angle_tolerance = math.radians(self.declare_parameter('angle_tolerance_deg', 2.0).value)
        self.position_reached = False
        self.finished = False
        self.command = Twist()
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(Pose, '/turtle1/pose', self.update_pose, 10)
        self.timer = self.create_timer(0.05, self.publish_velocity)

    def update_pose(self, pose):
        # El control rep directament una posició vàlida del subscriber.
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
                self.get_logger().info('Posició i orientació assolides.')
                return

        angular = self.ANGULAR_GAIN * error
        self.command.linear.x = max(0.0, min(linear, self.MAX_LINEAR_SPEED))
        self.command.angular.z = max(-self.MAX_ANGULAR_SPEED, min(angular, self.MAX_ANGULAR_SPEED))

    @staticmethod
    def angle_error(error):
        # Error entre -pi i pi per girar pel camí més curt.
        return math.atan2(math.sin(error), math.cos(error))

    def publish_velocity(self):
        self.publisher.publish(self.command)


def main(args=None):
    rclpy.init(args=args)
    node = GoToPose()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.timer.cancel()
        node.finished = True
        node.command = Twist()
        node.publish_velocity()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
