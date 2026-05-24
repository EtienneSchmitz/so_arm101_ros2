"""Visualise le SO-101 dans RViz avec sliders pour bouger les joints.

Lance: robot_state_publisher + joint_state_publisher_gui + rviz2.
Pas de ros2_control (joint_states_gui:=true cote xacro).
"""

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('so101_description')

    default_model = PathJoinSubstitution([pkg_share, 'urdf', 'so101.urdf.xacro'])
    default_rviz = PathJoinSubstitution([pkg_share, 'rviz', 'display.rviz'])

    model_arg = DeclareLaunchArgument(
        'model', default_value=default_model,
        description='Path to the SO-101 Xacro to load.'
    )
    rviz_arg = DeclareLaunchArgument(
        'rviz_config', default_value=default_rviz,
        description='Path to the RViz config file.'
    )

    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'), ' ',
            LaunchConfiguration('model'),
            ' joint_states_gui:=true',
        ]),
        value_type=str,
    )

    return LaunchDescription([
        model_arg,
        rviz_arg,
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', LaunchConfiguration('rviz_config')],
        ),
    ])
