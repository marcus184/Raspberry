# Button Camera Capture Setup Guide

## Quick Start

1. **Connect Button:**
   - One side to GPIO 18
   - Other side to GND
   - Use pull-up resistor (internal, handled by gpiozero)

2. **Install Dependencies:**
   ```bash
   sudo apt-get install -y libcamera-apps python3-gpiozero
   ```

3. **Enable Camera:**
   ```bash
   sudo raspi-config
   # Interface Options → Camera → Enable
   ```

4. **Run Script:**
   ```bash
   cd ~/wearable-pin/wearable-pin/pi
   chmod +x button_capture.py
   python3 button_capture.py
   ```

5. **Press Button to Capture!**

## Hardware Setup

### Button Connection
```
Button Pin 1 → GPIO 4 (Physical Pin 7)
Button Pin 2 → GND (Physical Pin 6 or 14)
```

**GPIO Pinout (Pi Zero 2W):**
```
    3.3V  [1] [2]  5V
   GPIO2  [3] [4]  5V
   GPIO3  [5] [6]  GND
   GPIO4  [7] [8]  GPIO14  ← Button here (GPIO 4)
     GND  [9] [10] GPIO15
  GPIO17 [11] [12] GPIO18
  GPIO27 [13] [14] GND     ← GND here
  GPIO22 [15] [16] GPIO23
    3.3V [17] [18] GPIO24
  GPIO10 [19] [20] GND
   GPIO9 [21] [22] GPIO25
  GPIO11 [23] [24] GPIO8
     GND [25] [26] GPIO7
```

### Button Types
- **Momentary push button** (recommended)
- **Tactile switch** (works well)
- Any normally-open switch

## Configuration

Edit `button_config.py` to change:
- GPIO pin number
- Image resolution
- Save location
- Camera settings

## Usage

### Basic Usage
```bash
python3 button_capture.py
```

### Test Button Only (No Camera)
```bash
# Test button functionality without camera
python3 button_capture.py --test

# Or short form
python3 button_capture.py -t
```

**Test mode output:**
```
==================================================
Button Test Mode
==================================================
Testing button on GPIO 4
Press the button to test...
Press Ctrl+C to exit
==================================================

Waiting for button press...
[2024-01-01 12:00:00] Button pressed! (Count: 1)
[2024-01-01 12:00:05] Button pressed! (Count: 2)
```

This is useful for:
- Testing button wiring
- Verifying GPIO pin works
- Debugging button issues
- Testing without camera connected

### Run in Background
```bash
nohup python3 button_capture.py > /tmp/button_camera.log 2>&1 &
```

### Run on Boot (systemd)
Create `/etc/systemd/system/button-camera.service`:
```ini
[Unit]
Description=Button Camera Capture
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/wearable-pin/wearable-pin/pi
ExecStart=/usr/bin/python3 /home/pi/wearable-pin/wearable-pin/pi/button_capture.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable button-camera.service
sudo systemctl start button-camera.service
```

## Troubleshooting

**Button not working:**
```bash
# Test GPIO
gpio readall  # If installed
# Or test with simple script
python3 -c "from gpiozero import Button; b = Button(4); b.wait_for_press(); print('Button works!')"
```

**Camera not found:**
```bash
# Check camera
rpicam-still --list-cameras
# Or
libcamera-hello --list-cameras
vcgencmd get_camera

# Test camera manually
rpicam-still -o test.jpg
```

**Permission errors:**
```bash
# Add to video group
sudo usermod -a -G video $USER
# Log out and back in
```

**Script won't run:**
```bash
# Make executable
chmod +x button_capture.py

# Check dependencies
python3 -c "import picamera2; import gpiozero; print('OK')"
```

## Changing GPIO Pin

Edit `button_config.py`:
```python
BUTTON_PIN = 17  # Change to your GPIO pin
```

Or edit `button_capture.py` directly:
```python
BUTTON_PIN = 4  # Line 23 (currently set to GPIO 4)
```

## Changing Save Location

Edit `button_config.py`:
```python
SAVE_DIR = "~/captures"  # Change to your location
```

Or edit `button_capture.py`:
```python
SAVE_DIR = os.path.expanduser("~/captures")  # Line 24
```

## Multiple Buttons (Future)

To add multiple buttons for different functions:
- Button 1 (GPIO 18): Capture image
- Button 2 (GPIO 17): Change resolution
- Button 3 (GPIO 27): Delete last image

## Success Indicators

- Script starts without errors
- "Camera ready!" message appears
- "Ready! Press button..." message shows
- Button press triggers capture
- Image file appears in save directory
- File size is reasonable (~1-2MB for 1080p)

