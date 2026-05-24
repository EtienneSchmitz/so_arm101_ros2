# so_arm101_ros2

Packages ROS 2 (Kilted) pour le bras **SO-101** utilisé au Bootcamp Robotique
Perpignan 2026 — Jour 3 (Manipulation).

Inspiré de [nimiCurtis/so101_ros2](https://github.com/nimiCurtis/so101_ros2).

## Packages

| Package | Rôle |
| --- | --- |
| `so101_description` | URDF Xacro + meshes + RViz |
| `so101_bringup` | Launchers (display + sim Gazebo) + config ros2_control |
| `so101_moveit_config` | Configuration MoveIt 2 |

## Quickstart

```bash
cd ~/ros2_bootcamp_ws
colcon build
source install/setup.bash

# Visualiser le bras dans RViz (sliders pour bouger les joints)
ros2 launch so101_bringup display.launch.py

# Lancer la simulation Gazebo Harmonic + ros2_control
ros2 launch so101_bringup so101_sim.launch.py

# Démo MoveIt 2 (planification + exécution sim)
ros2 launch so101_moveit_config demo.launch.py
```

## Licence

MIT — voir [LICENSE](LICENSE).
