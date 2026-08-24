import math

import numpy as np

from pose_tf2.pose_math import angle_axis_from_matrix
from pose_tf2.pose_math import euler_zyz_from_matrix
from pose_tf2.pose_math import quaternion_xyzw_from_rpy
from pose_tf2.pose_math import rotation_matrix_from_rpy


def test_exercise4_pose_conversions():
    roll = math.radians(135.0)
    pitch = math.radians(0.0)
    yaw = math.radians(60.0)

    rotation = rotation_matrix_from_rpy(roll, pitch, yaw)
    expected_rotation = np.array([
        [0.5, 0.6123724357, 0.6123724357],
        [0.8660254038, -0.3535533906, -0.3535533906],
        [0.0, 0.7071067812, -0.7071067812],
    ])
    np.testing.assert_allclose(rotation, expected_rotation, atol=1e-9)

    quaternion = quaternion_xyzw_from_rpy(roll, pitch, yaw)
    expected_quaternion = np.array([
        0.8001031452,
        0.4619397663,
        0.1913417162,
        0.3314135740,
    ])
    np.testing.assert_allclose(quaternion, expected_quaternion, atol=1e-9)
    assert math.isclose(np.linalg.norm(quaternion), 1.0, abs_tol=1e-12)

    euler_zyz = np.degrees(euler_zyz_from_matrix(rotation))
    np.testing.assert_allclose(euler_zyz, [-30.0, 135.0, 90.0], atol=1e-9)

    angle, axis = angle_axis_from_matrix(rotation)
    assert math.isclose(math.degrees(angle), 141.2908077, abs_tol=1e-7)
    np.testing.assert_allclose(
        axis,
        [0.84802901, 0.48960978, 0.20280301],
        atol=1e-8,
    )
