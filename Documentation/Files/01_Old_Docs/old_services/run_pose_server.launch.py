#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:

    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen',
    )

    run_pose_server_node = Node(
        package='ros2_move_turtle',
        executable='run_pose_server',
        name='run_pose_server',
        output='screen',
        parameters=[{
            'linear_gain': 1.0,
            'angular_gain': 4.0,
            'max_linear_speed': 1.5,
            'max_angular_speed': 2.0,
            'position_tolerance': 0.10,
            'angle_tolerance_deg': 2.0,
            'motion_timeout': 30.0,
        }],
    )

    delayed_server = TimerAction(
        period=5.0,
        actions=[run_pose_server_node],
    )

    return LaunchDescription([
        turtlesim_node,
        delayed_server,
    ])