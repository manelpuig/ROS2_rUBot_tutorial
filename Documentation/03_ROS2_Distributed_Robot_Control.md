# ROS 2 Tutorial — Distributed Robot Control with Services

## Learning objectives

This is a first guided introduction to distributed robot control in ROS 2. The
goal is not to program a complete controller from scratch, but to understand
how its parts communicate.

After this activity, you should be able to:

- identify a ROS 2 node, topic, service and parameter;
- explain the difference between a service client and a service server;
- identify the request and response fields of a service;
- explain why the client specifies **what** the robot must do while the server
  decides **how** to do it;
- make a small modification to a server and verify its behaviour.

![](./Images/02_ROS2_tutorial/02_move_turtle.png)

> ROS 2 node names are often similar to the names of their Python files.

---

# Part 1 — From direct to distributed control

## 1. Build the workspace

Open a terminal:

```bash
cd ~/ROS2_rUBot_tutorial

colcon build --packages-select \
  turtle_interfaces \
  ros2_move_turtle \
  --symlink-install

source install/setup.bash
```

## 2. Run the direct controller

Before introducing a service, consider the most direct solution. The package
contains `go_to_pose.py`, a node that receives a target through parameters and
executes the complete closed-loop controller:

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

It can be run with:

```bash
ros2 launch ros2_move_turtle go_to_pose.launch.py \
  target_x:=2.0 \
  target_y:=8.0 \
  target_theta_deg:=-90.0
```

Observe how this single controller node receives the target and moves the
turtle. When the target has been reached, stop the launch with `Ctrl+C` before
continuing with Part 2.

This architecture is simple and works well when the program and the robot are
on the same computer. However, consider a real robot controlled from a student
laptop through Wi-Fi:

```text
Student laptop
Closed-loop controller
      │
      │  continuous velocity commands over Wi-Fi
      ▼
Robot
```

The controller needs a continuous cycle:

```text
Read sensors → calculate error → send command → read sensors again
```

If this complete loop crosses the network, every controller iteration can be
affected by:

- Wi-Fi latency;
- network jitter;
- packet loss;
- variable communication delays;
- a temporary loss of connection.

For a real robot, the closed-loop controller should normally run close to its
sensors and actuators. The student computer should only send a high-level
request:

```text
Student laptop
Service client
      │
      │  one high-level request: Go to this pose
      ▼
Robot computer
Service server and local closed-loop controller
      │
      ├── reads sensors locally
      └── commands actuators locally
      ▼
Robot
```

This is why the second architecture implements the `/run_pose` service. The
client specifies **what the robot must do**, and the server decides **how the
robot executes it**.

The two architectures can be compared as follows:

| Direct node | Client-server architecture |
|---|---|
| Target comes directly from parameters | Target is sent in a service request |
| High-level command and controller are in one node | Client and controller are separate nodes |
| Node finishes after one movement | Server remains available |
| Suitable for local execution | Client and server can run on different computers |

The closed-loop controller can be the same in both cases. What changes is the
software architecture and the source of the target pose.

---

# Part 2 — Guided demonstration

Now run the distributed system and observe its behaviour. The client and
server code will be examined afterwards.

## 1. Start Turtlesim and the server

Terminal 1:

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash

ros2 launch ros2_move_turtle run_pose_server.launch.py
```

This launch file starts:

- the Turtlesim simulator;
- the persistent `run_pose_server` node.

Leave this terminal running.

## 2. Inspect the ROS 2 system

Open Terminal 2 and source the workspace:

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash
```

List the active nodes, topics and services:

```bash
ros2 node list
ros2 topic list
ros2 service list
```

Find the type used by `/run_pose` and inspect its interface:

```bash
ros2 service type /run_pose
ros2 interface show turtle_interfaces/srv/RunPose
```

The interface is:

```text
float32 target_x
float32 target_y
float32 target_theta_deg
---
bool success
string message
```

The fields above `---` form the request. The fields below it form the
response.

## 3. Send the first request

The service can be called directly from the terminal:

```bash
ros2 service call \
  /run_pose \
  turtle_interfaces/srv/RunPose \
  "{target_x: 2.0, target_y: 8.0, target_theta_deg: -90.0}"
```

Before pressing Enter, predict:

- where the turtle will move;
- what its final orientation will be;
- what the service response will contain.

The command waits while the server moves the turtle. When the target is
reached, the server returns a response similar to:

```text
success: true
message: "Target pose reached successfully."
```

## 4. Send a second request with the Python client

Without restarting Terminal 1, run:

```bash
ros2 launch ros2_move_turtle run_pose_client.launch.py \
  target_x:=8.0 \
  target_y:=3.0 \
  target_theta_deg:=90.0
```

Observe that:

- the client sends one request and finishes after receiving the response;
- the server executes the movement;
- the server remains active and can accept another request.

At this point, the important observation is:

```text
The client finishes.
The server remains active.
```

---

# Part 3 — Understanding the architecture

The complete system can be represented as:

```text
run_pose_client
        │
        │  RunPose request and response
        ▼
run_pose_server
        │
        ├── subscribes to /turtle1/pose
        ├── executes the closed-loop controller
        └── publishes to /turtle1/cmd_vel
        │
        ▼
turtlesim
```

The three nodes have different responsibilities:

| Node | Responsibility |
|---|---|
| `run_pose_client` | Specifies the target pose |
| `run_pose_server` | Receives the request and executes the controller |
| `turtlesim` | Simulates the robot and its motion |

## Topics, services and parameters

| ROS 2 concept | Example | Purpose |
|---|---|---|
| Topic | `/turtle1/pose` | Continuous pose information |
| Topic | `/turtle1/cmd_vel` | Continuous velocity commands |
| Service | `/run_pose` | One high-level movement request and its result |
| Parameters | `target_x`, `target_y`, `target_theta_deg` | Configure the client request |

A useful rule is:

```text
Topics continuously exchange robot data.
Services request a specific operation and return a result.
```

# Part 4 — How the client is constructed

The client is implemented in:

```text
src/ros2_move_turtle/ros2_move_turtle/run_pose_client.py
```

It is useful to study the client before the server because it has only one
responsibility: send one target pose and wait for the result.

## 1. Read the target parameters

The target is configured using ROS 2 parameters:

```python
self.declare_parameter('target_x', 8.0)
self.declare_parameter('target_y', 3.0)
self.declare_parameter('target_theta_deg', 90.0)
```

The launch arguments used in Part 1 change these values without editing the
Python program.

## 2. Create the service client

```python
self.client = self.create_client(
    RunPose,
    '/run_pose',
)
```

The client must use the same service type and service name as the server.

## 3. Create the request

```python
request = RunPose.Request()
request.target_x = self.target_x
request.target_y = self.target_y
request.target_theta_deg = self.target_theta_deg
```

These three fields correspond to the request section of `RunPose.srv`.

## 4. Send the request

```python
future = self.client.call_async(request)
```

The result is represented by a `future` because the robot has not completed
the movement when the request is sent. The client waits until the server
returns the response and then reads:

```python
response.success
response.message
```

The client does not subscribe to `/turtle1/pose` and does not publish velocity
commands. Those are server responsibilities.

---

# Part 5 — How the server is constructed

The server is implemented in:

```text
src/ros2_move_turtle/ros2_move_turtle/run_pose_server.py
```

It contains the robot-side controller and remains active after each request.

## 1. ROS 2 communication

The server creates a publisher for velocity commands:

```python
self.cmd_vel_publisher = self.create_publisher(
    Twist,
    '/turtle1/cmd_vel',
    10,
)
```

It subscribes to the current turtle pose:

```python
self.pose_subscriber = self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.pose_callback,
    10,
    callback_group=self.callback_group,
)
```

It also creates the service:

```python
self.run_pose_service = self.create_service(
    RunPose,
    '/run_pose',
    self.run_pose_callback,
    callback_group=self.callback_group,
)
```

## 2. Receive a request

When the client sends a request, ROS 2 executes:

```python
run_pose_callback(request, response)
```

The callback reads:

```python
request.target_x
request.target_y
request.target_theta_deg
```

and passes them to `start_motion()`.

## 3. Execute the controller

The controller first moves towards the target position and then reaches the
requested final orientation:

```text
MOVE_TO_POSITION
        │
        │  position reached
        ▼
ROTATE_TO_FINAL_ORIENTATION
        │
        │  final orientation reached
        ▼
IDLE
```

While moving, the server continuously:

1. receives the current pose from `/turtle1/pose`;
2. calculates the distance and angle errors;
3. publishes velocity commands to `/turtle1/cmd_vel`;
4. checks whether the target has been reached.

## 4. Return the response

When the movement finishes, the server assigns:

```python
response.success
response.message
```

The response is returned to the client, but the server returns to `IDLE` and
waits for another request.

## Why does the server use a multithreaded executor?

The service callback waits for the movement to finish. During that time, the
server must still receive pose messages and execute the controller timer.

For this reason, the provided implementation uses:

```text
MultiThreadedExecutor
ReentrantCallbackGroup
```

For this first activity, it is enough to understand their purpose: they allow
the service, subscriber and timer callbacks to continue working while a motion
request is active.

---

# Part 6 — Student activities

Work in pairs. Record short answers; one or two sentences are enough unless a
code modification is requested.

## Activity A — Predict and observe

With the server running, send these two targets one after another:

```bash
ros2 launch ros2_move_turtle run_pose_client.launch.py \
  target_x:=2.0 \
  target_y:=8.0 \
  target_theta_deg:=-90.0
```

```bash
ros2 launch ros2_move_turtle run_pose_client.launch.py \
  target_x:=8.0 \
  target_y:=3.0 \
  target_theta_deg:=90.0
```

Before each request, write down:

1. the expected final position;
2. the expected final orientation;
3. which node you expect to finish;
4. which node you expect to remain active.

After each request, compare the prediction with the observed result.

## Activity B — Change a controller parameter

Open:

```text
src/ros2_move_turtle/launch/run_pose_server.launch.py
```

Locate:

```python
'max_linear_speed': 1.5,
```

Perform the following experiment:

1. Run a target motion with the original value `1.5` and observe its speed.
2. Stop the launch with `Ctrl+C`.
3. Change the value to `0.5`.
4. Start the server launch again. Turtlesim will return to its initial state.
5. Send the same target and compare the movement.
6. Restore the original value `1.5` when the experiment is finished.

Answer:

1. Did the target position change?
2. Did the movement time change?
3. Was it necessary to modify the client?
4. Does this parameter describe **what** to do or **how** to do it?

## Activity C — Validate service requests

A robot server should not blindly execute every request. Modify
`run_pose_server.py` so that it only accepts targets inside this working area:

```text
1.0 <= target_x <= 10.0
1.0 <= target_y <= 10.0
```

Add the validation inside `run_pose_callback()`, before `start_motion()` is
called.

If the target is outside the working area, the server must:

- not start the movement;
- set `response.success` to `False`;
- set `response.message` to `Target outside the workspace`;
- return the response immediately;
- remain available for a new valid request.

The required logic is:

```text
Receive request
      │
      ▼
Is x and y inside the working area?
      │
      ├── no  ──► return a failure response
      │
      └── yes ──► start the movement
```

Test the modification with one valid request:

```bash
ros2 service call \
  /run_pose \
  turtle_interfaces/srv/RunPose \
  "{target_x: 8.0, target_y: 3.0, target_theta_deg: 90.0}"
```

Expected result:

```text
success: true
```

Then test one invalid request:

```bash
ros2 service call \
  /run_pose \
  turtle_interfaces/srv/RunPose \
  "{target_x: 20.0, target_y: 3.0, target_theta_deg: 90.0}"
```

Expected result:

```text
success: false
message: "Target outside the workspace"
```

Verify that the turtle does not move after the invalid request and that a new
valid request is still accepted.

---

# Part 7 — Short conceptual questions

Answer each question in one or two sentences.

1. What is the difference between a topic and a service?
2. What information does the client send to the server?
3. What information does the server return to the client?
4. Which node publishes to `/turtle1/cmd_vel`?
5. Which node subscribes to `/turtle1/pose`?
6. Why does the server remain active after completing a movement?
7. Why does the client not need to subscribe to `/turtle1/pose`?
8. If `max_linear_speed` is changed, are we changing what the robot must do or
   how it does it?
9. Why is it useful to validate a request in the server?
10. Why should a closed-loop controller normally run close to the robot's
    sensors and actuators?

---

# Service limitations

`RunPose` is useful for introducing distributed robot control. However, a
movement may take several seconds.

A ROS 2 Action would be more appropriate if the application required:

- continuous progress feedback;
- goal cancellation;
- explicit goal states;
- progress information during execution.

The service is used here because its request-response model makes the first
distributed architecture easier to understand.

---

# Connection with the real robots

The same separation will be used later with the rUBot and UR5e robots.

For the rUBot, a student laptop can send a high-level command while the
Raspberry Pi executes the local controller using odometry and motor commands.

For the UR5e, a student application can send a motion request while the robot
computer executes motion planning, trajectory execution and communication
with the industrial robot.

In all cases, the central idea is the same:

```text
Client: what the robot must do
Server: how the robot executes it
```

---

# Optional extension — Executing a pose sequence

> This extension does not form part of the student activity. It is included
> only to show how the same service can be used by a higher-level application.

The client used in the activity sends one target pose and then finishes. A
different client can reuse the same `/run_pose` service to execute several
motions in order.

The sequence is defined in:

```text
src/ros2_move_turtle/config/turtle_pose_sequence.yaml
```

Each step contains a descriptive name and one target pose:

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
```

The sequence client follows this process:

```text
Load the YAML file
        │
        ▼
Send one RunPose request
        │
        ▼
Wait for the server response
        │
        ├── failure ──► stop the sequence
        │
        └── success ─► send the next step
```

It does not publish velocity commands or execute the controller. It only
coordinates several high-level requests. The same `run_pose_server` used in
the main activity executes every movement.

## Running the sequence

First, keep the server running in Terminal 1:

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash

ros2 launch ros2_move_turtle run_pose_server.launch.py
```

Then run the sequence client in Terminal 2:

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash

ros2 launch ros2_move_turtle \
  run_pose_sequence_client.launch.py
```

The client loads the default YAML file, sends the first pose and waits until
the server reports success. It then continues with the following pose. The
sequence finishes when all the steps have completed successfully.

A different YAML file can be selected with the `sequence_file` launch
argument:

```bash
ros2 launch ros2_move_turtle \
  run_pose_sequence_client.launch.py \
  sequence_file:=/absolute/path/to/my_sequence.yaml
```

This illustrates an important benefit of the service architecture: the robot
server does not need to change when a new high-level client or behaviour is
created.
