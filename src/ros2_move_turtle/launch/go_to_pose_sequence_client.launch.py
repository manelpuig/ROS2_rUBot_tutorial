from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    sequence_file = DeclareLaunchArgument(
        'sequence_file',
        default_value=PathJoinSubstitution([
            FindPackageShare('ros2_move_turtle'),
            'config',
            'turtle_pose_sequence.yaml',
        ]),
    )
    client = Node(
        package='ros2_move_turtle',
        executable='go_to_pose_sequence_client',
        output='screen',
        parameters=[{
            'sequence_file': LaunchConfiguration('sequence_file'),
        }],
    )
    return LaunchDescription([sequence_file, client])
