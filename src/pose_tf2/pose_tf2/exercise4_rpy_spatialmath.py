"""Publish the Exercise 4 pose using spatialmath.base conversions."""

from geometry_msgs.msg import TransformStamped
import numpy as np
import rclpy
from rclpy.node import Node
from spatialmath.base import r2q, rpy2r, tr2angvec, tr2eul
from tf2_ros import TransformBroadcaster


class Exercise4SpatialMath(Node):
    """Broadcast Target B with respect to the UR5e base frame."""

    def __init__(self) -> None:
        super().__init__('exercise4_rpy_spatialmath')

        self.declare_parameter('x', 0.350)
        self.declare_parameter('y', -0.350)
        self.declare_parameter('z', 0.170)
        self.declare_parameter('roll_deg', 135.0)
        self.declare_parameter('pitch_deg', 0.0)
        self.declare_parameter('yaw_deg', 60.0)

        self.broadcaster = TransformBroadcaster(self)
        self.print_conversions()
        self.timer = self.create_timer(0.1, self.publish_transform)

    def pose(self):
        """Return the translation, rotation matrix and ROS quaternion."""
        translation = [
            float(self.get_parameter(axis).value) for axis in ('x', 'y', 'z')
        ]
        rpy_deg = [
            float(self.get_parameter(angle).value)
            for angle in ('roll_deg', 'pitch_deg', 'yaw_deg')
        ]

        # R = Rz(yaw) @ Ry(pitch) @ Rx(roll).
        rotation = rpy2r(rpy_deg, unit='deg', order='zyx')

        # SpatialMath: [w, x, y, z] -> ROS: [x, y, z, w].
        qw, qx, qy, qz = r2q(rotation)
        quaternion_ros = [qx, qy, qz, qw]
        return translation, rpy_deg, rotation, quaternion_ros

    def print_conversions(self) -> None:
        """Print the pose representations requested in Exercise 4."""
        translation, rpy_deg, rotation, quaternion = self.pose()
        euler_zyz = tr2eul(rotation, unit='deg')
        angle_deg, axis = tr2angvec(rotation, unit='deg')

        self.get_logger().info(
            '\nExercise 4 with spatialmath.base'
            f'\nTranslation [m]: {np.round(translation, 3)}'
            f'\nRPY [deg]: {np.round(rpy_deg, 3)}'
            f'\nRotation matrix R:\n{np.round(rotation, 6)}'
            f'\nEuler ZYZ [deg]: {np.round(euler_zyz, 3)}'
            f'\nApproach vector: {np.round(rotation[:, 2], 6)}'
            f'\nOrthogonal vector: {np.round(rotation[:, 1], 6)}'
            f'\nAngle-axis: {angle_deg:.3f} deg around {np.round(axis, 6)}'
            f'\nQuaternion ROS [x, y, z, w]: {np.round(quaternion, 6)}'
        )

    def publish_transform(self) -> None:
        """Publish the transform ur5e_base -> target_b."""
        translation, _, _, quaternion = self.pose()

        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = 'ur5e_base'
        transform.child_frame_id = 'target_b'

        transform.transform.translation.x = translation[0]
        transform.transform.translation.y = translation[1]
        transform.transform.translation.z = translation[2]
        transform.transform.rotation.x = quaternion[0]
        transform.transform.rotation.y = quaternion[1]
        transform.transform.rotation.z = quaternion[2]
        transform.transform.rotation.w = quaternion[3]

        self.broadcaster.sendTransform(transform)


def main(args=None) -> None:
    """Run the SpatialMath Exercise 4 broadcaster."""
    rclpy.init(args=args)
    node = Exercise4SpatialMath()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
