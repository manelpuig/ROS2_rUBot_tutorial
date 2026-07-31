# ROS 2 Tutorial — Distributed Robot Control with Services

## Objective

In the previous exercise, you implemented a simple `GoToPose` node.

The node:

* subscribed to the current turtle pose;
* calculated the position and orientation errors;
* generated linear and angular velocity commands;
* stopped when the turtle reached the requested pose.

This exercise introduces a different software architecture.

The same motion controller will be executed by a persistent **robot server**, while another node will send the target pose using a ROS 2 Service.

The objective is to understand how ROS 2 Services can be used to separate:

* a high-level application running on a client computer;
* a closed-loop robot controller running close to the robot.

This architecture will later be used with the **rUBot mobile robot** and the **UR5e industrial robot**.

---

## Why do we need a Service?

Imagine the following situation:

* A student works from a laptop connected through WiFi.
* The robot has its own computer, such as a Raspberry Pi or an industrial control PC.
* The robot must execute a closed-loop controller using sensors and actuators.

A possible architecture would be:

```text
Student PC
     │
     │ continuous /cmd_vel messages
     ▼
Robot
```

In this case, the complete control loop depends on the network.

Possible problems include:

* WiFi latency;
* network jitter;
* packet losses;
* variable communication delays;
* temporary loss of connection.

If every velocity command must travel through the network, the robot may react slowly or unpredictably.

A more robust architecture separates the high-level command from the local robot controller:

```text
Student PC
High-level application

        │
        │ RunPose service request
        ▼

Robot controller
Service server

        │
        ├── Sensor subscribers
        ├── Closed-loop controller
        └── Actuator publisher

        ▼

Robot
```

The client only specifies **what the robot must do**:

> Go to this pose.

The server decides **how the robot executes the motion**.

The complete closed-loop controller runs close to the robot, where communication with sensors and actuators is fast and reliable.

---

## Examples used later in this course

### rUBot mobile robot

```text
Student PC
High-level application

        │
        │ Motion request
        ▼

Raspberry Pi
Robot computer

        │
        ├── Wheel encoders
        ├── IMU and odometry
        ├── Local controller
        └── Motor commands

        ▼

rUBot
```

The student computer sends high-level commands.

The Raspberry Pi executes the low-level robot control locally.

Some computationally demanding processes, such as SLAM or Navigation2, may still run on the student PC because the Raspberry Pi has limited computational resources.

---

### UR5e industrial robot

```text
Student PC
High-level application

        │
        │ RunPose service request
        ▼

Professor PC
Robot server

        │
        ├── MoveIt 2
        ├── Motion planning
        ├── Trajectory execution
        └── UR5e communication

        ▼

UR5e
```

The student computer sends a motion request.

Motion planning and trajectory execution run on the professor PC, which is connected to the UR5e through Ethernet.

This avoids executing critical robot communication through the student WiFi connection.

---

# Exercise overview

The exercise is divided into two parts.

## Part 1 — Direct GoToPose node

The first implementation uses a single node:

```text
go_to_pose.py
```

The target pose is provided through ROS 2 parameters.

```text
Target parameters
        │
        ▼
go_to_pose
        │
        ├── subscribes to /turtle1/pose
        ├── executes the closed-loop controller
        └── publishes to /turtle1/cmd_vel
        ▼
turtlesim
```

Example:

```bash
ros2 launch ros2_move_turtle go_to_pose.launch.py \
  target_x:=2.0 \
  target_y:=8.0 \
  target_theta_deg:=-90.0
```

This node executes one motion and finishes when the target pose is reached.

---

## Part 2 — Distributed RunPose service

The motion controller is transformed into a persistent service server.

Two nodes are used:

```text
run_pose_server.py
run_pose_client.py
```

The client sends the target pose.

The server executes the same closed-loop motion controller used in `go_to_pose.py`.

```text
run_pose_client
        │
        │ RunPose request
        ▼
run_pose_server
        │
        ├── subscribes to /turtle1/pose
        ├── executes the closed-loop controller
        └── publishes to /turtle1/cmd_vel
        ▼
turtlesim
```

The server remains active after completing the motion and can receive additional requests.

---

# Packages

The workspace contains two packages:

```text
src/
├── turtle_interfaces
└── ros2_move_turtle
```

---

## `turtle_interfaces`

The teaching staff provides the interface package:

```text
turtle_interfaces
```

This package contains the custom service definition:

```text
srv/RunPose.srv
```

The package uses:

```text
ament_cmake
```

Custom ROS 2 interfaces are generated during compilation using `rosidl_generate_interfaces()`.

Students do not need to modify this package.

---

## `ros2_move_turtle`

Students work inside the Python package:

```text
ros2_move_turtle
```

The final package contains:

```text
ros2_move_turtle/
├── launch/
│   ├── go_to_pose.launch.py
│   ├── run_pose_server.launch.py
│   └── run_pose_client.launch.py
├── ros2_move_turtle/
│   ├── go_to_pose.py
│   ├── run_pose_server.py
│   └── run_pose_client.py
├── package.xml
├── setup.cfg
└── setup.py
```

This package uses:

```text
ament_python
```

---

# RunPose service definition

The service is defined in:

```text
turtle_interfaces/srv/RunPose.srv
```

```text
float32 target_x
float32 target_y
float32 target_theta_deg
---
bool success
string message
```

The request contains:

* target position `x`;
* target position `y`;
* final target orientation in degrees.

The response contains:

* whether the motion completed successfully;
* a message describing the result.

The interface can be inspected with:

```bash
ros2 interface show turtle_interfaces/srv/RunPose
```

---

# Node 1 — `go_to_pose.py`

## Purpose

`go_to_pose.py` is the first implementation of the closed-loop motion controller.

It receives the target pose through ROS 2 parameters.

It executes one motion and then finishes.

## Inputs

ROS 2 parameters:

```text
target_x
target_y
target_theta_deg
```

Controller parameters:

```text
linear_gain
angular_gain
max_linear_speed
max_angular_speed
position_tolerance
angle_tolerance_deg
```

## ROS 2 communication

Subscriber:

```text
/turtle1/pose
```

Message type:

```text
turtlesim/msg/Pose
```

Publisher:

```text
/turtle1/cmd_vel
```

Message type:

```text
geometry_msgs/msg/Twist
```

## Controller structure

The controller uses two motion states:

```text
MOVE_TO_POSITION
        │
        ▼
ROTATE_TO_FINAL_ORIENTATION
        │
        ▼
IDLE
```

### Move to position

The node calculates:

```text
distance error
heading error
```

The linear velocity is proportional to the distance error.

The angular velocity is proportional to the heading error.

The turtle moves and turns simultaneously towards the target position.

### Rotate to final orientation

When the target position is reached, linear velocity becomes zero.

The turtle rotates until it reaches the requested final orientation.

## Lifecycle

```text
Read target parameters
        │
        ▼
Start motion
        │
        ▼
Execute closed-loop controller
        │
        ▼
Reach target pose
        │
        ▼
Stop the turtle
        │
        ▼
Finish the node
```

---

# Node 2 — `run_pose_server.py`

## Purpose

`run_pose_server.py` contains the robot-side controller.

It provides the service:

```text
/run_pose
```

The server receives target poses from clients and executes the complete closed-loop motion locally.

Unlike `go_to_pose.py`, the server does not finish after completing one motion.

It returns to the idle state and waits for another request.

## ROS 2 communication

Service server:

```text
/run_pose
```

Service type:

```text
turtle_interfaces/srv/RunPose
```

Subscriber:

```text
/turtle1/pose
```

Publisher:

```text
/turtle1/cmd_vel
```

## Service execution

When a request is received, the server:

1. Reads the requested target pose.
2. Converts the target angle from degrees to radians.
3. Initializes the motion state.
4. Executes the closed-loop controller.
5. Stops the turtle when the pose is reached.
6. Returns the service response.
7. Waits for the next request.

```text
Wait for request
        │
        ▼
Start motion
        │
        ▼
Execute controller
        │
        ▼
Finish motion
        │
        ▼
Return response
        │
        ▼
Wait for next request
```

## Reused controller functions

The server reuses almost the same functions as `go_to_pose.py`:

```text
start_motion()
normalize_angle()
distance_to_target()
target_heading()
control_loop()
move_to_position()
rotate_to_final_orientation()
publish_velocity()
stop_turtle()
finish_motion()
```

The main difference is the source of the target pose.

In `go_to_pose.py`:

```text
ROS 2 parameters
        │
        ▼
start_motion()
```

In `run_pose_server.py`:

```text
RunPose request
        │
        ▼
start_motion()
```

## Multithreaded execution

The service callback waits until the motion is completed.

During this time, ROS 2 must continue processing:

* turtle pose messages;
* the controller timer;
* velocity publications.

For this reason, the server uses:

```text
MultiThreadedExecutor
ReentrantCallbackGroup
```

This allows the service callback, subscriber callback and timer callback to run concurrently.

---

# Node 3 — `run_pose_client.py`

## Purpose

`run_pose_client.py` represents the high-level application.

It does not calculate velocity commands.

It only specifies the requested target pose and sends it to the server.

## Inputs

ROS 2 parameters:

```text
target_x
target_y
target_theta_deg
```

## Client operation

The client:

1. Creates a client for `/run_pose`.
2. Waits until the service is available.
3. Creates a `RunPose` request.
4. Sends the target pose.
5. Waits for the response.
6. Prints the result.
7. Finishes.

```text
Read target parameters
        │
        ▼
Wait for /run_pose
        │
        ▼
Send request
        │
        ▼
Wait for response
        │
        ▼
Print result
        │
        ▼
Finish client
```

The client does not subscribe to the turtle pose and does not publish velocity commands.

This is an important architectural separation:

```text
Client
specifies what the robot must do

Server
decides how the robot executes it
```

---

# Complete ROS 2 architecture

```text
                    RunPose request
                    RunPose response
run_pose_client  ─────────────────────►  run_pose_server
                                              │
                                              │ subscribes
                                              ▼
                                       /turtle1/pose
                                              ▲
                                              │
                                           turtlesim
                                              ▲
                                              │
                                              │ publishes
                                              │
                                      /turtle1/cmd_vel
```

A simplified representation is:

```text
run_pose_client
        │
        │ high-level target pose
        ▼
run_pose_server
        │
        │ closed-loop velocity control
        ▼
turtlesim
```

---

# Running the direct GoToPose node

Compile and source the workspace:

```bash
cd ~/ROS2_rUBot_tutorial

colcon build --packages-select \
  turtle_interfaces \
  ros2_move_turtle

source install/setup.bash
```

Run:

```bash
ros2 launch ros2_move_turtle go_to_pose.launch.py \
  target_x:=2.0 \
  target_y:=8.0 \
  target_theta_deg:=-90.0
```

The launch finishes automatically when the target pose is reached.

---

# Running the service architecture

## Terminal 1 — Start the server

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash

ros2 launch ros2_move_turtle run_pose_server.launch.py
```

This starts:

* `turtlesim_node`;
* `run_pose_server`.

The server remains active.

---

## Terminal 2 — Send a request

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash

ros2 launch ros2_move_turtle run_pose_client.launch.py \
  target_x:=2.0 \
  target_y:=8.0 \
  target_theta_deg:=-90.0
```

The client finishes after receiving the response.

The server remains available.

A second request can then be sent:

```bash
ros2 launch ros2_move_turtle run_pose_client.launch.py \
  target_x:=8.0 \
  target_y:=8.0 \
  target_theta_deg:=180.0
```

---

# Calling the service from the command line

The server can also be tested without the Python client:

```bash
ros2 service call \
  /run_pose \
  turtle_interfaces/srv/RunPose \
  "{
    target_x: 8.0,
    target_y: 3.0,
    target_theta_deg: 90.0
  }"
```

Expected response:

```text
success: true
message: "Target pose reached successfully..."
```

---

# Comparing the two implementations

## Direct node

```text
Target parameters
        │
        ▼
go_to_pose
        │
        ├── closed-loop controller
        └── velocity commands
        ▼
turtlesim
```

Characteristics:

* one node;
* one target pose;
* one motion;
* the node finishes after execution.

---

## Client-server architecture

```text
Target parameters
        │
        ▼
run_pose_client
        │
        │ RunPose request
        ▼
run_pose_server
        │
        ├── closed-loop controller
        └── velocity commands
        ▼
turtlesim
```

Characteristics:

* separate high-level client and robot server;
* target transmitted through a service;
* controller remains close to the robot;
* server accepts multiple requests;
* client finishes after receiving the result.

---

# Topics and Services

Topics are used for continuous information:

```text
/turtle1/pose
/turtle1/cmd_vel
```

The service is used for a high-level request:

```text
/run_pose
```

A useful rule is:

```text
Topics continuously exchange robot data.

Services request a specific operation.
```

In this exercise:

```text
Pose sensor data        → Topic
Velocity commands       → Topic
Go to a target pose     → Service
```

---

# Service limitations

The `RunPose` service is useful for introducing distributed robot control.

However, the movement may take several seconds.

A ROS 2 Action would be more appropriate if the application required:

* continuous execution feedback;
* goal cancellation;
* explicit goal states;
* progress information.

The service architecture is used here because it is simple and directly related to the later UR5e laboratory architecture.

---

# Learning objectives

After completing this exercise, students should understand:

* how a closed-loop robot controller uses publishers and subscribers;
* how a target pose can be provided through parameters or through a service;
* the difference between a service client and a service server;
* why robot controllers should often execute close to the robot;
* why continuous low-level commands should not depend on a WiFi connection;
* how the same controller can be reused in different ROS 2 architectures;
* why the client specifies the task while the server executes the controller;
* how the architecture relates to the later rUBot and UR5e laboratory sessions.
 in the **rUBot** and **UR5e** laboratory sessions.