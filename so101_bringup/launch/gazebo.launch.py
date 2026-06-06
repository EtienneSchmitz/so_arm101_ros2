"""Lance le SO-101 en simulation Gazebo Harmonic avec ros2_control.

Sequence : robot_state_publisher -> Gazebo -> spawn entite -> pont /clock
-> joint_state_broadcaster -> arm_controller + gripper_controller.

Verification :
    ros2 control list_controllers
    ros2 action send_goal /arm_controller/follow_joint_trajectory ...
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    desc_share = get_package_share_directory('so101_description')
    bringup_share = get_package_share_directory('so101_bringup')

    default_world = os.path.join(bringup_share, 'worlds', 'empty.sdf')
    default_controllers = os.path.join(bringup_share, 'config', 'ros2_controllers.yaml')
    default_model = os.path.join(desc_share, 'urdf', 'so101.urdf.xacro')

    world_arg = DeclareLaunchArgument(
        'world', default_value=default_world,
        description='Path to the Gazebo world (.sdf).')
    controllers_arg = DeclareLaunchArgument(
        'controllers_file', default_value=default_controllers,
        description='ros2_control controllers YAML loaded by gz_ros2_control.')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use the Gazebo (simulated) clock.')
    headless_arg = DeclareLaunchArgument(
        'headless', default_value='false',
        description='Run Gazebo server only (no GUI), useful for CI/tests.')

    # robot_description = xacro en mode gazebo, avec le chemin du YAML controllers.
    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'), ' ',
            LaunchConfiguration('model'),
            ' mode:=gazebo',
            ' controllers_file:=', LaunchConfiguration('controllers_file'),
        ]),
        value_type=str,
    )
    model_arg = DeclareLaunchArgument(
        'model', default_value=default_model,
        description='Path to the SO-101 Xacro.')

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
        }],
    )

    # Permet a Gazebo de resoudre les meshes package://so101_description/...
    set_resource_path = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH', os.path.dirname(desc_share))

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py',
            ])
        ),
        launch_arguments={
            'gz_args': [
                LaunchConfiguration('world'), ' -r -v4 ',
                PythonExpression(["'-s' if '",
                                  LaunchConfiguration('headless'),
                                  "' == 'true' else ''"]),
            ],
            'on_exit_shutdown': 'true',
        }.items(),
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/robot_description', '-name', 'so101', '-z', '0.0'],
        output='screen',
    )

    jsb_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster',
                   '--controller-manager', '/controller_manager',
                   '--controller-manager-timeout', '60'],
        output='screen',
    )
    arm_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_controller',
                   '--controller-manager', '/controller_manager',
                   '--controller-manager-timeout', '60'],
        output='screen',
    )
    gripper_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_controller',
                   '--controller-manager', '/controller_manager',
                   '--controller-manager-timeout', '60'],
        output='screen',
    )

    # Le controller_manager n'existe qu'apres le spawn du modele (plugin gz).
    load_jsb_after_spawn = RegisterEventHandler(
        OnProcessExit(target_action=spawn_entity, on_exit=[jsb_spawner]))
    load_controllers_after_jsb = RegisterEventHandler(
        OnProcessExit(target_action=jsb_spawner, on_exit=[arm_spawner, gripper_spawner]))

    return LaunchDescription([
        world_arg,
        controllers_arg,
        use_sim_time_arg,
        headless_arg,
        model_arg,
        set_resource_path,
        robot_state_publisher,
        gz_sim,
        clock_bridge,
        spawn_entity,
        load_jsb_after_spawn,
        load_controllers_after_jsb,
    ])
