# ROS 2 Tutorial — Distributed Robot Control with Services

## Learning objectives

In this activity, you will compare a direct controller with a distributed client-server architecture. You will learn to:

- distinguish topics, services, and parameters;
- identify the request and response of a ROS 2 service;
- understand the responsibilities of a client and a server;
- explain why a closed-loop controller should run close to the robot;
- send one pose or a sequence of poses to a service.

![](./Images/02_ROS2_tutorial/02_move_turtle.png)

## 1. Build the workspace

```bash
cd ~/ROS2_rUBot_tutorial
colcon build --packages-select turtle_interfaces ros2_move_turtle --symlink-install
source install/setup.bash
```

## 2. Direct control with `go_to_pose`

The node [go_to_pose.py](../src/ros2_move_turtle/ros2_move_turtle/go_to_pose.py) receives its target through ROS parameters. It reads the turtle pose, calculates the velocity, and publishes the command itself:

```text
Target parameters
       |
       v
  go_to_pose
   |       |
   |       +--> /turtle1/cmd_vel
   +<---------- /turtle1/pose
```

Run it with:

```bash
ros2 launch ros2_move_turtle go_to_pose.launch.py \
  target_x:=2.0 target_y:=8.0 target_theta_deg:=-90.0
```

The launch starts Turtlesim and the controller. The controller first reaches the target position and then adjusts the final orientation.

This solution is suitable when the controller and robot run on the same computer. On a real robot, sending every sensor reading and velocity command through Wi-Fi would make the control loop depend on network latency and interruptions.

## 3. Distributed control with a service

A better distributed architecture keeps the closed-loop controller on the robot and sends only a high-level target:

```text
Student computer                         Robot computer

go_to_pose_client  -- RunPose request --> go_to_pose_server
                   <-- result ----------       |
                                             topics
                                               |
                                           turtlesim
```

The client specifies **what** the robot must do. The server decides **how** to execute it.

| Component | Responsibility |
|---|---|
| `go_to_pose_client` | Sends one target pose and waits for the result. |
| `go_to_pose_sequence_client` | Reads a YAML file and sends several poses in order. |
| `go_to_pose_server` | Executes the closed-loop controller and remains available. |
| `turtlesim` | Simulates the robot. |

### Service interface

All clients and the server use `/run_pose` with the type `turtle_interfaces/srv/RunPose`:

```text
float32 target_x
float32 target_y
float32 target_theta_deg
---
bool success
string message
```

The fields above `---` are the request. The fields below it are the response.

## 4. Run the client-server system

### Start Turtlesim and the server

Terminal 1:

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash
ros2 launch ros2_move_turtle go_to_pose_server.launch.py
```

This launch starts Turtlesim and the persistent server.

### Inspect the ROS graph

Terminal 2:

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash
ros2 node list
ros2 topic list
ros2 service list
ros2 service type /run_pose
ros2 interface show turtle_interfaces/srv/RunPose
```

Identify the three nodes, the two turtle topics, and the `/run_pose` service.

### Send a request from the terminal

```bash
ros2 service call /run_pose turtle_interfaces/srv/RunPose \
  "{target_x: 2.0, target_y: 8.0, target_theta_deg: -90.0}"
```

The command waits until the movement finishes. A successful response is:

```text
success: true
message: "Target pose reached successfully."
```

### Send a request with the Python client

```bash
ros2 launch ros2_move_turtle go_to_pose_client.launch.py \
  target_x:=8.0 target_y:=3.0 target_theta_deg:=90.0
```

The client finishes after receiving the response. The server remains active and can receive another request.

## 5. How the programs work

### Client

The file [go_to_pose_client.py](../src/ros2_move_turtle/ros2_move_turtle/go_to_pose_client.py) follows four steps:

1. Read the target parameters.
2. Create a client for `/run_pose`.
3. Fill and send a `RunPose.Request`.
4. Wait for and display the response.

The call is asynchronous because the result is not available immediately:

```python
future = self.client.call_async(request)
rclpy.spin_until_future_complete(node, future)
response = future.result()
```

The client never reads the turtle pose or publishes velocity. Those are server responsibilities.

### Server

Start from `go_to_pose_server_template.py` and rename it to `go_to_pose_server.py` when it is complete. The server combines four ROS elements:

| Element | Purpose |
|---|---|
| Service callback | Receives and stores a target pose. |
| Pose subscriber | Calculates the velocity from each current pose. |
| Publisher timer | Publishes the stored velocity at 20 Hz. |
| Service response | Reports success, rejection, or timeout. |

The controller has two simple phases:

```text
Move to target position --> Adjust final orientation --> Stop
```

The subscriber calculates the command, while the timer only publishes it. This is the same structure used in `go_to_pose.py`; the difference is that the target now comes from a service request instead of node parameters.

### Why is a multithreaded executor needed?

The service callback waits until the movement finishes. During this wait, ROS must continue executing the pose subscriber and publisher timer. Therefore, the server uses a `MultiThreadedExecutor` and a `ReentrantCallbackGroup`.

This concurrency is necessary for the service behaviour; the controller itself remains simple.

## 6. Topics, services, and parameters

| ROS 2 mechanism | Example | Use |
|---|---|---|
| Topic | `/turtle1/pose` | Continuous sensor information. |
| Topic | `/turtle1/cmd_vel` | Continuous velocity commands. |
| Service | `/run_pose` | One operation with a final response. |
| Parameter | `target_x` | Configures a node or client. |

Use topics for continuous data and services for operations that return one result.

## 7. Student activities

### Activity A — Predict and observe

Send these targets one after another:

```bash
ros2 launch ros2_move_turtle go_to_pose_client.launch.py \
  target_x:=2.0 target_y:=8.0 target_theta_deg:=-90.0

ros2 launch ros2_move_turtle go_to_pose_client.launch.py \
  target_x:=8.0 target_y:=3.0 target_theta_deg:=90.0
```

Before each request, predict the final pose. Afterwards, check which node finishes and which node remains active.

### Activity B — Inspect the communication

While the turtle is moving, use:

```bash
ros2 topic echo /turtle1/pose
ros2 topic echo /turtle1/cmd_vel
```

Answer:

1. Which topic contains feedback?
2. Which topic contains the control command?
3. Does the client publish or subscribe to either topic?

### Activity C — Validate requests

Modify `go_to_pose_server.py` so that it only accepts targets inside:

```text
1.0 <= target_x <= 10.0
1.0 <= target_y <= 10.0
```

If the target is outside this area, return immediately with:

```text
success: false
message: "Target outside the workspace"
```

Test a valid and an invalid request. Confirm that the invalid request does not move the turtle and that the server remains available afterwards.

## 8. Execute a pose sequence

The file `config/turtle_pose_sequence.yaml` contains several target poses. Run them with:

```bash
ros2 launch ros2_move_turtle go_to_pose_sequence_client.launch.py
```

The sequence client sends one request, waits for success, and then sends the next. It stops if a request fails.

A different YAML file can be selected with:

```bash
ros2 launch ros2_move_turtle go_to_pose_sequence_client.launch.py \
  sequence_file:=/absolute/path/to/my_sequence.yaml
```

The same server executes both single requests and sequences without modification.

## 9. Review questions

1. What is the difference between a topic and a service?
2. What information does the client send?
3. What information does the server return?
4. Why does the server remain active after a movement?
5. Why does the client not subscribe to `/turtle1/pose`?
6. Why should the closed-loop controller run close to the robot?
7. Why does this server need a multithreaded executor?

## Service limitation

A service is sufficient for this introductory activity. A ROS 2 Action would be more suitable if the application needed progress feedback, cancellation, or explicit goal states.
