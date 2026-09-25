# ROS 2 Tutorial — Distributed Robot Control with Services

## Objectives

In this exercise, you will implement and compare three ROS 2 programs for moving a Turtlesim robot to a target position and final orientation:

1. A direct closed-loop motion node.
2. A persistent motion server controlled by a client.
3. A high-level client that executes a sequence of motion steps defined in a YAML file.

The motion controller will:

- subscribe to `/turtle1/pose` to obtain the current turtle pose;
- calculate the distance and orientation errors;
- publish linear and angular velocity commands to `/turtle1/cmd_vel`;
- stop when the target position and final orientation are reached.

The exercise uses Python templates. The ROS 2 communication, node structure and auxiliary functions are already provided. You must complete the main parts of the motion controller and the sequence client.

This exercise also introduces the same high-level sequence execution pattern that will later be used to create a social movement with the UR5e robot.

---

## Why do we need a service?

Imagine that a student controls a robot from a laptop connected through Wi-Fi. The robot has its own computer, such as a Raspberry Pi or an industrial control PC.

If the complete control loop runs on the student computer, every velocity command depends on the network:

```text
Student PC
     │
     │ continuous velocity commands
     ▼
Robot
```

Possible problems include:

- Wi-Fi latency;
- network jitter;
- packet loss;
- variable communication delays;
- temporary loss of connection.

A client-server architecture separates the high-level request from the local robot controller:

```text
Student PC
High-level application

        │
        │ RunPose service request
        ▼

Robot computer
RunPose service server

        │
        ├── sensor subscribers
        ├── closed-loop controller
        └── actuator publisher

        ▼

Robot
```

The client specifies **what the robot must do**:

> Go to this pose.

The server decides **how the robot executes the motion**. The complete closed-loop controller runs close to the sensors and actuators.

---

## Packages

The workspace contains two packages:

```text
src/
├── turtle_interfaces
└── ros2_move_turtle
```

### `turtle_interfaces`

This package contains the custom service definition. Do not modify this package.

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

The interface can be inspected with:

```bash
ros2 interface show turtle_interfaces/srv/RunPose
```

### `ros2_move_turtle`

The exercise files are located in this Python package:

```text
ros2_move_turtle/
├── config/
│   └── turtle_pose_sequence.yaml
├── launch/
│   ├── go_to_pose.launch.py
│   ├── run_pose_server.launch.py
│   ├── run_pose_client.launch.py
│   └── run_pose_sequence_client.launch.py
├── ros2_move_turtle/
│   ├── go_to_pose_template.py
│   ├── run_pose_server_template.py
│   ├── run_pose_client.py
│   └── run_pose_sequence_client_template.py
├── package.xml
├── setup.cfg
└── setup.py
```

The following node is provided complete:

```text
run_pose_client.py
```

It sends one target pose to the `/run_pose` service.

The following templates contain incomplete sections marked with `TODO`:

```text
go_to_pose_template.py
run_pose_server_template.py
run_pose_sequence_client_template.py
```

Copy or rename them as:

```text
go_to_pose.py
run_pose_server.py
run_pose_sequence_client.py
```

---

# Part 1 — Complete the direct GoToPose controller

Start with:

```text
go_to_pose_template.py
```

The target pose is provided through ROS 2 parameters:

```text
target_x
target_y
target_theta_deg
```

The node uses the following controller states:

```text
MOVE_TO_POSITION
        │
        │ position reached
        ▼
ROTATE_TO_FINAL_ORIENTATION
        │
        │ final orientation reached
        ▼
IDLE
```

Complete these two functions:

```python
move_to_position()
rotate_to_final_orientation()
```

## Task 1.1 — Move to the target position

Complete `move_to_position()` so that it:

1. Calculates the distance to the target.
2. Calculates the desired heading.
3. Calculates and normalizes the heading error.
4. Generates proportional linear and angular velocities.
5. Limits both velocities to their configured maximum values.
6. Changes to the final rotation state when the position tolerance is reached.

The turtle should move and turn simultaneously towards the target position.

## Task 1.2 — Reach the final orientation

Complete `rotate_to_final_orientation()` so that it:

1. Calculates and normalizes the final orientation error.
2. Sets the linear velocity to zero.
3. Generates a proportional angular velocity.
4. Limits the angular velocity to its configured maximum value.
5. Stops the turtle when the angle tolerance is reached.

## Build and test

```bash
cd ~/ROS2_rUBot_tutorial

colcon build --packages-select \
  turtle_interfaces ros2_move_turtle \
  --symlink-install

source install/setup.bash
```

Run the direct controller:

```bash
ros2 launch ros2_move_turtle go_to_pose.launch.py \
  target_x:=2.0 \
  target_y:=8.0 \
  target_theta_deg:=-90.0
```

The node must stop the turtle and finish automatically after reaching the complete target pose.

---

# Part 2 — Complete the persistent RunPose server

Start with:

```text
run_pose_server_template.py
```

The template already contains:

- the `/run_pose` service;
- the pose subscriber;
- the velocity publisher;
- the controller timer;
- the controller state machine;
- the multithreaded executor;
- the service response and motion completion logic.

Complete the same controller functions used in Part 1:

```python
move_to_position()
rotate_to_final_orientation()
```

Reuse the controller logic implemented in `go_to_pose.py`.

The main difference is the source of the target pose:

| Program | Target source | Behaviour after one motion |
|---|---|---|
| `go_to_pose.py` | ROS 2 parameters | Finishes |
| `run_pose_server.py` | `RunPose` service request | Returns to `IDLE` and waits |

The service callback waits for the motion to finish. During this time, ROS 2 must continue processing pose messages and controller timer callbacks. The provided server therefore uses a `MultiThreadedExecutor` and a `ReentrantCallbackGroup`.

## Test the server

Terminal 1 — Start Turtlesim and the persistent server:

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash

ros2 launch ros2_move_turtle run_pose_server.launch.py
```

Terminal 2 — Send one target with the provided client:

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash

ros2 launch ros2_move_turtle run_pose_client.launch.py \
  target_x:=8.0 \
  target_y:=8.0 \
  target_theta_deg:=180.0
```

Send a second request without restarting the server:

```bash
ros2 launch ros2_move_turtle run_pose_client.launch.py \
  target_x:=2.0 \
  target_y:=8.0 \
  target_theta_deg:=-90.0
```

Verify that:

- each request produces one complete motion;
- the response reports whether the target was reached;
- the server remains active after completing a request;
- another client can send a new target without restarting the server.

You can also test the server directly:

```bash
ros2 service call \
  /run_pose \
  turtle_interfaces/srv/RunPose \
  "{target_x: 8.0, target_y: 3.0, target_theta_deg: 90.0}"
```

---

# Part 3 — Execute a sequence of YAML steps

The provided `run_pose_client.py` sends only one target pose. Start with:

```text
run_pose_sequence_client_template.py
```

Create a high-level client that loads several motion steps from:

```text
config/turtle_pose_sequence.yaml
```

Example:

```yaml
steps:
  - name: lower_left
    target_x: 2.0
    target_y: 2.0
    target_theta_deg: 0.0

  - name: upper_left
    target_x: 2.0
    target_y: 8.0
    target_theta_deg: 90.0

  - name: upper_right
    target_x: 8.0
    target_y: 8.0
    target_theta_deg: 180.0

  - name: lower_right
    target_x: 8.0
    target_y: 2.0
    target_theta_deg: -90.0
```

Each step contains:

- an optional descriptive `name`;
- the target position `target_x`;
- the target position `target_y`;
- the final orientation `target_theta_deg`.

## Differences from the single-pose client

| Single-pose client | Sequence client |
|---|---|
| Reads one pose from ROS 2 parameters | Reads a sequence from a YAML file |
| Creates one service request | Creates one request for every step |
| Waits for one response | Waits after every request |
| Finishes after one pose | Continues until all steps are complete |
| Does not validate a file | Validates the YAML structure and required fields |

## Student task

Complete the `TODO` sections so that the client:

1. Loads the YAML file.
2. Reads the list stored under `steps`.
3. Checks that the sequence is not empty.
4. Validates the required fields of every step.
5. Creates one `RunPose` request for each step.
6. Waits for the current motion to finish before sending the next request.
7. Stops the sequence if a service request fails.
8. Reports when the complete sequence has finished successfully.

The required execution order is:

```text
Load YAML steps
        │
        ▼
Send one step
        │
        ▼
Wait for the service response
        │
        ▼
Check the result
        │
        ├── failure ──► stop the sequence
        │
        └── success ─► send the next step
```

A new request must only be sent after the previous step has completed successfully.

## Test the sequence

Keep the server running in Terminal 1. In Terminal 2, run:

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash

ros2 launch ros2_move_turtle \
  run_pose_sequence_client.launch.py
```

The output must show:

- the index and name of every step;
- the requested target pose;
- the result returned by the server;
- a final successful sequence message.

---

# Comparison of the three programs

| Program | Target source | Number of motions | Controller location | Finishes after execution |
|---|---|---:|---|---|
| `go_to_pose.py` | ROS 2 parameters | One | Direct node | Yes |
| `run_pose_client.py` | ROS 2 parameters | One | Service server | Client: yes; server: no |
| `run_pose_sequence_client.py` | YAML file | Several | Service server | Client: yes; server: no |

The closed-loop controller is implemented in the direct node and the persistent server. The clients do not calculate velocity commands. They only specify what the robot must do.

---

# Topics, services and internal state

Topics are used for continuous information:

```text
/turtle1/pose
/turtle1/cmd_vel
```

The service is used for a high-level operation:

```text
/run_pose
```

A useful rule is:

```text
Topics continuously exchange robot data.

Services request a specific operation.
```

The client calls the service once for every motion step. The server then uses topics continuously while executing the local closed-loop controller.

---

# Expected results

Your implementation is correct when:

- `go_to_pose.py` reaches the requested position and orientation;
- the direct node stops the turtle and finishes automatically;
- `run_pose_server.py` executes the same closed-loop controller;
- the server returns a successful `RunPose` response;
- the server remains available after every motion;
- `run_pose_sequence_client.py` loads the YAML file correctly;
- the client sends the steps sequentially;
- a new step is not sent before the previous one finishes;
- the complete sequence finishes without restarting the server.

You can inspect the ROS 2 system with:

```bash
ros2 node list
ros2 topic list
ros2 service list
ros2 interface show turtle_interfaces/srv/RunPose
```

---

# Service limitations

`RunPose` is useful for introducing distributed robot control. However, a movement may take several seconds.

A ROS 2 Action would be more appropriate if the application required:

- continuous execution feedback;
- goal cancellation;
- explicit goal states;
- progress information.

The service is used here to keep the first distributed control architecture simple. The sequence client still teaches the important pattern of sending one request, waiting for completion and then sending the next request.

---

# Connection with the UR5e social robotics exercise

This exercise introduces the same high-level sequence pattern that will later be used to design a social movement with the UR5e:

```text
YAML motion definition
        │
        ▼
High-level sequence node
        │
        ▼
Execute one motion step
        │
        ▼
Wait for completion
        │
        ▼
Execute the next step
```

The robot interfaces are different:

| Turtlesim exercise | UR5e exercise |
|---|---|
| 2D pose: `x`, `y`, `theta` | Cartesian pose or joint target |
| `/run_pose` service | MoveIt 2 and trajectory execution |
| `/turtle1/pose` feedback | TF and `/joint_states` feedback |
| `/turtle1/cmd_vel` commands | Joint trajectory commands |
| YAML sequence of turtle poses | YAML sequence defining a social movement |

However, the high-level idea is the same:

- separate the motion definition from its execution;
- describe a behaviour as a sequence of named YAML steps;
- execute one step at a time;
- continue only after successful completion.

In the UR5e exercise, you will reuse this concept to define, simulate and execute a social robot movement.

---

# Learning outcomes

After completing this exercise, you should be able to:

- implement a closed-loop controller using publishers and subscribers;
- provide a target pose through parameters or a service request;
- explain the difference between a service client and a service server;
- reuse the same controller in direct and distributed architectures;
- explain why a robot controller should run close to its sensors and actuators;
- load and validate a sequence of named steps from a YAML file;
- execute service requests sequentially and handle failures;
- relate the Turtlesim sequence architecture to the later UR5e social robotics exercise.
