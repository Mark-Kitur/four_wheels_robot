import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = "four_wheels_robot"
    urdf_file = 'model.urdf.xacro'

    urdf_path = os.path.join(
        get_package_share_directory(pkg_name),
        "urdf", urdf_file
    )
    config_file =os.path.join(
        get_package_share_directory(pkg_name),
        "config","wheels_controllers.yaml"
    )

    robot_description = xacro.process_file(urdf_path).toxml()

    # Robot State Publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{'robot_description': robot_description}]
    )

    joint_state_publisher_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output='screen'
    )
    # Gazebo
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory("ros_gz_sim"), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': '-r -v 4 empty.sdf'}.items()
    )

    # Spawn robot
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'four_wheels_robot', '-topic', 'robot_description'],
        output='screen',
        parameters=[{'x': 0.0, 'y': 0.0, 'z': 0.56}]
    )

    # Controller Manager + Controllers (much more reliable)
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{'robot_description': robot_description},config_file],
        output="screen",
    )

    # Load controllers via spawner (best practice)
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
    )

    velocity_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=['velocity_controller', '--controller-manager', '/controller_manager'],
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        output="screen"
    )

    # delayed_spawners = TimerAction(
    #         period=2.0,  # Increase if still failing
    #         actions=[
    #             joint_state_broadcaster_spawner,
    #             velocity_controller_spawner
    #         ]
    #     )
    ld = LaunchDescription([
        gz_sim,
        robot_state_publisher,
        spawn_entity,
        controller_manager,
        joint_state_broadcaster_spawner,
        velocity_controller_spawner,
        rviz,
        #joint_state_publisher_gui
    ])

    return ld