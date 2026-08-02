#!/usr/bin/env python3

import yaml

import rclpy
from rclpy.node import Node

from turtle_interfaces.srv import RunPose


class RunPoseSequenceClient(Node):
    """Execute a sequence of target poses using the RunPose service."""

    def __init__(self) -> None:
        super().__init__('run_pose_sequence_client')

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
        """Load the target pose sequence from a YAML file."""
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

        poses = data.get('poses', [])

        if not poses:
            raise ValueError(
                'The YAML file does not contain any poses.'
            )

        required_fields = {
            'x',
            'y',
            'theta_deg',
        }

        for index, pose in enumerate(poses):
            missing_fields = required_fields - pose.keys()

            if missing_fields:
                raise ValueError(
                    f'Pose {index + 1} is missing fields: '
                    f'{sorted(missing_fields)}'
                )

        return poses

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

    def send_pose(self, pose: dict):
        """Send one target pose to the RunPose server."""
        request = RunPose.Request()

        request.target_x = float(pose['x'])
        request.target_y = float(pose['y'])
        request.target_theta_deg = float(
            pose['theta_deg']
        )

        return self.client.call_async(request)


def main(args=None) -> None:
    rclpy.init(args=args)

    node = RunPoseSequenceClient()

    try:
        poses = node.load_sequence()

        if not node.wait_for_server():
            return

        total_poses = len(poses)

        for index, pose in enumerate(poses, start=1):
            if not rclpy.ok():
                break

            pose_name = pose.get(
                'name',
                f'pose_{index}',
            )

            node.get_logger().info(
                f'Executing pose {index}/{total_poses}: '
                f'{pose_name} — '
                f'x={float(pose["x"]):.2f}, '
                f'y={float(pose["y"]):.2f}, '
                f'theta={float(pose["theta_deg"]):.1f} deg'
            )

            future = node.send_pose(pose)

            rclpy.spin_until_future_complete(
                node,
                future,
            )

            if not rclpy.ok():
                break

            if future.exception() is not None:
                node.get_logger().error(
                    f'Service call failed: '
                    f'{future.exception()}'
                )
                break

            response = future.result()

            if response is None:
                node.get_logger().error(
                    'The service returned no response.'
                )
                break

            if not response.success:
                node.get_logger().error(
                    f'Pose {index} failed: '
                    f'{response.message}'
                )
                break

            node.get_logger().info(
                f'Pose {index} completed: '
                f'{response.message}'
            )

        else:
            node.get_logger().info(
                'Pose sequence completed successfully.'
            )

    except FileNotFoundError:
        node.get_logger().error(
            f'Sequence file not found: '
            f'{node.sequence_file}'
        )

    except (OSError, ValueError, yaml.YAMLError) as error:
        node.get_logger().error(
            f'Could not load pose sequence: {error}'
        )

    except KeyboardInterrupt:
        # Avoid ROS logging after the context has been invalidated
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