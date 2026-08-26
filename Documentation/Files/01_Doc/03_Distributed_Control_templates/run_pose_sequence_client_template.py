#!/usr/bin/env python3

"""Student template: execute a YAML sequence through the RunPose service."""

import yaml

import rclpy
from rclpy.node import Node

from turtle_interfaces.srv import RunPose


class RunPoseSequenceClient(Node):
    """Load and execute a sequence of target poses."""

    def __init__(self) -> None:
        super().__init__('run_pose_sequence_client')

        # Unlike the one-pose client, targets are stored in a YAML file.
        self.declare_parameter('sequence_file', '')
        self.declare_parameter('service_timeout', 10.0)

        self.sequence_file = str(
            self.get_parameter('sequence_file').value
        )
        self.service_timeout = float(
            self.get_parameter('service_timeout').value
        )

        self.client = self.create_client(
            RunPose,
            '/run_pose',
        )

    def load_sequence(self) -> list:
        """Load and validate the list of steps from the YAML file."""
        if not self.sequence_file:
            raise ValueError(
                'The sequence_file parameter is empty.'
            )

        with open(
            self.sequence_file,
            'r',
            encoding='utf-8',
        ) as yaml_file:
            data = yaml.safe_load(yaml_file)

        # TODO 1:
        # Read the list stored under the key "steps".
        # Raise ValueError if the YAML root is not a dictionary or if the
        # sequence is empty.
        steps = []

        # TODO 2:
        # Check that every step is a dictionary and contains:
        #   target_x, target_y, target_theta_deg
        # The optional field "name" does not need validation.

        return steps

    def wait_for_server(self) -> bool:
        """Wait until the RunPose service is available."""
        self.get_logger().info(
            'Waiting for /run_pose service...'
        )

        available = self.client.wait_for_service(
            timeout_sec=self.service_timeout
        )

        if not available:
            self.get_logger().error(
                '/run_pose service is not available.'
            )

        return available

    def send_step(self, step: dict):
        """Create and send one asynchronous RunPose request."""
        request = RunPose.Request()

        # TODO 3:
        # Copy target_x, target_y and target_theta_deg from step into request.
        # Convert every value to float.

        return self.client.call_async(request)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = RunPoseSequenceClient()

    try:
        steps = node.load_sequence()

        if not node.wait_for_server():
            return

        total_steps = len(steps)

        # TODO 4:
        # For every step:
        #   1. Show its index, name and target in the log.
        #   2. Call node.send_step(step).
        #   3. Wait with rclpy.spin_until_future_complete(node, future).
        #   4. Check future.exception() and future.result().
        #   5. Stop the sequence if the service reports success == False.
        #   6. Continue only after the current step completed successfully.
        # After the loop, report that all total_steps were completed.
        _ = total_steps

    except FileNotFoundError:
        node.get_logger().error(
            f'Sequence file not found: {node.sequence_file}'
        )

    except (OSError, ValueError, yaml.YAMLError) as error:
        node.get_logger().error(
            f'Could not load pose sequence: {error}'
        )

    except KeyboardInterrupt:
        if rclpy.ok():
            node.get_logger().info(
                'Pose sequence interrupted by the user.'
            )

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
