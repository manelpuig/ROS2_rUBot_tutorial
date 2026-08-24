"""Student template for publishing the Exercise 4 Target B pose."""

import math

from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class Exercise4BroadcasterTemplate(Node):
    """Complete the RPY-to-quaternion conversion and TF message fields."""

    def __init__(self) -> None:
        super().__init__('exercise4_rpy_broadcaster')

        self.declare_parameter('x', 0.350)
        self.declare_parameter('y', -0.350)
        self.declare_parameter('z', 0.170)
        self.declare_parameter('roll_deg', 135.0)
        self.declare_parameter('pitch_deg', 0.0)
        self.declare_parameter('yaw_deg', 60.0)

        self.broadcaster = TransformBroadcaster(self)
        self.timer = self.create_timer(0.1, self.publish_transform)

        self.get_logger().info(
            'Exercise 4 template started. Complete the TODO sections in '
            'exercise4_rpy_template.py.'
        )

    @staticmethod
    def quaternion_from_rpy(
        roll: float,
        pitch: float,
        yaw: float,
    ) -> tuple[float, float, float, float]:
        """Return the ROS quaternion [x, y, z, w]."""
        # TODO 1: Replace the identity quaternion with the conversion from
        # fixed-axis XYZ roll, pitch and yaw. Remember that the angles are
        # expressed in radians and ROS stores the quaternion as [x, y, z, w].
        del roll, pitch, yaw
        return 0.0, 0.0, 0.0, 1.0

    def publish_transform(self) -> None:
        """Build and broadcast the ur5e_base -> target_b transform."""
        x = float(self.get_parameter('x').value)
        y = float(self.get_parameter('y').value)
        z = float(self.get_parameter('z').value)
        roll = math.radians(float(self.get_parameter('roll_deg').value))
        pitch = math.radians(float(self.get_parameter('pitch_deg').value))
        yaw = math.radians(float(self.get_parameter('yaw_deg').value))

        qx, qy, qz, qw = self.quaternion_from_rpy(roll, pitch, yaw)

        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()

        # TODO 2: Assign the parent and child frame identifiers.
        transform.header.frame_id = 'ur5e_base'
        transform.child_frame_id = 'target_b'

        # TODO 3: Assign the translation in metres.
        transform.transform.translation.x = x
        transform.transform.translation.y = y
        transform.transform.translation.z = z

        # TODO 4: Assign the quaternion in ROS [x, y, z, w] order.
        transform.transform.rotation.x = qx
        transform.transform.rotation.y = qy
        transform.transform.rotation.z = qz
        transform.transform.rotation.w = qw

        self.broadcaster.sendTransform(transform)


def main(args=None) -> None:
    """Run the student template broadcaster."""
    rclpy.init(args=args)
    node = Exercise4BroadcasterTemplate()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
