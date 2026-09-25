#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory(
        'ros2_move_turtle'
    )

    default_sequence_file = os.path.join(
        package_share,
        'config',
        'turtle_pose_sequence.yaml',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'sequence_file',
            default_value=default_sequence_file,
            description='YAML file containing the pose sequence',
        ),

        DeclareLaunchArgument(
            'service_timeout',
            default_value='10.0',
            description='Time to wait for the RunPose service',
        ),

        Node(
            package='ros2_move_turtle',
            executable='run_pose_sequence_client',
            name='run_pose_sequence_client',
            output='screen',
            parameters=[{
                'sequence_file': LaunchConfiguration(
                    'sequence_file'
                ),
                'service_timeout': LaunchConfiguration(
                    'service_timeout'
                ),
            }],
        ),
    ])