# ROS 2 Tutorial - Distributed Robot Control with Services

## Objective

In the previous exercise, you implemented a simple **GoToPose** node.

The node subscribed to the turtle pose, computed the control error, and continuously published velocity commands until the turtle reached the target pose.

This approach is useful for learning ROS 2 publishers and subscribers, but it is **not the architecture normally used in modern robots**.

The objective of this exercise is to redesign the same application using a **ROS 2 Service**, following the same architecture that will later be used with the **rUBot mobile robot** and the **UR5e industrial robot**.

---

# Why do we need a Service?

Imagine the following situation:

- A student is working from a laptop connected through WiFi.
- The robot contains its own onboard computer (for example a Raspberry Pi or an industrial controller).
- The robot must execute a closed-loop motion controller using its sensors and actuators.

A first idea could be:

```
Student PC
      │
      │ cmd_vel
      ▼
Robot
```

However, this architecture has an important problem.

The motion controller would depend on:

- WiFi latency
- Network jitter
- Packet losses
- Variable communication delays

If every control command has to travel through the network, the robot may become unstable or react slowly.

Instead, modern robotic systems usually separate the application into two parts.

```
Student PC
(High-level application)

        │
        │ RunPose Service
        ▼

Robot Controller
(Server)

        │
        ├── Sensor subscribers
        ├── Closed-loop controller
        └── Velocity publisher

        ▼

Robot
```

The client only sends a high-level command:

> "Go to this pose."

The robot controller executes the complete control loop locally, where communication with sensors and actuators is fast and deterministic.

This architecture is widely used in industrial robotics.

---

# Examples in this course

Later in this course you will use exactly the same architecture.

## rUBot mobile robot

```
Student PC
        │
        │ RunPose
        ▼
Raspberry Pi
        │
        ├── Wheel encoders
        ├── IMU
        ├── Closed-loop controller
        └── Motors
```

The Raspberry Pi executes the motion controller locally.

---

## UR5e industrial robot

```
Student PC
        │
        │ RunPose
        ▼
Professor PC
        │
        ├── MoveIt 2
        ├── Motion planning
        ├── Robot controller
        └── UR5e
```

The student computer sends a motion request.

The motion planning and trajectory execution are performed on the computer directly connected to the robot through Ethernet.

---

# Exercise overview

In the previous exercise you implemented this node:

```
go_to_pose.py
```

The node:

- subscribes to `/turtle1/pose`
- publishes `/turtle1/cmd_vel`
- reaches a target position and orientation

To execute the node:
```bash
ros2 launch ros2_move_turtle go_to_pose.launch.py \
  target_x:=2.0 \
  target_y:=8.0 \
  target_theta_deg:=-90.0
```

In this exercise the controller will remain almost identical.

The main difference is that the target pose is no longer defined inside the node.

Instead, another node will request the motion using a ROS 2 Service.

---

# Package provided

The teaching staff provides the package:

```
turtle_interfaces
```

This package contains the custom ROS 2 interface:

```
srv/RunPose.srv
```

The package is implemented using **ament_cmake** because ROS 2 custom interfaces must be generated during compilation.

Students do **not** need to modify this package.

---

# Service definition

```
float32 target_x
float32 target_y
float32 target_theta

---

bool success
string message
```

The request contains the desired turtle pose.

The response indicates whether the motion has finished successfully.

---

# Package to implement

Students will work only inside the Python package:

```
ros2_move_turtle
```

---

# Node 1 - RunPose Server

Create:

```
run_pose_server.py
```

Responsibilities:

- Subscribe to `/turtle1/pose`
- Publish `/turtle1/cmd_vel`
- Offer the service:

```
/run_pose
```

When a client sends a request:

1. Store the target pose.
2. Execute the closed-loop controller.
3. Stop the turtle when the position and orientation tolerances are satisfied.
4. Return:

```
success = true
```

---

# Node 2 - RunPose Client

Create:

```
run_pose_client.py
```

Responsibilities:

- Wait until the service is available.
- Send a target pose.
- Wait for the response.
- Print the result.

Example:

```
Target pose

x = 8.0
y = 3.0
theta = 1.57 rad
```

---

# Expected architecture

```
                Service Request

run_pose_client
        │
        ▼
run_pose_server
        │
        ├── Subscriber (/turtle1/pose)
        ├── Closed-loop controller
        └── Publisher (/turtle1/cmd_vel)
                │
                ▼
             turtlesim
```

---

# Comparison with the previous exercise

Previous exercise:

```
Target pose
      │
      ▼
go_to_pose.py
      │
      ├── Subscriber
      └── Publisher
```

Current exercise:

```
run_pose_client
      │
      ▼
RunPose Service
      │
      ▼
run_pose_server
      │
      ├── Subscriber
      └── Publisher
```

The control algorithm is almost identical.

The main difference is the software architecture.

---

# Learning objectives

After completing this exercise you should understand:

- Why services are useful in distributed robotic systems.
- The difference between Topics and Services.
- How to create a ROS 2 Service Server.
- How to create a ROS 2 Service Client.
- Why industrial robots usually execute the control loop locally.
- Why high-level applications send commands instead of directly controlling the actuators.

This architecture will be reused later in the **rUBot** and **UR5e** laboratory sessions.