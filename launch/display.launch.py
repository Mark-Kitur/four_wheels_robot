import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time", default=True)
    pkg_name = "four_wheels_robot"
    urdf_file = 'model.urdf.xacro'

    pkg_share_dir = get_package_share_directory(pkg_name)

    urdf_path = os.path.join(pkg_share_dir, "urdf", urdf_file)
    robot_description = xacro.process_file(urdf_path).toxml()

    # Robot State Publisher (FIXED: Added use_sim_time parameter)
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time
        }]
    )

    joint_state_publisher_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="screen"
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        output="log",
        parameters=[{"use_sim_time":True}]
    )

    # Gazebo
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory("ros_gz_sim"), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': '-r -v 4 empty.sdf'}.items()
    )

    imu_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['imu_sensor_broadcaster'],
    )
    # Spawn robot
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

    delayed_spawners = TimerAction(
        period=3.0,  
        actions=[
            joint_state_broadcaster_spawner,
            velocity_controller_spawner,imu_broadcaster_spawner
        ]
    )


    # (FIXED: Corrected directional brackets for clock bridge)
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/imu@sensor_msgs/msg/Imu@gz.msgs.IMU' 
        ],
        output='screen'
    )

    robot_localization_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            os.path.join(pkg_share_dir, 'config', 'ekf.yaml'),
            {'use_sim_time': use_sim_time}
        ]
    )

    ld = LaunchDescription([
        gz_sim,
        clock_bridge,
        robot_state_publisher,
        # joint_state_publisher_gui,
        rviz,
        spawn_entity,
        delayed_spawners,
        robot_localization_node
    ])

    return ld
