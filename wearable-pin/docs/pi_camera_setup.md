# Raspberry Pi Camera Setup Guide

This guide will help you set up and configure the camera module for the Wearable Pin project on your Raspberry Pi.

## Prerequisites

- Raspberry Pi (Model 3, 4, or Zero 2 W recommended)
- Raspberry Pi Camera Module (v2, v3, or HQ Camera)
- Raspberry Pi OS (Bullseye or later)
- Internet connection for installing packages

## Hardware Setup

1. **Power off your Raspberry Pi** completely before connecting the camera.

2. **Connect the camera module:**
   - Locate the Camera Serial Interface (CSI) port on your Raspberry Pi
   - Gently pull up the plastic clip on the CSI port
   - Insert the camera ribbon cable with the blue side facing the Ethernet port (silver contacts facing away)
   - Push the plastic clip back down to secure the cable

3. **Power on your Raspberry Pi**

## Software Configuration

### 1. Enable the Camera Interface

#### Using raspi-config (Command Line):
```bash
sudo raspi-config
```
- Select `Interface Options`
- Select `Camera`
- Select `Yes` to enable the camera
- Reboot when prompted

#### Alternative Method (Direct):
```bash
# Add or uncomment the camera settings in config.txt
sudo nano /boot/config.txt

# Ensure these lines are present:
# camera_auto_detect=1
# start_x=1

# Reboot
sudo reboot
```

### 2. Install Required Packages

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install -y python3 python3-pip

# Install picamera2 library (for newer Pi OS)
sudo apt install -y python3-picamera2

# Install additional dependencies
sudo apt install -y python3-libcamera python3-kms++
```

### 3. Verify Camera Detection

```bash
# Check if the camera is detected
libcamera-hello --list-cameras

# You should see output like:
# Available cameras
# 0 : imx219 [3280x2464] (/base/soc/i2c0mux/i2c@1/imx219@10)
```

### 4. Test Camera Capture

```bash
# Take a test photo
libcamera-still -o test.jpg

# Take a 5-second video
libcamera-vid -t 5000 -o test.h264
```

## Installing the Wearable Pin Camera Software

### 1. Clone or Copy the Project

```bash
# Create project directory
mkdir -p /home/pi/wearable-pin
cd /home/pi/wearable-pin

# Copy the pi directory from your repository
# (Adjust the path as needed)
```

### 2. Run the Test Suite

```bash
cd /home/pi/wearable-pin/pi
python3 test_camera.py
```

The test suite will verify:
- Configuration settings
- Camera detection
- Camera initialization
- Image capture functionality

### 3. Test Manual Image Capture

```bash
# Capture a single image
python3 capture_image.py

# Check the captured image
ls -lh /home/pi/wearable-pin/images/
```

### 4. Configure the Service

```bash
# Copy the service file to systemd directory
sudo cp services/camera.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable camera.service

# Start the service
sudo systemctl start camera.service

# Check service status
sudo systemctl status camera.service
```

### 5. Monitor the Service

```bash
# View service logs
sudo journalctl -u camera.service -f

# View application logs
tail -f /home/pi/wearable-pin/camera.log
```

## Configuration

Edit `/home/pi/wearable-pin/pi/config.py` to customize:

- **Camera Resolution**: `CAMERA_RESOLUTION = (1920, 1080)`
- **Capture Interval**: `CAPTURE_INTERVAL = 5` (seconds)
- **Image Format**: `IMAGE_FORMAT = 'jpeg'`
- **Storage Location**: `IMAGE_DIR = '/home/pi/wearable-pin/images'`
- **Maximum Images**: `MAX_IMAGES = 1000`

After changing configuration, restart the service:
```bash
sudo systemctl restart camera.service
```

## Troubleshooting

### Camera Not Detected

1. **Check physical connection:**
   - Ensure the ribbon cable is properly inserted
   - Try a different CSI port if available
   - Check for visible damage to the cable

2. **Verify camera interface is enabled:**
   ```bash
   vcgencmd get_camera
   # Should show: supported=1 detected=1
   ```

3. **Check for conflicts:**
   ```bash
   # Make sure no other process is using the camera
   sudo fuser -v /dev/video0
   ```

### Permission Issues

If you encounter permission errors:
```bash
# Add user to video group
sudo usermod -aG video $USER

# Logout and login again, or reboot
```

### Service Fails to Start

1. **Check service logs:**
   ```bash
   sudo journalctl -u camera.service -n 50
   ```

2. **Verify Python path and script location:**
   ```bash
   which python3
   ls -l /home/pi/wearable-pin/pi/capture_image.py
   ```

3. **Test script manually:**
   ```bash
   cd /home/pi/wearable-pin/pi
   python3 capture_image.py --continuous
   # Press Ctrl+C to stop
   ```

### Low Disk Space

If you run out of disk space:
```bash
# Check disk usage
df -h

# Clean up old images manually
rm /home/pi/wearable-pin/images/capture_*.jpeg

# Or adjust MAX_IMAGES in config.py to a lower value
```

## Performance Optimization

### For Better Image Quality
```python
# In config.py
CAMERA_RESOLUTION = (3280, 2464)  # Maximum for Camera Module v2
IMAGE_QUALITY = 95
```

### For Lower Resource Usage
```python
# In config.py
CAMERA_RESOLUTION = (1280, 720)  # Lower resolution
IMAGE_QUALITY = 75
CAPTURE_INTERVAL = 10  # Less frequent captures
```

### For Faster Startup
```python
# In config.py
CAMERA_RESOLUTION = (640, 480)  # Minimum resolution
```

## Additional Resources

- [Raspberry Pi Camera Documentation](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [picamera2 Library Documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Raspberry Pi Forums - Camera](https://forums.raspberrypi.com/viewforum.php?f=43)

## Support

If you encounter issues not covered in this guide, please:
1. Check the application logs in `/home/pi/wearable-pin/camera.log`
2. Review the service logs with `sudo journalctl -u camera.service`
3. Run the test suite to identify specific failures
4. Consult the troubleshooting section above
