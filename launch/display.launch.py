import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    pkg_name = "four_wheels_robot"
    urdf_file = 'model.urdf.xacro'

    urdf_path = os.path.join(
        get_package_share_directory(pkg_name),
        "urdf", urdf_file
    )

    robot_description = xacro.process_file(urdf_path).toxml()

    # Robot State Publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{'robot_description': robot_description}]
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher"
    )

    joint_state_publisher_gui=Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui"

    )

    # Gazebo
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory("ros_gz_sim"), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': '-r -v 4 empty.sdf'}.items()
    )

    # Spawn robot (FIXED: Moved x, y, z positions from parameters to arguments)
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'four_wheels_robot', 
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.56'
        ],
        output='screen'
    )

    # Load controllers via spawner
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=['joint_state_broadcaster'],
    )

    velocity_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=['velocity_controller'],
    )

    # Delayed spawners to allow Gazebo enough time to boot up and initialize the controller manager
    delayed_spawners = TimerAction(
        period=3.0,  
        actions=[
            joint_state_broadcaster_spawner,
            velocity_controller_spawner
        ]
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        output="screen"
    )
        # Bridge ROS 2 and Gazebo Clock (FIXES THE WARNING)
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )


    ld = LaunchDescription([
       # gz_sim,clock_bridge,
        robot_state_publisher,
        joint_state_publisher,
        # spawn_entity,
        # delayed_spawners,
        rviz,
    ])

    return ld
