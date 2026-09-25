#!/usr/bin/env python3
"""Client simple per demanar una pose al servei /run_pose."""

import rclpy
from rclpy.node import Node
from turtle_interfaces.srv import RunPose


class GoToPoseClient(Node):
    def __init__(self):
        super().__init__('go_to_pose_client')
        self.target_x = self.declare_parameter('target_x', 8.0).value
        self.target_y = self.declare_parameter('target_y', 3.0).value
        self.target_theta = self.declare_parameter('target_theta_deg', 90.0).value
        self.client = self.create_client(RunPose, '/run_pose')

    def send_request(self):
        if not self.client.wait_for_service(timeout_sec=10.0):
            self.get_logger().error('/run_pose service is not available.')
            return None

        request = RunPose.Request()
        request.target_x = float(self.target_x)
        request.target_y = float(self.target_y)
        request.target_theta_deg = float(self.target_theta)
        return self.client.call_async(request)


def main(args=None):
    rclpy.init(args=args)
    node = GoToPoseClient()
    try:
        future = node.send_request()
        if future is not None:
            rclpy.spin_until_future_complete(node, future)
            response = future.result()
            if response.success:
                node.get_logger().info(response.message)
            else:
                node.get_logger().error(response.message)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
