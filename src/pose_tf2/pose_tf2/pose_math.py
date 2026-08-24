"""Small, explicit pose-conversion helpers used by the TF2 exercise."""

import math

import numpy as np


def rotation_matrix_from_rpy(
    roll: float,
    pitch: float,
    yaw: float,
) -> np.ndarray:
    """Return Rz(yaw) @ Ry(pitch) @ Rx(roll), with angles in radians."""
    cr = math.cos(roll)
    sr = math.sin(roll)
    cp = math.cos(pitch)
    sp = math.sin(pitch)
    cy = math.cos(yaw)
    sy = math.sin(yaw)

    return np.array([
        [
            cy * cp,
            cy * sp * sr - sy * cr,
            cy * sp * cr + sy * sr,
        ],
        [
            sy * cp,
            sy * sp * sr + cy * cr,
            sy * sp * cr - cy * sr,
        ],
        [-sp, cp * sr, cp * cr],
    ])


def quaternion_xyzw_from_rpy(
    roll: float,
    pitch: float,
    yaw: float,
) -> tuple[float, float, float, float]:
    """Convert fixed-axis XYZ RPY angles to a normalized ROS quaternion."""
    half_roll = roll / 2.0
    half_pitch = pitch / 2.0
    half_yaw = yaw / 2.0

    cr = math.cos(half_roll)
    sr = math.sin(half_roll)
    cp = math.cos(half_pitch)
    sp = math.sin(half_pitch)
    cy = math.cos(half_yaw)
    sy = math.sin(half_yaw)

    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    qw = cr * cp * cy + sr * sp * sy

    norm = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
    return qx / norm, qy / norm, qz / norm, qw / norm


def euler_zyz_from_matrix(rotation: np.ndarray) -> np.ndarray:
    """Return one ZYZ Euler-angle solution in radians."""
    cos_theta = float(np.clip(rotation[2, 2], -1.0, 1.0))
    theta = math.acos(cos_theta)
    sin_theta = math.sin(theta)

    if abs(sin_theta) < 1e-9:
        # At the singularity only a combination of phi and psi is observable.
        phi = math.atan2(rotation[1, 0], rotation[0, 0])
        psi = 0.0
    else:
        phi = math.atan2(rotation[1, 2], rotation[0, 2])
        psi = math.atan2(rotation[2, 1], -rotation[2, 0])

    return np.array([phi, theta, psi])


def angle_axis_from_matrix(rotation: np.ndarray) -> tuple[float, np.ndarray]:
    """Return the rotation angle in radians and a unit rotation axis."""
    cos_angle = float(np.clip((np.trace(rotation) - 1.0) / 2.0, -1.0, 1.0))
    angle = math.acos(cos_angle)

    if abs(angle) < 1e-9:
        return 0.0, np.array([1.0, 0.0, 0.0])

    if abs(math.pi - angle) < 1e-6:
        diagonal = np.maximum((np.diag(rotation) + 1.0) / 2.0, 0.0)
        axis = np.sqrt(diagonal)
        axis[0] = math.copysign(axis[0], rotation[2, 1] - rotation[1, 2])
        axis[1] = math.copysign(axis[1], rotation[0, 2] - rotation[2, 0])
        axis[2] = math.copysign(axis[2], rotation[1, 0] - rotation[0, 1])
    else:
        axis = np.array([
            rotation[2, 1] - rotation[1, 2],
            rotation[0, 2] - rotation[2, 0],
            rotation[1, 0] - rotation[0, 1],
        ]) / (2.0 * math.sin(angle))

    axis_norm = np.linalg.norm(axis)
    if axis_norm < 1e-12:
        return angle, np.array([1.0, 0.0, 0.0])
    return angle, axis / axis_norm
