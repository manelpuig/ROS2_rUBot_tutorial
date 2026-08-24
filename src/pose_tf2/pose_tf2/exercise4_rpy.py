"""Publish the Exercise 4 Target B pose as a ROS 2 TF transform."""

import math

from geometry_msgs.msg import TransformStamped
import numpy as np
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster

from pose_tf2.pose_math import angle_axis_from_matrix
from pose_tf2.pose_math import euler_zyz_from_matrix
from pose_tf2.pose_math import quaternion_xyzw_from_rpy
from pose_tf2.pose_math import rotation_matrix_from_rpy


class Exercise4Broadcaster(Node):
    """Broadcast the pose of Target B with respect to the UR5e base frame."""

    def __init__(self) -> None:
        super().__init__('exercise4_rpy_broadcaster')

        self.declare_parameter('x', 0.350)
        self.declare_parameter('y', -0.350)
        self.declare_parameter('z', 0.170)
        self.declare_parameter('roll_deg', 135.0)
        self.declare_parameter('pitch_deg', 0.0)
        self.declare_parameter('yaw_deg', 60.0)
        self.declare_parameter('publish_rate', 10.0)

        self.parent_frame = 'ur5e_base'
        self.child_frame = 'target_b'
        self.broadcaster = TransformBroadcaster(self)

        publish_rate = float(self.get_parameter('publish_rate').value)
        if publish_rate <= 0.0:
            raise ValueError('publish_rate must be greater than zero')

        self._print_pose_conversions()
        self.timer = self.create_timer(1.0 / publish_rate, self.publish_transform)

    def _pose_values(self) -> tuple[float, float, float, float, float, float]:
        """Read the current translation in metres and RPY angles in radians."""
        x = float(self.get_parameter('x').value)
        y = float(self.get_parameter('y').value)
        z = float(self.get_parameter('z').value)
        roll = math.radians(float(self.get_parameter('roll_deg').value))
        pitch = math.radians(float(self.get_parameter('pitch_deg').value))
        yaw = math.radians(float(self.get_parameter('yaw_deg').value))
        return x, y, z, roll, pitch, yaw

    def _print_pose_conversions(self) -> None:
        """Print all pose representations requested in Exercise 4."""
        x, y, z, roll, pitch, yaw = self._pose_values()
        rotation = rotation_matrix_from_rpy(roll, pitch, yaw)
        quaternion = quaternion_xyzw_from_rpy(roll, pitch, yaw)
        euler_zyz = np.degrees(euler_zyz_from_matrix(rotation))
        angle, axis = angle_axis_from_matrix(rotation)
        approach = rotation[:, 2]
        orthogonal = rotation[:, 1]

        matrix_text = np.array2string(
            rotation,
            precision=6,
            suppress_small=True,
        )
        self.get_logger().info(
            '\nExercise 4 pose: target_b with respect to ur5e_base'
            f'\nTranslation [m]: [{x:.3f}, {y:.3f}, {z:.3f}]'
            '\nRPY [deg]: '
            f'[{math.degrees(roll):.3f}, {math.degrees(pitch):.3f}, '
            f'{math.degrees(yaw):.3f}]'
            f'\nRotation matrix R:\n{matrix_text}'
            '\nEuler ZYZ [deg]: '
            f'{np.array2string(euler_zyz, precision=3, suppress_small=True)}'
            '\nApproach vector: '
            f'{np.array2string(approach, precision=6, suppress_small=True)}'
            '\nOrthogonal vector: '
            f'{np.array2string(orthogonal, precision=6, suppress_small=True)}'
            f'\nAngle-axis: {math.degrees(angle):.3f} deg around '
            f'{np.array2string(axis, precision=6, suppress_small=True)}'
            '\nQuaternion ROS [x, y, z, w]: '
            f'[{quaternion[0]:.6f}, {quaternion[1]:.6f}, '
            f'{quaternion[2]:.6f}, {quaternion[3]:.6f}]'
        )

    def publish_transform(self) -> None:
        """Publish ur5e_base -> target_b using the current parameters."""
        x, y, z, roll, pitch, yaw = self._pose_values()
        qx, qy, qz, qw = quaternion_xyzw_from_rpy(roll, pitch, yaw)

        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = self.parent_frame
        transform.child_frame_id = self.child_frame

        transform.transform.translation.x = x
        transform.transform.translation.y = y
        transform.transform.translation.z = z
        transform.transform.rotation.x = qx
        transform.transform.rotation.y = qy
        transform.transform.rotation.z = qz
        transform.transform.rotation.w = qw

        self.broadcaster.sendTransform(transform)


def main(args=None) -> None:
    """Run the Exercise 4 TF2 broadcaster."""
    rclpy.init(args=args)
    node = Exercise4Broadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
