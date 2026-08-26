# Solution — Validating the RunPose workspace

## Objective

This solution modifies the `RunPose` server so that it only accepts target
positions inside the following workspace:

```text
1.0 <= target_x <= 10.0
1.0 <= target_y <= 10.0
```

If either coordinate is outside this interval, the server:

- does not start the controller;
- returns `success: false`;
- returns the message `Target outside the workspace`;
- remains available for another request.

The target orientation is not restricted. The controller already converts it
to radians and normalizes angular errors.

---

# Files used in the solution

The original student server remains unchanged:

```text
src/ros2_move_turtle/ros2_move_turtle/run_pose_server.py
```

The complete solution is provided in a separate file:

```text
src/ros2_move_turtle/ros2_move_turtle/run_pose_server_validated.py
```

The name `validated` is used instead of `constrained` because the new server
validates the request and rejects it when necessary. It does not constrain or
modify the robot trajectory.

The following executable was also registered in `setup.py`:

```python
'run_pose_server_validated = ros2_move_turtle.run_pose_server_validated:main',
```

This allows the solution to be launched with `ros2 run` without replacing the
original server.

---

# Code modifications

## 1. Rename the class and node

The solution uses a different class and ROS 2 node name so that it can be
identified easily:

```python
class ValidatedRunPoseServer(Node):
    """Execute validated GoToPose requests through a ROS 2 service."""

    def __init__(self) -> None:
        super().__init__('run_pose_server_validated')
```

Only one `/run_pose` server should run at a time because both the original and
validated versions provide the same service name.

## 2. Add the workspace limits

Two class constants define the accepted interval:

```python
WORKSPACE_MIN = 1.0
WORKSPACE_MAX = 10.0
```

Keeping these values in named constants makes the condition easier to read
and allows the workspace to be changed in one place.

## 3. Read the request values once

At the beginning of `run_pose_callback()`, inside the existing `try` block,
the request fields are converted to Python `float` values:

```python
target_x = float(request.target_x)
target_y = float(request.target_y)
target_theta_deg = float(request.target_theta_deg)
```

The same variables are used for validation and later passed to
`start_motion()`.

## 4. Validate the target position

The following code is added before checking the turtle pose and before calling
`start_motion()`:

```python
target_inside_workspace = (
    self.WORKSPACE_MIN <= target_x <= self.WORKSPACE_MAX
    and self.WORKSPACE_MIN <= target_y <= self.WORKSPACE_MAX
)

if not target_inside_workspace:
    response.success = False
    response.message = 'Target outside the workspace'

    self.get_logger().warning(
        f'{response.message}. '
        f'Received x={target_x:.2f}, y={target_y:.2f}.'
    )
    return response
```

The two comparisons are joined with `and`, so both coordinates must be valid.
The limits are inclusive: values equal to `1.0` or `10.0` are accepted.

Returning immediately is important. It prevents execution from reaching
`start_motion()`, so no velocity command is generated for an invalid target.

The validation remains inside the original `try ... finally` structure. The
`finally` block therefore releases `motion_lock` even when the request is
rejected.

## 5. Start valid motions with the checked values

The original code converted the request fields directly in the call:

```python
self.start_motion(
    target_x=float(request.target_x),
    target_y=float(request.target_y),
    target_theta_deg=float(request.target_theta_deg),
)
```

It is replaced by:

```python
self.start_motion(
    target_x=target_x,
    target_y=target_y,
    target_theta_deg=target_theta_deg,
)
```

This call is only reached after the workspace validation has succeeded.

## Complete modified part of the callback

The relevant section of `run_pose_callback()` is:

```python
try:
    target_x = float(request.target_x)
    target_y = float(request.target_y)
    target_theta_deg = float(request.target_theta_deg)

    target_inside_workspace = (
        self.WORKSPACE_MIN <= target_x <= self.WORKSPACE_MAX
        and self.WORKSPACE_MIN <= target_y <= self.WORKSPACE_MAX
    )

    if not target_inside_workspace:
        response.success = False
        response.message = 'Target outside the workspace'

        self.get_logger().warning(
            f'{response.message}. '
            f'Received x={target_x:.2f}, y={target_y:.2f}.'
        )
        return response

    if self.pose is None:
        response.success = False
        response.message = 'Turtle pose is not available.'

        self.get_logger().error(response.message)
        return response

    self.start_motion(
        target_x=target_x,
        target_y=target_y,
        target_theta_deg=target_theta_deg,
    )

    # The original motion completion code continues here.
```

---

# Building and running the solution

Because a new console executable was added to `setup.py`, rebuild the package:

```bash
cd ~/ROS2_rUBot_tutorial

colcon build --packages-select \
  turtle_interfaces \
  ros2_move_turtle \
  --symlink-install
```

## Terminal 1 — Start Turtlesim

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash

ros2 run turtlesim turtlesim_node
```

## Terminal 2 — Start the validated server

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash

ros2 run ros2_move_turtle run_pose_server_validated
```

The server reports the accepted workspace:

```text
Validated RunPose server ready on /run_pose.
Workspace: 1.0 <= x, y <= 10.0.
```

Do not run `run_pose_server` and `run_pose_server_validated` simultaneously.
Both provide the `/run_pose` service.

---

# Verification

## Test 1 — Valid request

Terminal 3:

```bash
source ~/ROS2_rUBot_tutorial/install/setup.bash

ros2 service call \
  /run_pose \
  turtle_interfaces/srv/RunPose \
  "{target_x: 8.0, target_y: 3.0, target_theta_deg: 90.0}"
```

Expected result:

```text
success: true
```

The turtle moves to the target pose.

## Test 2 — Invalid x coordinate

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

The turtle does not move.

## Test 3 — Invalid y coordinate

```bash
ros2 service call \
  /run_pose \
  turtle_interfaces/srv/RunPose \
  "{target_x: 5.0, target_y: -2.0, target_theta_deg: 0.0}"
```

Expected result:

```text
success: false
message: "Target outside the workspace"
```

## Test 4 — Server remains available

After an invalid request, send another valid one:

```bash
ros2 service call \
  /run_pose \
  turtle_interfaces/srv/RunPose \
  "{target_x: 2.0, target_y: 8.0, target_theta_deg: -90.0}"
```

The turtle should execute the motion normally. This verifies that rejecting a
request does not stop or block the server.

---

# Result

The service interface has not changed. Clients continue sending the same
`target_x`, `target_y` and `target_theta_deg` fields. The new responsibility is
entirely inside the server:

```text
Client sends a target
        │
        ▼
Server validates x and y
        │
        ├── invalid ─► failure response, no motion
        │
        └── valid   ─► execute controller, return result
```

This demonstrates why input validation belongs on the robot side: the server
protects the robot even if a client sends an incorrect request.
