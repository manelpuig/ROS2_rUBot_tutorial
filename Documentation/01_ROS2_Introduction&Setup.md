# **ROS 2 Humble: An Introduction**

In this section we will:
- learn what is ROS
- Setup a usefull working ROS environment
- Practice main concepts with Turtlesim robot

## **What is ROS?**

ROS (Robot Operating System) is not a traditional operating system, but a flexible framework for writing robot software. It's a collection of tools, libraries, and conventions that simplify the task of creating complex and robust robot behavior across a wide variety of robotic platforms.

Interesting references for courses:
- Edouard Renard: https://www.udemy.com/course/ros2-for-beginners/learn/lecture/20260476#overview
- https://www.udemy.com/course/learn-ros2-as-a-ros1-developer-and-migrate-your-ros-projects/learn/lecture/22003074#overview

And the ROS2 reference sites:
- https://docs.ros.org/
- https://docs.ros.org/en/humble/

ROS1 is at its end of life (EOL) and we have switched to ROS2 Humble. Each ROS2 version is maintained for five years. ROS2 Humble will be maintained up to May 2027.

![](./Images/01_ROS2_setup/01_ROS2_time.png)

The main architecture and differences are:
![](./Images/01_ROS2_setup/02_ROS1_ROS2.png)
![](./Images/01_ROS2_setup/03_ROS2_dif.png)

ROS2 Humble is now a very good choice.

**The Origin of ROS**

ROS originated in 2007 at Stanford University's Stanford AI Laboratory (SAIL) as part of the Stanford Artificial Intelligence Robot (STAIR) project. Later, development transitioned to Willow Garage.

ROS 2 was developed to address limitations in ROS 1, particularly concerning real-time performance, multi-robot systems, and production-level deployments.

**Why is it Useful?**

ROS 2 provides numerous benefits for robotics development:

- Hardware Abstraction: Enables ROS 2 to be used on different robot hardware (PC, Arduino board, mobile phone, etc.).
- Code Reusability: Facilitates the use of existing ROS packages and libraries from third parties.
- Modularity: Enables the development of modular and maintainable code.
- Community Support: Offers access to a large and active community.
- Production Readiness: Designed for robust and reliable deployments.
- Robustness in communication.
- Development Tools: Includes tools for visualization, debugging, and data logging (e.g., Rviz, ros2 bag).

**How it Works**

ROS 2 operates through a network of nodes that communicate using messages. 

A large project can be structured as a group of different nodes

Each node contains a functionality and shares information with other nodes.

- Nodes: Independent processes that perform specific tasks.
- Topics: Named communication channels where nodes publish and subscribe to messages.
- Messages: Data structures defined in .msg files, used to exchange information.
- DDS (Data Distribution Service): The middleware layer that handles the communication between nodes.
- Services: Synchronous request/response communication.
- Actions: Asynchronous goal/feedback/result communication with cancellation support.

### ROS 2 communication styles

ROS 2 offers different communication mechanisms because robots exchange different kinds of information.

Here's a basic overview of the three ROS 2 communication styles:

A simple rule is:

- Use a topic for continuous data.
- Use a service for a short operation.
- Use an action for a task that needs time to complete.

**Topics: continuous information**: 

Topics are used for unidirectional publish/subscribe communication for streaming data.

Publisher ───── message ─────> Subscriber

![](./Images/01_ROS2_setup/04_Topic-MultiplePublisherandMultipleSubscriber.gif)
official reference: https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.html


Topics are used when data is published continuously.

Examples:

- robot velocity commands;
- robot position;
- camera images;
- laser scanner measurements;
- joint positions.

For example:
- a mobile robot continuously receives velocity commands through the topic: `/cmd_vel`
- and continuously publishes its estimated position through the topic: `/odom`

A topic does not normally return a direct response to the publisher.


**Services: short request and response**: 

A service is used when one node asks another node to execute a short operation.

Client ───── request ─────> Server

Client <──── response ───── Server

Is a synchronous request/response communication for one-shot operations.

![](./Images/01_ROS2_setup/Service-SingleServiceClient.gif)
official reference: https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Services/Understanding-ROS2-Services.html

Examples:

- reset the robot odometry;
- enable or disable the motors;
- open or close a gripper;
- change a robot configuration;
- spawn a new turtle.

A service should normally finish quickly.

For example:
- the /spawn service receives the position and name of a new turtle 
- and returns the final turtle name.
- The service structure is:
  ```text
  Request:
      x
      y
      theta
      name

  Response:
      final name
  ```

Services are not the best option for tasks that require several seconds because the client does not receive continuous information about the task progress.

**Actions: tasks with progress**

An action is used for a task that needs time to complete.

Represents an asynchronous goal/feedback/result communication for long-running tasks.

An action has three main parts:

- Goal
- Feedback
- Result

![](./Images/01_ROS2_setup/Action-SingleActionClient.gif)
Official reference: https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Actions/Understanding-ROS2-Actions.html


- The client sends a goal to the action server.

  Action client ───── goal ─────> Action server

- While the server is executing the task, it can send feedback. 

  Action client <── feedback ─── Action server

- When the task finishes, it sends the result.

  Action client <──── result ─── Action server

Actions can normally also be cancelled.

Examples:

- rotate a robot to a target angle;
- navigate to a target position;
- move a robotic arm;
- follow a joint trajectory;
- pick up an object.

In Turtlesim, the /turtle1/rotate_absolute action rotates the turtle to a desired orientation.


## **Setup a useful working ROS environment**

To work properly in a ROS environment, you can:
- use the UB custom Docker-based ROS2 Humble environment
- use the ROS environment developed by "The Construct" third party enterprise.

### UB custom Docker-based ROS2 Humble environment

We have designed a University of Barcelona custom Docker-based ROS 2 Humble environment to simplify student access to ROS 2 and ensure platform-independent workflows in robotics courses.

The installation details are described on: [UB custom ROS2 Humble environment](https://github.com/manelpuig/ROS2_rUBot_tutorial_ws/blob/main/network_config/humble/UB_Custom_Docker_container_humble.md)
### "The Construct" ROS environment

Is recommended for fast and reliable use:
- Open the link: https://app.theconstructsim.com/
- Create a free user account
- Select "myRosjects"
![](./Images/01_ROS2_setup/05_myRosjects.png)
- Create a New Project: Select ROS2_Humble, create from the scratch and choose a name (i.e. ROS2_Humble)
![](./Images/01_ROS2_setup/06_Rosject.png)
You will have 2GB Virtual machine with Ubuntu 22 and ROS2 Humble installed for free!!

## **Prepare your Workspace**

When working in Laboratory groups, we suggest you:
- One student plays the role of `Director`. This student makes a "Fork" of the Professor's github project.
- The `Director` accept the other students as `Collaborators`
![](./Images/01_ROS2_setup/07_github_collaborators.png)
- Then the `Collaborators` will make a "fork" of the `Director`'s github project.
- The `Collaborators` will be able to update the github `Director`'s project and participate on the project generation

To work on the project (during lab sessions or for homework at home), each student has to clone the `Director`'s github project in his ROS2 Humble working environment.
- Open your ROS2 Humble environment
- Clone the `Director`'s github project
  ```shell
  cd /home/user
  git clone https://github.com/director_username/ROS2_rUBot_tutorial_ws
  cd ROS2_rUBot_tutorial_ws
  colcon build
  ```
- If the compilation process returns warnings on "Deprecated setup tools". Install setup tools version 58.2.0 (last version to work with ros2 python packages without any warnings):
    ````shell
    sudo apt install python3-pip
    pip3 list | grep setuptools
    pip3 install setuptools==58.2.0
    ````
- If the compilation process returns warnings on PREFIX_PATH:
    ````shell
    unset COLCON_PREFIX_PATH
    unset AMENT_PREFIX_PATH
    unset CMAKE_PREFIX_PATH
    cd ~/ROS2_rUBot_tutorial_ws
    rm -rf build/ install/ log/
    colcon build
    ````
- Open .bashrc file (from user) with VS Code (open file...)
- Add the lines (review the exact name of your repository):
    ```xml
    source /opt/ros/humble/setup.bash
    source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
    source /home/user/ROS2_rUBot_tutorial_ws/install/setup.bash
    cd /home/user/ROS2_rUBot_tutorial_ws
    git config --global user.email "xxx@alumnes.ub.edu"
    git config --global user.name "your_github_username"
    ```
    > Include the name an email you have used to create your github account
    >
    > verify your `/home/user/` path

You are ready to work with your repository for this session!

**Repository synchronisation**

The objective is to update the changes you have made, when working in a ROS2 environment, in your GitHub repository.

- Access to your environment local repository:
  ````shell
  cd /home/user/ROS2_rUBot_tutorial_ws
  ````
- Update the local repository with possible changes in github origin repository
  ````shell
  git pull
  ````
- You can work with your local repository for the speciffic project session
- Once you have finished and you want to syncronize the changes you have made and update the github origin repository.  You can use VScode graphical tool options or type:
  ````shell
  git add .
  git commit -m "Message"
  git push
  ````
  > You will have to specify the Username and Password (Personal Access Token you have generated)

To obtain the **PAT** in github follow the instructions:

  - Log in to GitHub
  - Go to Developer Settings
  - Select Personal Access Tokens: Choose Tokens (classic)
  - Click Generate new token (classic) and configure it:
    - Add a note to describe the purpose of the token, e.g., "ROS repo sync."
    - Set the expiration (e.g., 30 days, 60 days, or no expiration).
    - Under Scopes, select the permissions required:
      - For repository sync, you usually need: repo (full control of private repositories)
    - Click Generate token
  - Once the token is generated, copy it immediately. You won't be able to see it again after leaving the page.

Your github origin repository has been updated!

## **Practice ROS2 with Turtlesim**

In this section we will practice the ROS2 concepts with a very simple and useful turtlesim robot.

Documentation:
- [Turtlesim project](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Introducing-Turtlesim/Introducing-Turtlesim.html)

**Turtlesim environment**

Turtlesim is a package that contains a 2D turtle robot simulation and is a good opportunity to start working with ROS2.

We will start turtlesim node with:
```shell
ros2 run turtlesim turtlesim_node
```
![](./Images/01_ROS2_setup/08_turtlesim.png)

You can see the nodes, and their associated topics, services, and actions:
````shell
ros2 node list
ros2 topic list
ros2 service list
ros2 action list
````
![](./Images/01_ROS2_setup/08_turtlesim_node.png)

To see the **information about the nodes, topics and messages**, type:

```shell
ros2 node info /turtlesim
ros2 topic info /turtle1/cmd_vel
ros2 topic info /turtle1/pose
```
In order **to see the message structure**, type:
```shell
ros2 interface show geometry_msgs/msg/Twist
ros2 interface show turtlesim/msg/Pose 
```
you can also find the message structure in google: "geometry_msgs/Twist"

You can see this information in a compact form:
````bash
ros2 topic list -t
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim/msg/Color]
/turtle1/pose [turtlesim/msg/Pose]
````

To see and practice the 3 different communication styles:

### **Topics**: 

In order **to write a message to a topic** we have different options:
- we can **publish directly to the topic**: for exemple to publish a Twist type message with a rate of 1Hz to define a circle, type:

```shell
ros2 topic pub -r 1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 2.0}}"
```

![](./Images/01_ROS2_setup/09_turtlesim_pub.png)


- we can **listen a message from a topic**:
```shell
ros2 topic echo /turtle1/pose
ros2 topic echo /turtle1/cmd_vel
```
- If you’re wondering where all these topics are in rqt_graph, we can use "rqt_graph" and "rqt_plot" to se the nodes-topics structure and the message values

```shell
rqt_graph
rqt # to open the rqt interface and then select the "Plot" plugin
```

![](./Images/01_ROS2_setup/11_turtlesim_rqt.png)


### **Services**:

Running the ros2 service list command in a new terminal will return a list of all the services currently active in the system

````bash
ros2 service list -t
/clear [std_srvs/srv/Empty]
/kill [turtlesim/srv/Kill]
/reset [std_srvs/srv/Empty]
/spawn [turtlesim/srv/Spawn]
...
/turtle1/set_pen [turtlesim/srv/SetPen]
/turtle1/teleport_absolute [turtlesim/srv/TeleportAbsolute]
/turtle1/teleport_relative [turtlesim/srv/TeleportRelative]
...
````
- Let’s introspect a service with a type that sends and receives data, like `/spawn`. From the results of ros2 service list -t, we know /spawn’s type is turtlesim/srv/Spawn.

To see the request and response arguments of the `/spawn` service, run the command:
````bash
ros2 interface show turtlesim/srv/Spawn
float32 x
float32 y
float32 theta
string name # Optional.  A unique name will be created and returned if this is empty
---
string name
````
- Now let’s spawn a new turtle by calling /spawn and setting arguments.
````bash
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2, y: 2, theta: 0.2, name: ''}"
requester: making request: turtlesim.srv.Spawn_Request(x=2.0, y=2.0, theta=0.2, name='')

response:
turtlesim.srv.Spawn_Response(name='turtle2')
````
![](./Images/01_ROS2_setup/spawn1.png)

### **Actions**:

To practice wit a speciffic action, let's start up the two turtlesim nodes:
- Open a new terminal and start `/turtlesim` node:
```shell
ros2 run turtlesim turtlesim_node
```
- In another terminal, start `/teleop_turtle` node to control the turtlesim robot:
```shell
ros2 run turtlesim turtle_teleop_key
```
![](./Images/01_ROS2_setup/10_turtlesim_key.png)

Use the arrow keys on your keyboard to control the turtle. It will move around the screen, using its attached “pen” to draw the path it followed so far.
- To identify all the actions in the ROS graph, run the command:
````bash
ros2 action list -t
/turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]
````
> In brackets to the right of each action name (in this case only /turtle1/rotate_absolute) is the action type, turtlesim/action/RotateAbsolute. You will need this when you want to execute an action from the command line or from code.
- You can further introspect the /turtle1/rotate_absolute action with the command:
````bash
ros2 action info /turtle1/rotate_absolute
Action: /turtle1/rotate_absolute
Action clients: 1
    /teleop_turtle
Action servers: 1
    /turtlesim
````
- One more piece of information you will need before sending or executing an action goal yourself is the structure of the action type.
````bash
ros2 interface show turtlesim/action/RotateAbsolute
# The desired heading in radians
float32 theta
---
# The angular displacement in radians to the starting position
float32 delta
---
# The remaining rotation in radians
float32 remaining
````

- Now let’s send an action goal from the command line and see the feedback:
````bash
ros2 action send_goal /turtle1/rotate_absolute turtlesim/action/RotateAbsolute "{theta: -1.57}" --feedback
Sending goal:
   theta: -1.57

Goal accepted with ID: e6092c831f994afda92f0086f220da27

Feedback:
  remaining: -3.1268222332000732

Feedback:
  remaining: -3.1108222007751465

…

Result:
  delta: 3.1200008392333984

Goal finished with status: SUCCEEDED
````

- We can use "rqt_graph" and "rqt_plot" to se the nodes-topics structure and the message values

```shell
rqt_graph
rqt # to open the rqt interface and then select the "Plot" plugin
```

![](./Images/01_ROS2_setup/11_turtlesim_rqt.png)

