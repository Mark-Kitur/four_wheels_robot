ros2 topic pub /velocity_controller/cmd_vel geometry_msgs/msg/TwistStamped "{
  header: {stamp: {sec: 0, nanosec: 0}, frame_id: ''},
  twist: {
    linear: {x: 3.0, y: 0.0, z: 0.0},
    angular: {x: 0.0, y: 0.0, z: 5.0}
  }
}" -r 100
