# **ROS2 tutorial**

The objective of this section is to learn how to ceate a Package to perform a specific project and the needed nodes to give the desired functionality to the robot.

Bibliography:
- [RO2 Humble official doc](https://docs.ros.org/en/humble/)
- [Edouard Renard-Udemy course](https://www.udemy.com/course/ros2-for-beginners/learn/lecture/21305270#overview)
- [ROS2 Basics in 5 Days (Python)-TheConstruct course](https://www.robotigniteacademy.com/courses/268)


## **1. ROS2 workspace and packages**

The **ROS2 workspace** is the directory in your hard disk where your ROS2 packages reside to be usable by ROS2.

ROS2 uses **packages** to organize its programs. You can think of a package as all the files that a specific ROS2 program contains

In ROS2, you can create two types of packages: Python packages and CMake (C++) packages.

Every **Python package** will have the following structure of files and folders:

- package.xml: File containing meta-information about the package (maintainer of the package, dependencies, etc.).
- setup.py: File containing instructions for how to compile the package: define the executables, install the extra folders, etc
- setup.cfg: File that defines where the scripts will be installed.
- /<package_name>: This directory will always have the same name as your package. You will put all your Python scripts inside this folder. Note that it already contains an empty "__init__.py" file.
- /resource/<package_name>: stores essential information that ROS 2 uses to understand and manage the package.

Every **CMake package** will have the following structure of files and folders:
- package.xml: file containing meta information about the package (maintainer of the package, dependencies, etc.).
- CMakeLists.txt: file that describes how to build the code within the package (i.e. install the extra folders, etc)
- src: directory containing the source code for the package
- include/<package_name>: directory containing the public headers for the package

Some packages might contain extra folders. For instance, the launch folder that contains the package's launch files 

**Create a new package**

Every time you want to create a package, you have to be in the src directory 

Type to create a **python package**:
```shell
cd src
ros2 pkg create --build-type ament_python --license Apache-2.0 <package_name> --dependencies rclpy
````
Type to create a **CMake package**:
```shell
cd src
ros2 pkg create --build-type ament_cmake --license Apache-2.0 <package_name> --dependencies rclcpp
````
In our case we have created a python package:
````shell
ros2 pkg create --build-type ament_python --license Apache-2.0 ros2_tutorial --dependencies rclpy
````
>the <package_dependencies> are the names of other ROS2 packages that your package depends on.

Now you have to build the created ws:
```shell
cd /home/ROS2_rUBot_tutorial_ws
colcon build
```
Source the workspace. Be sure in .bashrc file to have:
```shell
source /opt/ros/humble/setup.bash 
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
source /home/ROS2_rUBot_tutorial_ws/install/setup.bash
cd /home/ROS2_rUBot_tutorial_ws
```
You are ready to work with this workspace

Some interesting commands:
- ros2 pkg list: Gives you a list of all your ROS system packages.

- ros2 pkg list | grep my_package: Filters, from all of the packages located in the ROS system, the package is named my_package.

**Compile a Package**

Sometimes (for large projects), you will not want to compile all of your packages. This would take such a long time. So instead, you can use the following command to compile only the packages where you have made changes:
```shell
colcon build --packages-select <package_name>
```
You can compile a speciffic package and launch not the executable but the python file in src (we do not need to compile every time we make a change in the python file!):
```shell
colcon build --packages-select ros2_tutorial --symlink-install
```

## **2. ROS2 Nodes**
In ROS2, each node should be responsible for a single module (e.g., one node for controlling wheel motors, one for controlling a LIDAR control, etc.). Each node can communicate with other nodes publishing or subscribing messages from topics.

A full robotic system is comprised of many nodes working together. In ROS2, a single executable (a C++ or Python program, etc.) is needed to create a node.
ROS2 nodes are:
- Subprograms in your application, responsible for only one thing
- communicate with each other through topics, services and parameters

**Create first ROS2 Program**

You can create a program based on two nodes:
- A Publisher node (/talker) that publish a string message "Hello world" to a "/chatter" topic
- A subscriber node (/listener) that subscribes to "/chatter" topic and prints on the screen the read message.

![](./Images/02_ROS2_tutorial/01_PubSub.png)

Each node is created within a python program in "src/ros2_tutorial/ros2_tutorial" folder:
- "publisher_hello.py": creates a talker node
- "subscriber_hello.py": creates a listener node

You can create Publisher and Subscriber python files using speciffic templates.

Before compilation we have to generate an **executable** from the python scripts you created:
- In "setup.cfg": is specified where do you install the node (install/ros2_tutorial/lib/ros2_tutorial). This is already done by default.
- In the **setup.py**: you have to add entry points for Publisher and Subscriber executables
    ```python
    entry_points={
        'console_scripts': [
                'publisher_exec = ros2_tutorial.publisher_hello:main',
                'subscriber_exec = ros2_tutorial.subscriber_hello:main',
        ],
    },
    ```
Compile inside ws: 

````shell
colcon build
````
Run in a separate terminals:
```shell
ros2 run ros2_tutorial publisher_exec
ros2 run ros2_tutorial subscriber_exec
```
You can also run the nodes from the folder where the nodes are installed
```shell
cd install/ros2_tutorial/lib/ros2_tutorial
./publisher_exec
./subscriber_exec
```
Take into account that, the name of:
- the python file (publisher_hello.py)
- the node (talker)
- the executable (publisher_exec)

Could be different!!

## **3. Create Launch files**

ROS2 programs can be run:
- from executable files
- from launch files. 

When using executable files, we need one terminal to run each node. 

To make easier this process using a unique terminal to launch multiple nodes, we will use launch files.

 Launch files written in Python or XML. They can start and stop different nodes as well as trigger and act on various events. 

To create a launch file we have to:
- create a "launch" folder in "src/ros2_tutorial/"
- Inside create the launch file in different formats (python, XML)
- Enable the execution of all files in "launch" folder. For that you have to open "setup.py" file and make some modifications to:
    - Import some libraries
    ```shell
    import os
    from glob import glob
    ```
    - share this launch folder to the executable path. Add this line in "data_files"
    ```shell
    (os.path.join('share', package_name), glob('launch/*'))
    ```
- compile again

**Writting launch files**

Launch files can be written in python or XML formats. We show here the same lauch file in the 2 different formats.
- Launch file in Python format: "hello_pub_sub.launch.py" file
```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ros2_tutorial',
            executable='publisher_exec',
            output='screen'),
        Node(
            package='ros2_tutorial',
            executable='subscriber_exec',
            output='screen'),
    ])
```
Now you can execute the launch file:
```shell
ros2 launch ros2_tutorial hello_pub_sub.launch.py
```
- Launch file in XML format: "hello_pub_sub.xml" file
```xml
<launch>
<node pkg="ros2_tutorial" exec="publisher_exec"/>
<node pkg="ros2_tutorial" exec="subscriber_exec"/>
</launch>
```
See documentation: https://docs.ros.org/en/humble/How-To-Guides/Launch-files-migration-guide.html

Now you can execute the launch file:
```shell
ros2 launch ros2_tutorial hello_pub_sub.xml
```

**Exercise:**

Create a new package "ros2_move_turtle" to control the movement of the previous Turtlesim robot.

![](./Images/02_ROS2_tutorial/02_move_turtle.png)

The program functionality will be based on 2 nodes:
- The "/turtlesim" node we have already practice in last section
- A new "/move_turtle" node that:
    - subscribes to the "/turtle1/pose" topic
    - Publish to the "/turtle1/cmd_vel" topic a message Twist
    - if the position in x or y direction of the robot is greater than 7m, the robot stops

