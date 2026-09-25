from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            output='screen',
        ),
        Node(
            package='ros2_move_turtle',
            executable='go_to_pose_server',
            output='screen',
        )
    ])
