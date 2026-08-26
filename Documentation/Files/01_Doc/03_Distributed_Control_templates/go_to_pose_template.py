#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Pose


class GoToPose(Node):
    """Move the turtlesim turtle to a target position and orientation."""

    MOVE_TO_POSITION = 0
    ROTATE_TO_FINAL_ORIENTATION = 1
    IDLE = 2

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

        # Read target parameters
        target_x = float(
            self.get_parameter('target_x').value
        )

        target_y = float(
            self.get_parameter('target_y').value
        )

        target_theta_deg = float(
            self.get_parameter('target_theta_deg').value
        )

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

        angle_tolerance_deg = float(
            self.get_parameter('angle_tolerance_deg').value
        )

        self.angle_tolerance = math.radians(
            angle_tolerance_deg
        )

        # Current turtle pose
        self.pose: Pose | None = None

        # Target pose
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_theta_deg = 0.0
        self.target_theta = 0.0

        # Motion state
        self.state = self.IDLE
        self.motion_active = False
        self.motion_finished = False
        self.motion_success = False
        self.motion_message = ''

        # Velocity publisher
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10,
        )

        # Pose subscriber
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

        # Start the requested motion
        self.start_motion(
            target_x=target_x,
            target_y=target_y,
            target_theta_deg=target_theta_deg,
        )

    def pose_callback(self, msg: Pose) -> None:
        """Store the current turtle pose."""
        self.pose = msg

    def start_motion(
        self,
        target_x: float,
        target_y: float,
        target_theta_deg: float,
    ) -> None:
        """Initialize a new target-pose motion."""
        self.target_x = target_x
        self.target_y = target_y
        self.target_theta_deg = target_theta_deg

        # Internal angular calculations use radians
        self.target_theta = math.radians(
            self.target_theta_deg
        )

        self.state = self.MOVE_TO_POSITION
        self.motion_active = True
        self.motion_finished = False
        self.motion_success = False
        self.motion_message = ''

        self.get_logger().info(
            'GoToPose motion started. '
            f'Target: x={self.target_x:.2f}, '
            f'y={self.target_y:.2f}, '
            f'theta={self.target_theta_deg:.1f} deg'
        )

    @staticmethod
    def normalize_angle(angle: float) -> float:
        """Normalize an angle to the interval [-pi, pi]."""
        return math.atan2(
            math.sin(angle),
            math.cos(angle),
        )

    @staticmethod
    def limit(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """Limit a value to the specified interval."""
        return max(
            minimum,
            min(value, maximum),
        )

    def distance_to_target(self) -> float:
        """Calculate the Euclidean distance to the target position."""
        if self.pose is None:
            return 0.0

        error_x = self.target_x - self.pose.x
        error_y = self.target_y - self.pose.y

        return math.hypot(
            error_x,
            error_y,
        )

    def target_heading(self) -> float:
        """Calculate the direction from the turtle to the target."""
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
        self.publish_velocity(
            linear_velocity=0.0,
            angular_velocity=0.0,
        )

    def control_loop(self) -> None:
        """Execute the closed-loop GoToPose controller."""
        if (
            not self.motion_active
            or self.motion_finished
            or self.pose is None
        ):
            return

        if self.state == self.MOVE_TO_POSITION:
            self.move_to_position()

        elif self.state == self.ROTATE_TO_FINAL_ORIENTATION:
            self.rotate_to_final_orientation()

    def move_to_position(self) -> None:
        """Move towards the target position."""
        # TODO: Complete the MOVE_TO_POSITION state.
        #
        # Suggested steps:
        # 1. Calculate the distance to the target.
        # 2. If the position tolerance is reached:
        #    - stop the turtle;
        #    - change to ROTATE_TO_FINAL_ORIENTATION;
        #    - return from this function.
        # 3. Calculate the desired heading and heading error.
        # 4. Calculate and limit the linear and angular velocities.
        # 5. Publish the velocity command.
        #
        # Useful attributes and methods:
        # self.pose, self.distance_to_target(), self.target_heading()
        # self.normalize_angle(), self.limit(), self.publish_velocity()
        # self.position_tolerance, self.linear_gain, self.angular_gain
        # self.max_linear_speed, self.max_angular_speed
        self.stop_turtle()

    def rotate_to_final_orientation(self) -> None:
        """Rotate until the requested final orientation is reached."""
        # TODO: Complete the ROTATE_TO_FINAL_ORIENTATION state.
        #
        # Suggested steps:
        # 1. Calculate and normalize the final orientation error.
        # 2. If the angle tolerance is reached:
        #    - call finish_motion(success=True, message=...);
        #    - return from this function.
        # 3. Calculate and limit the angular velocity.
        # 4. Publish zero linear velocity and the angular velocity.
        #
        # Useful attributes and methods:
        # self.pose, self.target_theta, self.normalize_angle()
        # self.limit(), self.publish_velocity(), self.finish_motion()
        # self.angle_tolerance, self.angular_gain
        # self.max_angular_speed
        self.stop_turtle()

    def finish_motion(
        self,
        success: bool,
        message: str,
    ) -> None:
        """Stop the turtle and store the motion result."""
        if self.motion_finished:
            return

        self.stop_turtle()
        self.control_timer.cancel()

        self.motion_success = success
        self.motion_message = message
        self.motion_finished = True
        self.motion_active = False
        self.state = self.IDLE

        if success:
            self.get_logger().info(message)
        else:
            self.get_logger().error(message)


def main(args=None) -> None:
    rclpy.init(args=args)

    node = GoToPose()

    try:
        while rclpy.ok() and not node.motion_finished:
            rclpy.spin_once(
                node,
                timeout_sec=0.1,
            )

    except KeyboardInterrupt:
        node.get_logger().info(
            'Motion interrupted by the user.'
        )

    finally:
        # Always stop the turtle before closing the node
        node.stop_turtle()

        # Allow ROS 2 to process the final zero-velocity command
        if rclpy.ok():
            rclpy.spin_once(
                node,
                timeout_sec=0.1,
            )

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

