#!/usr/bin/env python3

import math
import threading
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from turtle_interfaces.srv import RunPose
from turtlesim.msg import Pose


class RunPoseServer(Node):
    """Execute GoToPose motions requested through a ROS 2 service."""

    MOVE_TO_POSITION = 0
    ROTATE_TO_FINAL_ORIENTATION = 1
    IDLE = 2

    def __init__(self) -> None:
        super().__init__('run_pose_server')

        # Controller parameters
        self.declare_parameter('linear_gain', 1.0)
        self.declare_parameter('angular_gain', 4.0)
        self.declare_parameter('max_linear_speed', 1.5)
        self.declare_parameter('max_angular_speed', 2.0)
        self.declare_parameter('position_tolerance', 0.10)
        self.declare_parameter('angle_tolerance_deg', 2.0)
        self.declare_parameter('motion_timeout', 30.0)

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
        self.angle_tolerance = math.radians(angle_tolerance_deg)

        self.motion_timeout = float(
            self.get_parameter('motion_timeout').value
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
        self.shutting_down = False

        # Used to notify the service callback when motion finishes
        self.motion_done_event = threading.Event()

        # Avoid two simultaneous motion requests
        self.motion_lock = threading.Lock()

        # Allow service, timer and subscriber callbacks to run concurrently
        self.callback_group = ReentrantCallbackGroup()

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
            callback_group=self.callback_group,
        )

        self.control_timer = self.create_timer(
            0.05,
            self.control_loop,
            callback_group=self.callback_group,
        )

        self.run_pose_service = self.create_service(
            RunPose,
            '/run_pose',
            self.run_pose_callback,
            callback_group=self.callback_group,
        )

        self.get_logger().info(
            'RunPose server ready on /run_pose.'
        )

    def pose_callback(self, msg: Pose) -> None:
        """Store the current turtle pose."""
        self.pose = msg

    def run_pose_callback(
        self,
        request: RunPose.Request,
        response: RunPose.Response,
    ) -> RunPose.Response:
        """Receive a target pose, execute it and return the result."""

        # Reject a new request while another motion is running
        if not self.motion_lock.acquire(blocking=False):
            response.success = False
            response.message = 'Another motion is already running.'

            self.get_logger().warning(response.message)
            return response

        try:
            if self.pose is None:
                response.success = False
                response.message = 'Turtle pose is not available.'

                self.get_logger().error(response.message)
                return response

            self.start_motion(
                target_x=float(request.target_x),
                target_y=float(request.target_y),
                target_theta_deg=float(request.target_theta_deg),
            )

            motion_completed = self.motion_done_event.wait(
                timeout=self.motion_timeout
            )

            if self.shutting_down or not rclpy.ok():
                response.success = False
                response.message = 'RunPose server is shutting down.'
                return response

            if not motion_completed:
                self.finish_motion(
                    success=False,
                    message=(
                        'Motion timeout after '
                        f'{self.motion_timeout:.1f} seconds.'
                    ),
                )

            response.success = self.motion_success
            response.message = self.motion_message

            return response

        finally:
            self.motion_lock.release()

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
        self.target_theta = math.radians(target_theta_deg)

        self.state = self.MOVE_TO_POSITION
        self.motion_active = True
        self.motion_finished = False
        self.motion_success = False
        self.motion_message = ''

        self.motion_done_event.clear()

        self.get_logger().info(
            'RunPose motion started. '
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
        return max(minimum, min(value, maximum))

    def distance_to_target(self) -> float:
        """Calculate the Euclidean distance to the target position."""
        if self.pose is None:
            return 0.0

        return math.hypot(
            self.target_x - self.pose.x,
            self.target_y - self.pose.y,
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
        """Execute the active closed-loop controller."""
        if (
            self.shutting_down
            or not self.motion_active
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

        self.motion_success = success
        self.motion_message = message
        self.motion_finished = True
        self.motion_active = False
        self.state = self.IDLE

        self.motion_done_event.set()

        if success:
            self.get_logger().info(message)
        else:
            self.get_logger().error(message)

    def prepare_shutdown(self) -> None:
        """Release pending callbacks and prepare the node for shutdown."""
        if self.shutting_down:
            return

        self.shutting_down = True

        # Publishing is only possible while the ROS 2 context is valid
        if rclpy.ok():
            self.stop_turtle()

        self.state = self.IDLE
        self.motion_active = False
        self.motion_finished = True
        self.motion_success = False
        self.motion_message = 'RunPose server interrupted.'

        # Release a service callback waiting in Event.wait()
        self.motion_done_event.set()

      
def main(args=None) -> None:
    rclpy.init(args=args)

    node = RunPoseServer()
    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(node)

    try:
        executor.spin()

    except KeyboardInterrupt:
        # Avoid logging if ROS 2 has already invalidated the context
        if rclpy.ok():
            node.get_logger().info(
                'RunPose server interrupted by the user.'
            )

    finally:
        node.prepare_shutdown()

        executor.shutdown(timeout_sec=1.0)
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
