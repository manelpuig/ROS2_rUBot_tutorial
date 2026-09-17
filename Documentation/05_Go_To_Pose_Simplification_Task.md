# Task: Simplify a ROS 2 Go-to-Pose Controller

## Goal

Analyze [go_to_pose.py](../src/ros2_move_turtle/ros2_move_turtle/go_to_pose.py) and rewrite it using the publisher and subscriber templates you have learned. Your program must move the turtlesim turtle to a target position and then rotate it to a target orientation.

Keep the original file unchanged. Write your solution in `go_to_pose_simple.py`. Use the provided simplified version as a reference after developing your own solution.

## 1. Understand the original program

Read the code and answer these questions before making changes:

- Which topics and message types does the node use?
- Which parameters define the target, controller gains, speed limits, and tolerances?
- How does the program calculate distance and angular errors?
- Why are angles converted from degrees to radians and normalized between −π and π?
- Why does forward speed decrease when the turtle is facing away from the target?
- How does the program switch from moving to the target position to adjusting the final orientation?
- What happens when the target is reached or the user presses Ctrl+C?

Identify where the original program stores the pose, calculates velocity, and publishes commands.

## 2. Simplify the structure

Use the following organization:

| Part | Responsibility |
| --- | --- |
| Constructor | Define parameters, initialize the command, and create the publisher, subscriber, and timer. |
| Pose subscriber callback | Calculate and store the velocity command using the received pose. |
| Publisher timer callback | Publish the stored command every 0.05 seconds (20 Hz). |
| Main function | Initialize ROS, create the node, call `rclpy.spin(node)`, and clean up on exit. |

### Define parameters directly as attributes

Declare and read each ROS parameter in one statement. For example:

```python
self.target_x = self.declare_parameter('target_x', 8.0).value
```

Keep all original parameter names and default values. Store values in clear instance attributes such as `self.target_x` and `self.linear_gain`. Convert the target angle and angular tolerance to radians when reading them.

### Publish with a timer

Initialize `self.command` as an empty `Twist`, so the initial velocities are zero. Create a publisher on `/turtle1/cmd_vel` and a timer with a period of 0.05 seconds.

The timer callback should only publish `self.command`. It should not calculate motion or wait for a pose.

### Calculate motion in the subscriber callback

Subscribe to `/turtle1/pose` using `Pose`. Use the pose passed directly to the callback: this callback runs when a position message arrives, so no initial pose-waiting loop is needed.

Keep two simple indicators:

- `self.position_reached`: switch from position control to orientation control.
- `self.finished`: prevent further motion calculations once the target is reached.

Implement the following behavior:

1. During position control, calculate distance and heading error. Update the forward and angular velocities using the original control equations and speed limits.
2. When the distance is within tolerance, store a zero command and switch to orientation control.
3. During orientation control, keep forward velocity at zero and calculate the angular velocity from the final orientation error.
4. When the angular error is within tolerance, store a zero command and mark the motion as finished.

Keep angle normalization and the cosine factor that reduces forward speed. Remove the original timer-based control loop, extra motion states, and redundant attributes or methods.

### Simplify the main function

Use `rclpy.spin(node)` to let ROS execute both callbacks. Do not use movement loops, `spin_once()` loops, or `sleep()` calls.

Use `try`, `except KeyboardInterrupt`, and `finally` to handle Ctrl+C. During cleanup, cancel the timer, disable further motion calculations, publish a zero command, destroy the node, and shut down ROS if it is still active.

After reaching the target, the node should remain active and continue publishing zero velocity until the user stops it.

## 3. Test your solution

Start turtlesim and run your simplified program in your ROS 2 environment.

- Check the default target: x = 8.0, y = 3.0, orientation = 90°.
- Try another target using ROS parameters.
- Check that the turtle turns toward the target before moving forward when initially facing away from it.
- Check that it stops advancing before adjusting its final orientation.
- Check that it remains stopped after completing the motion.
- Press Ctrl+C during motion and check the shutdown behavior.

## Submit

Submit your simplified Python file and a short explanation of:

- How the original controller works.
- Which parts you simplified and why.
- How the subscriber callback and publisher timer share the velocity command.
- What you observed during testing.

Aim for clear, readable code with fewer unnecessary steps. Do not remove the control equations, speed limits, or tolerances just to reduce the line count.
