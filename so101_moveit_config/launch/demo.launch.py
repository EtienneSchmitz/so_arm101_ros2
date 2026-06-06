"""Demo MoveIt 2 du SO-101 : Gazebo Ionic + MoveIt + RViz.

Lance :
  - so101_bringup/gazebo.launch.py  -> Gazebo + ros2_control + spawners
  - move_group                      -> planificateur MoveIt
  - RViz MoveIt                     -> panneau MotionPlanning

Note locale : on force LC_NUMERIC=C.UTF-8 pour eviter une regression MoveIt 2
Kilted qui serialise les doubles selon la locale system. En locale fr_FR,
"3.14" devient "3,14" et le panel RViz MotionPlanning leve une exception
"loadRobotModel: setting double to string". Cf moveit2 issue #1049.
"""

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import SetParameter


def generate_launch_description():
    bringup_share = get_package_share_directory('so101_bringup')
    moveit_share = get_package_share_directory('so101_moveit_config')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([bringup_share, 'launch', 'gazebo.launch.py'])
        ),
    )
    move_group = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([moveit_share, 'launch', 'move_group.launch.py'])
        ),
    )
    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([moveit_share, 'launch', 'moveit_rviz.launch.py'])
        ),
    )

    return LaunchDescription([
        SetEnvironmentVariable('LC_NUMERIC', 'C.UTF-8'),
        SetParameter(name='use_sim_time', value=True),
        gazebo,
        move_group,
        rviz,
    ])
