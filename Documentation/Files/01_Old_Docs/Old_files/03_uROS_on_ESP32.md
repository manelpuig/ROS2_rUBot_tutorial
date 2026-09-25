## **1. microROS Installation on ESP32**

Follow instructions in:
- https://www.udemy.com/course/ros2-for-beginners-build-your-first-robot-with-esp32/learn/lecture/39333626?start=45#overview

Official links:
- uROS official website: https://micro.ros.org/docs/overview/features/
- uROS arduino library: https://github.com/micro-ROS/micro_ros_arduino
- Setup ESP32 in arduino IDE: https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-windows-instructions/
- uROS agent: https://github.com/micro-ROS/micro-ROS-Agent
- Install ROS dependencies: https://wiki.ros.org/rosdep


![](./Images/01_ROS2_install/4_uROS_connection.png)

uROS for Arduino supports ESP32, for that we will have to:
- Install arduino in rbpi4 board:
```shell
sudo snap install arduino
```
> You will have to add mpuig user to the group (this appears as warning when executing arduino first time)
```shell
sudo usermod -a -G dialout mpuig
```
> You have to shutdown the RaspberryPi4 before continue with the installation!!
- run arduino
- Install on arduino IDE the ESP32 board from Espressif Systems (version 2.0.2 or later)
https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html
- Update the Boards firmware if needed
- Connect ESP32 board
- Select the ESP32 Dev Module board and port ttyUSB0
- Add arduino uROS libraries: 
    - https://github.com/micro-ROS/micro_ros_arduino
    - Select Humble branch and download in zip
    - Add this library in arduino IDE

In order to properly communicate microROS sketch in ESP32 to ROS2 in RaspberryPi4, we need to install microROS Agent: https://github.com/micro-ROS/micro-ROS-Agent
- Go to the microROS Agent web site and select Humble
- copy the URL to clone this repository
- clone the repository to src folder in raspberrypi4 ros2_ws project
```shell
cd ~/ros2_ws/src
git clone https://github.com/micro-ROS/micro-ROS-Agent.git -b humble
```

- we have to install dependencies for packages in ws. Later we compile the new package
```shell
cd ~/ros2_ws
rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/local_setup.bash
```
Now you can run a sketch in arduino ESP32:
- Select exemple "micro-ros_publisher.ino" and compile it
- Connect ESP32 to arduino USB and upload the sketch
- Run the microROS agent:
```shell
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0
```
- press enable button to stablish communication
- Verify the topic list and the publication of the sketch:
```shell
ros2 topic list
ros2 topic echo /micro_ros_arduino_node_publisher
```
Congratulations!. You have now the micoros agent working and you have good communication between ESP32 and RaspberryPi4!!

**First exemple**

Let's upload the micro-ros_subscriber_twist.ino exemple to our ESP32

Now run the micr-ros agent:
```shell
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0
```
Press enable button and the ESP32 will be connected

Open a new terminal an type:
```shell
ros2 topic list
```
You will see the topic: micro_ros_arduino_twist_subscriber

In the same terminal listen to this topic
```shell
ros2 topic echo /micro_ros_arduino_twist_subscriber 
```

In a new terminal publish to this topic with:
```shell
ros2 run teleop_twist_keyboard teleop_twist_keyboard --args -ros -remap /cmd_vel:=/micro_ros_arduino_twist_subscriber
```
![](./Images/05_uROS/01_rqt_subs.png)


