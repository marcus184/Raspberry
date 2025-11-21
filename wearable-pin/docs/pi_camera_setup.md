# Raspberry Pi Camera Setup Guide

This guide will help you set up the Raspberry Pi camera module for the wearable pin project.

## Supported Cameras

This project supports:
- **Arducam 5MP OV5647** (Recommended) - 5MP resolution (2592 x 1944), 1080p recommended
- **Arducam 16MP IMX519** - 16MP resolution (4656 x 3496)
- **Standard Raspberry Pi Camera** (v2, v3, HQ Camera)

## Prerequisites

- Raspberry Pi (3/4/5 or **Zero 2 W** recommended)
- **Arducam 5MP OV5647** (Recommended) or Arducam 16MP IMX519 or Raspberry Pi Camera Module (v2 or v3)
- **Raspberry Pi OS** (Bullseye or later) or **Raspbian** (OV5647 works on both, IMX519 requires Raspberry Pi OS)
- Python 3.7 or higher

### Raspberry Pi Zero 2W Considerations

The **Raspberry Pi Zero 2W** is fully supported with the following considerations:

- **Memory**: 512MB RAM - sufficient for 16MP captures but may be slower
- **Performance**: Full 16MP (4656x3496) works but capture time is ~2-3 seconds
- **Recommended Resolution**: For faster captures, consider 4K (3840x2160) or 1080p (1920x1080)
- **Power**: Ensure adequate power supply (2.5A recommended when using camera)
- **CSI Port**: Compatible with standard CSI camera connector

**Quick Setup Check**: Run `python3 check_environment.py` to verify your Pi Zero 2W setup.

## Hardware Setup

### For Arducam 5MP OV5647

1. **Power off your Raspberry Pi** before connecting the camera.

2. **Connect the Arducam OV5647:**
   - Locate the CSI (Camera Serial Interface) port on your Raspberry Pi (between HDMI and audio jack)
   - Gently pull up on the edges of the plastic clip
   - Insert the camera ribbon cable with the contacts facing the correct orientation
   - Push the plastic clip back down to secure the cable
   - **Important**: Ensure the cable is fully inserted and secured

3. **Power on your Raspberry Pi**

### For Arducam 16MP IMX519

1. **Power off your Raspberry Pi** before connecting the camera.

2. **Connect the Arducam:**
   - Locate the CSI (Camera Serial Interface) port on your Raspberry Pi (between HDMI and audio jack)
   - Gently pull up on the edges of the plastic clip
   - Insert the camera ribbon cable with the contacts facing the correct orientation
   - Push the plastic clip back down to secure the cable
   - **Important**: Ensure the cable is fully inserted and secured

3. **Power on your Raspberry Pi**

### For Standard Raspberry Pi Camera

1. **Power off your Raspberry Pi** before connecting the camera module.

2. **Connect the Camera Module:**
   - Locate the camera port on your Raspberry Pi (between HDMI and audio jack)
   - Gently pull up on the edges of the plastic clip
   - Insert the camera ribbon cable with the blue side facing the Ethernet/USB ports
   - Push the plastic clip back down to secure the cable

3. **Power on your Raspberry Pi**

## Software Setup

### 1. Verify OS Compatibility

**For Arducam 5MP OV5647**: Works on both **Raspberry Pi OS** and **Raspbian**.

**For Arducam 16MP IMX519**: Requires **Raspberry Pi OS** (not Raspbian).

Check your OS:
```bash
cat /etc/os-release
```

Both OS versions work for OV5647. Only Raspberry Pi OS works for IMX519.

### 2. Enable the Camera Interface

```bash
sudo raspi-config
```

Navigate to:
- `Interface Options` → `Camera` → `Yes`
- **For Arducam**: Select "Yes" to enable camera interface
- **For standard Pi camera**: Select "Yes" to enable camera interface
- **Do NOT** enable "Legacy Camera" - use the standard camera interface

Reboot after enabling:
```bash
sudo reboot
```

### 3. Verify Camera Detection

After reboot, verify your camera is detected:

```bash
# List all detected cameras
libcamera-hello --list-cameras
```

**For Arducam 5MP OV5647**, you should see output mentioning "ov5647" or standard camera:
```
Available cameras
-----------------
0 : ov5647 [2592x1944] (/base/soc/i2c0mux/i2c@1/ov5647@36)
```

**For Arducam 16MP IMX519**, you should see output mentioning "imx519":
```
Available cameras
-----------------
0 : imx519 [4656x3496] (/base/soc/i2c0mux/i2c@1/imx519@1a)
```

**For standard Pi camera**, you'll see the standard camera module listed.

### 4. Install Required Packages

For Raspberry Pi OS Bullseye or later (required for Arducam):

```bash
sudo apt-get update
sudo apt-get install -y python3-picamera2 python3-pip libcamera-apps
```

**Note**: Arducam 16MP requires `python3-picamera2` and does NOT work with the legacy `python3-picamera` package.

### 5. Configure Camera Type

Edit `pi/config.py` to specify your camera type:

```python
# For Arducam 5MP OV5647 (Recommended)
CAMERA_TYPE = 'standard'  # OV5647 works as standard camera
CAMERA_RESOLUTION = (1920, 1080)  # 1080p recommended for OV5647
# CAMERA_RESOLUTION = (2592, 1944)  # Full 5MP for OV5647
# CAMERA_RESOLUTION = (1280, 720)   # 720p fastest option

# For Arducam 16MP IMX519
CAMERA_TYPE = 'arducam_16mp'
CAMERA_RESOLUTION = (4656, 3496)  # Full 16MP resolution

# For standard Raspberry Pi camera
CAMERA_TYPE = 'standard'
CAMERA_RESOLUTION = (1920, 1080)  # Or your preferred resolution

# Auto-detect (recommended)
CAMERA_TYPE = 'auto'  # Will automatically detect camera type
```

### 6. Install Project Dependencies

Clone or copy the wearable-pin project to your Raspberry Pi:

```bash
cd ~
git clone https://github.com/marcus184/Raspberry.git wearable-pin
cd wearable-pin/wearable-pin/pi
```

### 7. Test the Camera

Run the test script to verify everything is working:

```bash
python3 test_camera.py
```

**For Arducam 5MP OV5647**, you should see:
- "Detected standard Raspberry Pi camera (or Arducam OV5647)"
- Resolution: (1920, 1080) or your configured resolution
- Successful image capture

**For Arducam 16MP IMX519**, you should see:
- "Detected Arducam 16MP IMX519 camera"
- Resolution: (4656, 3496) or your configured resolution
- Successful image capture

**For standard camera**, you should see:
- "Detected standard Raspberry Pi camera"
- Successful image capture

### 8. Capture a Test Image

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

Edit `pi/config.py` to customize settings:

```python
# Camera type: 'standard' for OV5647, 'arducam_16mp' for IMX519, or 'auto'
CAMERA_TYPE = 'standard'  # For Arducam 5MP OV5647 (works as standard camera)

# Camera settings
# Arducam 5MP OV5647: Max resolution 2592 x 1944 (5MP)
# Arducam 16MP IMX519: Max resolution 4656 x 3496 (16MP)
CAMERA_RESOLUTION = (1920, 1080)  # 1080p recommended for OV5647
# CAMERA_RESOLUTION = (2592, 1944)  # Full 5MP for OV5647
# CAMERA_RESOLUTION = (1280, 720)   # 720p fastest option
CAMERA_FRAMERATE = 30             # Frames per second
CAMERA_ROTATION = 0               # Rotation in degrees (0, 90, 180, 270)

# Image settings
IMAGE_FORMAT = 'jpeg'             # Image format (jpeg, png)
IMAGE_QUALITY = 85                # JPEG quality (1-100)
IMAGE_DIR = '~/wearable-pin/images'  # Save location

# Capture settings
CAPTURE_DELAY = 0                 # Delay before capture (seconds)
```

### Arducam 5MP OV5647 Settings

The Arducam 5MP OV5647 supports:
- **Maximum Resolution**: 2592 x 1944 pixels (5MP)
- **Recommended Resolutions**: 
  - 1080p: 1920 x 1080 (recommended - best balance of quality and speed)
  - Full 5MP: 2592 x 1944 (higher quality, slower)
  - 720p: 1280 x 720 (fastest option)
- **File Size**: ~1-2MB for 1080p, ~2-5MB for 5MP
- **Compatibility**: Works on Raspbian and Raspberry Pi OS

### Arducam 16MP IMX519 Settings

The Arducam 16MP IMX519 supports:
- **Maximum Resolution**: 4656 x 3496 pixels (16MP)
- **Recommended Resolutions**: 
  - Full: 4656 x 3496 (works on all Pi models, slower on Pi Zero 2W)
  - 4K: 3840 x 2160 (recommended for Pi Zero 2W - good balance)
  - 1080p: 1920 x 1080 (fastest on Pi Zero 2W)
  - 720p: 1280 x 720 (very fast, lower quality)
- **File Size**: ~20-30MB for 16MP
- **Compatibility**: Requires Raspberry Pi OS (not Raspbian)

### Pi Zero 2W Optimization

For **Raspberry Pi Zero 2W** (512MB RAM) with **Arducam 5MP OV5647**, recommended settings in `config.py`:

```python
# Option 1: 1080p (recommended - best balance, ~0.5-1 second per capture)
CAMERA_RESOLUTION = (1920, 1080)

# Option 2: Full 5MP (higher quality, ~1-2 seconds per capture)
CAMERA_RESOLUTION = (2592, 1944)

# Option 3: 720p (fastest, ~0.3-0.5 second per capture)
CAMERA_RESOLUTION = (1280, 720)
```

**Memory Usage**: OV5647 JPEG images are approximately 1-5MB each. With 512MB total RAM, the system handles captures easily.

For **Arducam 16MP IMX519** on Pi Zero 2W:
```python
# Option 1: 1080p (fastest, ~0.5-1 second per capture)
CAMERA_RESOLUTION = (1920, 1080)

# Option 2: 4K (recommended - good quality, ~1-2 seconds per capture)
CAMERA_RESOLUTION = (3840, 2160)

# Option 3: Full 16MP (slower, ~2-3 seconds per capture)
CAMERA_RESOLUTION = (4656, 3496)
```

## Troubleshooting

### Camera Not Detected

```bash
# Check if camera is detected (may not work for Arducam)
vcgencmd get_camera

# For Arducam and modern cameras, use libcamera:
libcamera-hello --list-cameras
```

If not detected:

**For Arducam 16MP:**
- Verify you're using **Raspberry Pi OS** (not Raspbian)
- Check cable connection to CSI port
- Ensure camera interface is enabled in `raspi-config`
- Try: `libcamera-hello --list-cameras`
- Check camera is powered (some Arducam modules need external power)

**For standard Pi camera:**
- Check cable connection
- Ensure cable is inserted correctly (blue side orientation)
- Try a different cable or camera module

### Permission Errors

Add your user to the `video` group:

```bash
sudo usermod -a -G video $USER
```

Log out and back in for changes to take effect.

### Arducam-Specific Issues

**"Camera not detected" or "Error initializing camera":**

1. **Verify OS**: Arducam requires Raspberry Pi OS (not Raspbian)
   ```bash
   cat /etc/os-release
   ```

2. **Check camera detection**:
   ```bash
   libcamera-hello --list-cameras
   ```

3. **Verify camera interface is enabled**:
   ```bash
   sudo raspi-config
   # Interface Options -> Camera -> Enable
   ```

4. **Test camera directly**:
   ```bash
   libcamera-hello -t 0
   ```

5. **Check for IMX519 sensor**:
   ```bash
   libcamera-hello --list-cameras | grep -i imx519
   ```

**"Resolution not supported" errors:**

- Arducam 16MP maximum resolution is 4656 x 3496
- If you set a higher resolution, it will be automatically capped
- Lower resolutions (e.g., 1920x1080) work fine for faster captures

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
