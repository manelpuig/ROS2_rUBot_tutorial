from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    parameters = ['target_x', 'target_y', 'target_theta_deg',
                  'position_tolerance', 'angle_tolerance_deg']
    defaults = ['8.0', '3.0', '90.0', '0.10', '2.0']
    arguments = [DeclareLaunchArgument(name, default_value=value)
                 for name, value in zip(parameters, defaults)]
    return LaunchDescription(arguments + [
        Node(package='turtlesim', executable='turtlesim_node'),
        Node(
            package='ros2_move_turtle',
            executable='go_to_pose',
            output='screen',
            parameters=[{name: LaunchConfiguration(name) for name in parameters}],
        ),
    ])
