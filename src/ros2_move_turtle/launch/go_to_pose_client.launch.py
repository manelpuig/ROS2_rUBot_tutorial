from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    arguments = [
        DeclareLaunchArgument('target_x', default_value='8.0'),
        DeclareLaunchArgument('target_y', default_value='3.0'),
        DeclareLaunchArgument('target_theta_deg', default_value='90.0'),
    ]
    client = Node(
        package='ros2_move_turtle',
        executable='go_to_pose_client',
        output='screen',
        parameters=[{
            'target_x': LaunchConfiguration('target_x'),
            'target_y': LaunchConfiguration('target_y'),
            'target_theta_deg': LaunchConfiguration('target_theta_deg'),
        }],
    )
    return LaunchDescription(arguments + [client])
