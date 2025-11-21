# Raspberry Pi Camera Setup Guide

This guide will help you set up the Raspberry Pi camera module for the wearable pin project.

## Prerequisites

- Raspberry Pi (3/4/5 or Zero 2 W recommended)
- Raspberry Pi Camera Module (v2 or v3)
- Latest Raspberry Pi OS installed
- Python 3.7 or higher

## Hardware Setup

1. **Power off your Raspberry Pi** before connecting the camera module.

2. **Connect the Camera Module:**
   - Locate the camera port on your Raspberry Pi (between HDMI and audio jack)
   - Gently pull up on the edges of the plastic clip
   - Insert the camera ribbon cable with the blue side facing the Ethernet/USB ports
   - Push the plastic clip back down to secure the cable

3. **Power on your Raspberry Pi**

## Software Setup

### 1. Enable the Camera Interface

```bash
sudo raspi-config
```

Navigate to:
- `Interfacing Options` → `Camera` → `Yes`
- Or use: `Interface Options` → `Legacy Camera` → `No` (for newer Pi OS with libcamera)

Reboot after enabling:
```bash
sudo reboot
```

### 2. Install Required Packages

For Raspberry Pi OS Bullseye or later (recommended):

```bash
sudo apt-get update
sudo apt-get install -y python3-picamera2 python3-pip
```

For older systems using legacy camera stack:

```bash
sudo apt-get install -y python3-picamera python3-pip
```

### 3. Install Project Dependencies

Clone or copy the wearable-pin project to your Raspberry Pi:

```bash
cd ~
git clone <repository-url>
cd wearable-pin/pi
```

### 4. Test the Camera

Run the test script to verify everything is working:

```bash
python3 test_camera.py
```

You should see output indicating successful camera initialization and test image captures.

### 5. Capture a Test Image

Run the capture script manually:

```bash
python3 capture_image.py
```

Check the captured image in `~/wearable-pin/images/`

## Setting Up as a System Service

To run the camera capture automatically on boot:

### 1. Copy the Service File

```bash
sudo cp services/camera.service /etc/systemd/system/
```

### 2. Update Service File Paths

Edit the service file if your installation path differs:

```bash
sudo nano /etc/systemd/system/camera.service
```

Update `WorkingDirectory` and `ExecStart` paths if needed.

### 3. Enable and Start the Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable camera.service

# Start the service now
sudo systemctl start camera.service
```

### 4. Check Service Status

```bash
sudo systemctl status camera.service
```

### 5. View Service Logs

```bash
# View recent logs
sudo journalctl -u camera.service -n 50

# Follow logs in real-time
sudo journalctl -u camera.service -f
```

## Configuration

Edit `config.py` to customize settings:

```python
# Camera settings
CAMERA_RESOLUTION = (1920, 1080)  # Image resolution
CAMERA_FRAMERATE = 30             # Frames per second
CAMERA_ROTATION = 0               # Rotation in degrees (0, 90, 180, 270)

# Image settings
IMAGE_FORMAT = 'jpeg'             # Image format (jpeg, png)
IMAGE_QUALITY = 85                # JPEG quality (1-100)
IMAGE_DIR = '~/wearable-pin/images'  # Save location

# Capture settings
CAPTURE_DELAY = 0                 # Delay before capture (seconds)
```

## Troubleshooting

### Camera Not Detected

```bash
# Check if camera is detected
vcgencmd get_camera

# Should show: supported=1 detected=1
```

If not detected:
- Check cable connection
- Ensure cable is inserted correctly (blue side orientation)
- Try a different cable or camera module

### Permission Errors

Add your user to the `video` group:

```bash
sudo usermod -a -G video $USER
```

Log out and back in for changes to take effect.

### libcamera vs Legacy Stack

Recent Raspberry Pi OS versions use libcamera. If you have issues:

```bash
# Check which stack is available
libcamera-hello --list-cameras

# Or for legacy:
raspistill -t 0
```

### Import Errors

If you get `ImportError: No module named 'picamera2'`:

```bash
# For picamera2 (new):
sudo apt-get install -y python3-picamera2

# For picamera (legacy):
sudo apt-get install -y python3-picamera
```

### Service Won't Start

Check logs for errors:

```bash
sudo journalctl -u camera.service -n 100 --no-pager
```

Common issues:
- Incorrect paths in service file
- Python script not executable
- Missing dependencies
- Camera already in use by another process

## Additional Resources

- [Raspberry Pi Camera Documentation](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [picamera2 Library Documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Raspberry Pi Forums](https://forums.raspberrypi.com/)

## Project Structure

```
wearable-pin/
├── pi/
│   ├── capture_image.py      # Main camera capture module
│   ├── config.py              # Configuration settings
│   ├── test_camera.py         # Test suite
│   └── services/
│       └── camera.service     # Systemd service file
├── docs/
│   └── pi_camera_setup.md     # This file
├── .gitignore
└── README.md
```

## Support

For issues or questions, please open an issue on the project repository.
