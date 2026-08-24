# pose_tf2 — Exercise 4

This ROS 2 Humble package represents the Exercise 4 `Target B` pose with TF2
and displays an asymmetric target object in RViz2.

The transform is:

```text
ur5e_base
    └── target_b
```

The default target pose is:

```text
Translation [m] = [0.350, -0.350, 0.170]
RPY [deg]       = [135.0, 0.0, 60.0]
```

## Build and run

From the workspace root:

```bash
colcon build --packages-select pose_tf2 --symlink-install
source install/setup.bash
ros2 launch pose_tf2 exercise4.launch.py
```

The launch file starts:

- the Exercise 4 TF2 broadcaster;
- `robot_state_publisher` with `urdf/target_pose.urdf`;
- RViz2 with the Grid, TF and RobotModel displays already configured.

## Verify the result

```bash
ros2 run tf2_ros tf2_echo ur5e_base target_b
ros2 run tf2_tools view_frames
```

Expected ROS quaternion order `[x, y, z, w]`:

```text
[0.800103, 0.461940, 0.191342, 0.331414]
```

## Change the pose

The launch arguments use metres and degrees:

```bash
ros2 launch pose_tf2 exercise4.launch.py \
  x:=0.50 y:=-0.20 z:=0.30 \
  roll_deg:=90.0 pitch_deg:=30.0 yaw_deg:=45.0
```

The solution node reads the parameters for every publication, so they can also
be changed while the node is running:

```bash
ros2 param set /exercise4_rpy_broadcaster pitch_deg 45.0
```

## Student template

Launch the template instead of the completed solution:

```bash
ros2 launch pose_tf2 exercise4.launch.py \
  exercise_node:=exercise4_rpy_template
```

Complete the `TODO` sections in
`pose_tf2/exercise4_rpy_template.py`. The initial template publishes the correct
translation but uses the identity quaternion until the conversion is completed.

## Orientation convention

The package uses fixed-axis XYZ roll, pitch and yaw:

```text
R = Rz(yaw) @ Ry(pitch) @ Rx(roll)
```

Angles received by the launch file are in degrees. TF2 messages use radians for
the conversion and store the final orientation as a normalized quaternion in
ROS order `[x, y, z, w]`.
