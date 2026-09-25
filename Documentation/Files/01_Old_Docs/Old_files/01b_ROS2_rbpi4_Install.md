# **ROS2 Humble install on RaspberryPi4**

The procedure is:
- Install Ubuntu22.04 server (64bits) image using "Pi Imager"
- connect using SSH
- Install ubuntu-desktop
- Install ros2 Humble

You can follow the instructions on:
- https://roboticsbackend.com/install-ubuntu-on-raspberry-pi-without-monitor/
- https://roboticsbackend.com/install-ros2-on-raspberry-pi/
- https://github.com/ros-realtime/ros-realtime-rpi4-image

## **Install Ubuntu22 on Raspberrypi4**

Follow instructions:
- Use RaspberryPi Imager and choose Ubuntu22 Desktop (64bits)
- Connect ethernet cable to your raspberrypi4
- Insert SD card in RBPI4 and switch on
- select Language and keyboard 
- Select:
    - username: mpuig
    - Password: 1234
- Select your wifi
- Configure a hotspot:
    - Select wifi settings
    - Turn on hotspot
        - name: rubot_ros2
        - pass: rubot_ros2
    - Make the connection "Hotspot" start automatically:
    ```shell
    nmcli con mod Hotspot connection.autoconnect yes
    ```
- update, upgrade and Install ssh service:
```shell
sudo apt update
sudo apt upgrade
sudo apt-get install openssh-server
```
- reboot
- Change the Hotspot settings (name or password):
```shell
sudo nm-connection-editor
```

**Connect to the rbpi4:**

First time we have to configure your Raspberry Pi to allow graphical desktop remote connections:
- In Ubuntu settings select **sharing**
- Activate sharing (for Nomachine remote desktop)
- Activate "Remote Login" (for ssh connection)

a) remotelly with **SSH**
```shell
cmd
ssh mpuig@10.42.0.1
```
> Perhaps the security Key will be reestablished and you will need to delete the line for the old key in C:\Users\puigm\ .ssh\known_hosts
> Comment the line with the 10.42.0.1 IP to stablish another security key
- With screen and keyboard

    - Sometimes when you connect a USB the screen service is corrupted. Then reestart the service from the remote connection:
    ```shell
    sudo service gdm3 restart
    ```

b) With a remote Desktop **Nomachine** (recommended):

To have the graphical interface available, you will need to connect a HDMI dongle in the microHDMI Connector!
- In your raspberryPi4 install Nomachine (arm64, DEB package): https://downloads.nomachine.com/download/?id=107&distro=Raspberry&hw=Pi4
- In PC open NoMachine viewer
- Select the raspberrypi IP address: 10.42.0.1
- you have to specify:
    - user: mpuig
    - password: 1234
- Choose "scale remote display to the window"
- You will have the raspberrypi4 desktop on your windows NoMachine screen


## **Install ROS2 Humble on Raspberrypi4**

Follow instructions in: https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html

I suggest to install **ros-humble-desktop**

If you have installed "ros-humble-ros-base", you will need to:
- Install ROSDEP2
```shell
sudo apt install python3-rosdep2
rosdep update
```
- Install C++ compiler (g++)
```shell
sudo apt-get install g++
export CXX=g++
```
> add this last instruction "export" in ~/.bashrc

## **Make a backup of Raspberrypi4 SD card**

To copy this card already installed to another SD card, you will have to make a backup of your original SD card.

The procedure is:

1. **Insert an External Storage Device**: Insert an external storage device (e.g., a USB drive) into one of the USB ports on your Raspberry Pi. This USB has to be formated to NTFS format to accept files larger than 4GBytes!

2. **Identify the SD Card and USB paths**: Determine the device name of your SD card an USB. You can use the `lsblk` or `fdisk -l` command to list the connected drives and identify the SD card. It typically has a device name like "/dev/mmcblk0" for SD original card and "/media/mpuig/usb_backup2/" for the pendrive connected to USB port.

3. **Create the Image**: Use the `dd` command to create an image of the SD card and save it directly to the external storage device. For example:

   ```bash
   sudo dd if=/dev/mmcblk0 of=/media/mpuig/usb_backup2/Humble_rbpi4.img bs=4M status=progress
   ```

   - `if`: Input file (the SD card).
   - `of`: Output file (the image file on the external drive).
   - `bs`: Block size (use 4M for better performance).
   - `status=progress`: Display progress information while creating the image.

4. **Wait for Completion**: The `dd` command may take some time to complete, depending on the size of your SD card. Be patient and let it finish.

5. **Eject the External Drive**: Once the image creation is complete, safely eject the external storage device from your Raspberry Pi.

6. **Reduce size of image**: PiShrink is a script specifically designed for Raspberry Pi images. It can shrink a full image to a smaller size based on the actual data size, removing unused space. First, you need to install PiShrink:

```bash
cd /home/mpuig
git clone https://github.com/Drewsif/PiShrink.git
cd PiShrink
sudo chmod +x pishrink.sh
```
7. **Shrink the Image**: Run PiShrink on your full image to reduce its size:

```bash
cd /media/mpuig/usb_backup2
sudo ~/PiShrink/pishrink.sh Humble_full_rbpi4.img Humble_full_rbpi_shrink.img
```
This script will automatically reduce the size of the image file to fit the actual data size and removes unused space.

You have also another **tool: gzip** (recommended!)

Open a terminal in the folder where you have the image to compact:
```shell
gzip your_image.img
```
This will give you a compacted image with extension your_image.img.gz. You can use RaspberryPi Imager to write directly the compacted image to a 32GB SD card.

Now you have an image file of your Raspberry Pi's SD card saved on the external storage device, which you can use for backup, cloning, or restoring your Raspberry Pi's operating system and data.

## **Restore an image to another Raspberrypi4 SD card**

To restore the created image, you can use "Balena Etcher" or "RaspberryPi Imager" softwares.
- Identify the size of the data to be restores from the image:
```bash
ls -lh /path/to/your/image.img
```
> If your SD card has 16 GB of storage but you're only using 4 GB of that space, the image file will be around 4 GB in size.
- If you are using "RaspberryPi Imager" use the "Use custom" option to select the image location in your pendrive.
- The new SD card will have the size of the "full_image_shrink.img" to expand it to the total size of SD card:
```bash
sudo apt install raspi-config
sudo raspi-config
```
- Navigate to "Advanced Options": Use the arrow keys to navigate to "Advanced Options" and press Enter.

- Select "Expand Filesystem": In the "Advanced Options" menu, select "Expand Filesystem" and press Enter.

- Confirm Resize: Follow the on-screen prompts to confirm the resizing of the filesystem. This will resize the root filesystem to utilize the full available space on the SD card.

- Reboot: After the resizing is complete, you will be prompted to reboot. Select "Finish" and then choose to reboot.

## **Install ROS2 Humble on RaspberryPi5!!**


RaspberryPi5 works on Ubuntu23 and the Installation process is:
- Save image of Ubuntu23 Desktop from Raspberry Imager
- Connect Monitor and keyboard
- select network
- Install XRDP from instructions in: https://c-nergy.be/blog/?p=19228
```shell
wget https://www.c-nergy.be/downloads/xRDP/xrdp-installer-1.4.8.zip
unzip xrdp-installer-1.4.8.zip 
chmod +x  ~/Downloads/xrdp-installer-1.4.8.sh
./xrdp-installer-1.4.8.sh -s -l  
```
- Reboot
- On your computer, select the hotspot:
    ISSD: "rUBot_5_01"
    Pass: mpuig1234
- Open "Remote Desktop" and select:
    - Ip: 10.42.0.1
    - user: mpuig
    - pass: 1234

- Install ROs2 Humble from Docker: 
    - Follow instructions in: https://docs.ros.org/en/humble/How-To-Guides/Installing-on-Raspberry-Pi.html#raspberry-pi-os-with-ros-2-in-docker
```shell
sudo docker pull ros:humble-ros-core
sudo docker run -it --rm ros:humble-ros-core
sudo docker run --name ROS2_Humble_osrf -e DISPLAY=host.docker.internal:0.0 -it --rm ros:humble-ros-core
```
List the containers:
```shell
sudo docker ps -q
```
Stop/Remove container
```shell
sudo docker stop afa800661dc0
sudo docker rm afa800661dc0
```
- Update packages
```shell
apt update
apt upgrade
```
Follow tutorials: https://docs.ros.org/en/humble/Tutorials.html
