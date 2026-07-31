#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtle_interfaces.srv import RunPose


class RunPoseClient(Node):
    """Send a target-pose request to the RunPose server."""

    def __init__(self) -> None:
        super().__init__('run_pose_client')

        self.declare_parameter('target_x', 8.0)
        self.declare_parameter('target_y', 3.0)
        self.declare_parameter('target_theta_deg', 90.0)
        self.declare_parameter('service_timeout', 10.0)

        self.target_x = float(
            self.get_parameter('target_x').value
        )
        self.target_y = float(
            self.get_parameter('target_y').value
        )
        self.target_theta_deg = float(
            self.get_parameter('target_theta_deg').value
        )
        self.service_timeout = float(
            self.get_parameter('service_timeout').value
        )

        self.client = self.create_client(
            RunPose,
            '/run_pose',
        )

    def send_request(self):
        """Wait for the service and send the target pose."""
        self.get_logger().info(
            'Waiting for /run_pose service...'
        )

        service_available = self.client.wait_for_service(
            timeout_sec=self.service_timeout
        )

        if not service_available:
            self.get_logger().error(
                '/run_pose service is not available.'
            )
            return None

        request = RunPose.Request()
        request.target_x = self.target_x
        request.target_y = self.target_y
        request.target_theta_deg = self.target_theta_deg

        self.get_logger().info(
            'Sending RunPose request. '
            f'Target: x={self.target_x:.2f}, '
            f'y={self.target_y:.2f}, '
            f'theta={self.target_theta_deg:.1f} deg'
        )

        return self.client.call_async(request)


def main(args=None) -> None:
    rclpy.init(args=args)

    node = RunPoseClient()

    try:
        future = node.send_request()

        if future is None:
            return

        rclpy.spin_until_future_complete(
            node,
            future,
        )

        if future.exception() is not None:
            node.get_logger().error(
                f'Service call failed: {future.exception()}'
            )
            return

        response = future.result()

        if response is None:
            node.get_logger().error(
                'The service returned no response.'
            )
            return

        if response.success:
            node.get_logger().info(
                f'Motion completed: {response.message}'
            )
        else:
            node.get_logger().error(
                f'Motion failed: {response.message}'
            )

    except KeyboardInterrupt:
        node.get_logger().info(
            'RunPose client interrupted by the user.'
        )

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()