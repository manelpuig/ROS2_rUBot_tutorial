#!/usr/bin/env python3
"""Client simple per executar una seqüència de poses des d'un fitxer YAML."""

import yaml

import rclpy
from rclpy.node import Node
from turtle_interfaces.srv import RunPose


class GoToPoseSequenceClient(Node):
    def __init__(self):
        super().__init__('go_to_pose_sequence_client')
        self.sequence_file = self.declare_parameter('sequence_file', '').value
        self.client = self.create_client(RunPose, '/run_pose')

    def load_sequence(self):
        with open(self.sequence_file, encoding='utf-8') as yaml_file:
            return yaml.safe_load(yaml_file)['steps']

    def send_request(self, pose):
        request = RunPose.Request()
        request.target_x = float(pose['target_x'])
        request.target_y = float(pose['target_y'])
        request.target_theta_deg = float(pose['target_theta_deg'])
        return self.client.call_async(request)


def main(args=None):
    rclpy.init(args=args)
    node = GoToPoseSequenceClient()
    try:
        if not node.client.wait_for_service(timeout_sec=10.0):
            node.get_logger().error('/run_pose service is not available.')
            return

        poses = node.load_sequence()
        for index, pose in enumerate(poses, start=1):
            name = pose.get('name', f'pose_{index}')
            node.get_logger().info(f'Executing {name} ({index}/{len(poses)}).')

            future = node.send_request(pose)
            rclpy.spin_until_future_complete(node, future)
            response = future.result()
            if not response.success:
                node.get_logger().error(response.message)
                break
        else:
            node.get_logger().info('Pose sequence completed successfully.')
    except (OSError, KeyError, TypeError, yaml.YAMLError) as error:
        node.get_logger().error(f'Could not load pose sequence: {error}')
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
