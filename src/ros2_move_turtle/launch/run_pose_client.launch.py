#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:

    target_x_arg = DeclareLaunchArgument(
        'target_x',
        default_value='8.0',
        description='Target x position',
    )

    target_y_arg = DeclareLaunchArgument(
        'target_y',
        default_value='3.0',
        description='Target y position',
    )

    target_theta_deg_arg = DeclareLaunchArgument(
        'target_theta_deg',
        default_value='90.0',
        description='Target orientation in degrees',
    )

    client_node = Node(
        package='ros2_move_turtle',
        executable='run_pose_client',
        name='run_pose_client',
        output='screen',
        parameters=[{
            'target_x': LaunchConfiguration('target_x'),
            'target_y': LaunchConfiguration('target_y'),
            'target_theta_deg': LaunchConfiguration(
                'target_theta_deg'
            ),
        }],
    )

    return LaunchDescription([
        target_x_arg,
        target_y_arg,
        target_theta_deg_arg,
        client_node,
    ])