#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
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
        description='Target final orientation in degrees',
    )

    position_tolerance_arg = DeclareLaunchArgument(
        'position_tolerance',
        default_value='0.10',
        description='Position tolerance',
    )

    angle_tolerance_deg_arg = DeclareLaunchArgument(
        'angle_tolerance_deg',
        default_value='2.0',
        description='Angular tolerance in degrees',
    )

    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen',
    )

    go_to_pose_node = Node(
        package='ros2_move_turtle',
        executable='go_to_pose',
        name='go_to_pose',
        output='screen',
        parameters=[{
            'target_x': LaunchConfiguration('target_x'),
            'target_y': LaunchConfiguration('target_y'),
            'target_theta_deg': LaunchConfiguration('target_theta_deg'),
            'position_tolerance': LaunchConfiguration('position_tolerance'),
            'angle_tolerance_deg': LaunchConfiguration('angle_tolerance_deg'),
        }],
    )

    delayed_go_to_pose = TimerAction(
        period=3.0,
        actions=[go_to_pose_node],
    )

    return LaunchDescription([
        target_x_arg,
        target_y_arg,
        target_theta_deg_arg,
        position_tolerance_arg,
        angle_tolerance_deg_arg,
        turtlesim_node,
        delayed_go_to_pose,
    ])