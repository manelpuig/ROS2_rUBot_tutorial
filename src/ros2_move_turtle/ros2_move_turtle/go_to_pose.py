#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Pose


class GoToPose(Node):
    """Move the turtlesim turtle to a target position and orientation."""

    ROTATE_TO_TARGET = 0
    MOVE_TO_TARGET = 1
    ROTATE_TO_FINAL_ORIENTATION = 2
    FINISHED = 3

    def __init__(self) -> None:
        super().__init__('go_to_pose')

        # Target pose parameters
        self.declare_parameter('target_x', 8.0)
        self.declare_parameter('target_y', 3.0)
        self.declare_parameter('target_theta_deg', 90.0)

        # Controller parameters
        self.declare_parameter('linear_gain', 1.0)
        self.declare_parameter('angular_gain', 4.0)
        self.declare_parameter('max_linear_speed', 1.5)
        self.declare_parameter('max_angular_speed', 2.0)
        self.declare_parameter('position_tolerance', 0.10)
        self.declare_parameter('angle_tolerance_deg', 2.0)

        # Read target position
        self.target_x = float(
            self.get_parameter('target_x').value
        )
        self.target_y = float(
            self.get_parameter('target_y').value
        )

        # Read target orientation in degrees
        self.target_theta_deg = float(
            self.get_parameter('target_theta_deg').value
        )

        # Convert target orientation to radians for internal calculations
        self.target_theta = math.radians(self.target_theta_deg)

        # Read controller parameters
        self.linear_gain = float(
            self.get_parameter('linear_gain').value
        )
        self.angular_gain = float(
            self.get_parameter('angular_gain').value
        )
        self.max_linear_speed = float(
            self.get_parameter('max_linear_speed').value
        )
        self.max_angular_speed = float(
            self.get_parameter('max_angular_speed').value
        )
        self.position_tolerance = float(
            self.get_parameter('position_tolerance').value
        )

        self.angle_tolerance_deg = float(
            self.get_parameter('angle_tolerance_deg').value
        )

        # Convert tolerance to radians
        self.angle_tolerance = math.radians(
            self.angle_tolerance_deg
        )

        self.pose: Pose | None = None
        self.state = self.ROTATE_TO_TARGET

        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10,
        )

        self.pose_subscriber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
        )

        # Closed-loop controller at 20 Hz
        self.control_timer = self.create_timer(
            0.05,
            self.control_loop,
        )

        self.get_logger().info(
            'GoToPose started. '
            f'Target: x={self.target_x:.2f}, '
            f'y={self.target_y:.2f}, '
            f'theta={self.target_theta_deg:.1f} deg'
        )

    def pose_callback(self, msg: Pose) -> None:
        """Store the current turtle pose."""
        self.pose = msg

    @staticmethod
    def normalize_angle(angle: float) -> float:
        """Normalize an angle to the interval [-pi, pi]."""
        return math.atan2(
            math.sin(angle),
            math.cos(angle),
        )

    @staticmethod
    def limit(value: float, minimum: float, maximum: float) -> float:
        """Limit a value to the specified interval."""
        return max(minimum, min(value, maximum))

    def distance_to_target(self) -> float:
        """Calculate the Euclidean distance to the target position."""
        if self.pose is None:
            return 0.0

        error_x = self.target_x - self.pose.x
        error_y = self.target_y - self.pose.y

        return math.hypot(error_x, error_y)

    def target_heading(self) -> float:
        """Calculate the heading from the turtle to the target."""
        if self.pose is None:
            return 0.0

        return math.atan2(
            self.target_y - self.pose.y,
            self.target_x - self.pose.x,
        )

    def publish_velocity(
        self,
        linear_velocity: float,
        angular_velocity: float,
    ) -> None:
        """Publish a velocity command."""
        command = Twist()
        command.linear.x = linear_velocity
        command.angular.z = angular_velocity

        self.cmd_vel_publisher.publish(command)

    def stop_turtle(self) -> None:
        """Stop the turtle."""
        self.publish_velocity(0.0, 0.0)

    def control_loop(self) -> None:
        """Execute the closed-loop GoToPose controller."""
        if self.pose is None:
            return

        if self.state == self.ROTATE_TO_TARGET:
            self.rotate_to_target()

        elif self.state == self.MOVE_TO_TARGET:
            self.move_to_target()

        elif self.state == self.ROTATE_TO_FINAL_ORIENTATION:
            self.rotate_to_final_orientation()

        elif self.state == self.FINISHED:
            self.stop_turtle()

    def rotate_to_target(self) -> None:
        """Rotate until the turtle points towards the target position."""
        desired_heading = self.target_heading()

        heading_error = self.normalize_angle(
            desired_heading - self.pose.theta
        )

        if abs(heading_error) <= self.angle_tolerance:
            self.stop_turtle()
            self.state = self.MOVE_TO_TARGET

            self.get_logger().info(
                'Target direction reached. Moving to target position.'
            )
            return

        angular_velocity = self.angular_gain * heading_error

        angular_velocity = self.limit(
            angular_velocity,
            -self.max_angular_speed,
            self.max_angular_speed,
        )

        self.publish_velocity(
            linear_velocity=0.0,
            angular_velocity=angular_velocity,
        )

    def move_to_target(self) -> None:
        """Move towards the target position."""
        distance_error = self.distance_to_target()

        if distance_error <= self.position_tolerance:
            self.stop_turtle()
            self.state = self.ROTATE_TO_FINAL_ORIENTATION

            self.get_logger().info(
                'Target position reached. Adjusting final orientation.'
            )
            return

        desired_heading = self.target_heading()

        heading_error = self.normalize_angle(
            desired_heading - self.pose.theta
        )

        # Rotate again if the heading error becomes larger than 15 degrees.
        heading_correction_limit = math.radians(15.0)

        if abs(heading_error) > heading_correction_limit:
            self.stop_turtle()
            self.state = self.ROTATE_TO_TARGET
            return

        linear_velocity = self.linear_gain * distance_error
        angular_velocity = self.angular_gain * heading_error

        linear_velocity = self.limit(
            linear_velocity,
            0.0,
            self.max_linear_speed,
        )

        angular_velocity = self.limit(
            angular_velocity,
            -self.max_angular_speed,
            self.max_angular_speed,
        )

        self.publish_velocity(
            linear_velocity=linear_velocity,
            angular_velocity=angular_velocity,
        )

    def rotate_to_final_orientation(self) -> None:
        """Rotate until the requested final orientation is reached."""
        orientation_error = self.normalize_angle(
            self.target_theta - self.pose.theta
        )

        if abs(orientation_error) <= self.angle_tolerance:
            self.stop_turtle()
            self.state = self.FINISHED

            final_theta_deg = math.degrees(self.pose.theta)

            self.get_logger().info(
                'Target pose reached successfully. '
                f'Final pose: x={self.pose.x:.2f}, '
                f'y={self.pose.y:.2f}, '
                f'theta={final_theta_deg:.1f} deg'
            )
            return

        angular_velocity = self.angular_gain * orientation_error

        angular_velocity = self.limit(
            angular_velocity,
            -self.max_angular_speed,
            self.max_angular_speed,
        )

        self.publish_velocity(
            linear_velocity=0.0,
            angular_velocity=angular_velocity,
        )


def main(args=None) -> None:
    rclpy.init(args=args)

    node = GoToPose()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_turtle()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()