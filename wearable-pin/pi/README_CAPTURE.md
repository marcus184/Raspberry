# Camera Capture Command Guide

## Quick Start

Capture an image with default settings:
```bash
cd ~/wearable-pin/wearable-pin/pi
python3 capture_image.py
```

Image will be saved to: `~/wearable-pin/images/capture_YYYYMMDD_HHMMSS.jpg`

## Command Options

### Basic Usage
```bash
# Default capture (auto filename, default location)
python3 capture_image.py

# Save with custom filename
python3 capture_image.py -o myphoto.jpg

# Save to custom directory
python3 capture_image.py -d /home/pi/Pictures

# Custom filename and directory
python3 capture_image.py -o test.jpg -d /tmp/captures
```

### Resolution Options
```bash
# Capture at 1080p (recommended for Pi Zero 2W)
python3 capture_image.py -r 1920 1080

# Capture at full 5MP (2592x1944)
python3 capture_image.py -r 2592 1944

# Capture at 720p (fastest)
python3 capture_image.py -r 1280 720
```

### Quality Settings
```bash
# High quality (larger file)
python3 capture_image.py -q 95

# Lower quality (smaller file, faster)
python3 capture_image.py -q 70
```

### Verbose Output
```bash
# Show detailed information
python3 capture_image.py -v
```

### Combined Options
```bash
# Full example with all options
python3 capture_image.py -o myphoto.jpg -d /home/pi/Pictures -r 1920 1080 -q 85 -v
```

## Default Settings

- **Camera Type**: Standard (Arducam 5MP OV5647)
- **Resolution**: 1920x1080 (1080p)
- **Format**: JPEG
- **Quality**: 85
- **Save Location**: `~/wearable-pin/images/`

## Changing Default Save Location

Edit `config.py`:
```python
IMAGE_DIR = '/home/pi/Pictures'  # Change to your preferred location
```

Or use command-line:
```bash
python3 capture_image.py -d /path/to/save/location
```

## Examples for Raspberry Pi Zero 2W

**Fast capture (720p):**
```bash
python3 capture_image.py -r 1280 720
```

**High quality (5MP):**
```bash
python3 capture_image.py -r 2592 1944 -q 95
```

**Save to USB drive:**
```bash
python3 capture_image.py -d /media/usb/captures
```

**Save with timestamp in filename:**
```bash
python3 capture_image.py -o "photo_$(date +%Y%m%d_%H%M%S).jpg"
```

## Troubleshooting

**Camera not found:**
```bash
# Check camera detection
libcamera-hello --list-cameras
vcgencmd get_camera

# Enable camera interface
sudo raspi-config  # Interface Options → Camera → Enable
```

**Permission denied:**
```bash
# Add user to video group
sudo usermod -a -G video $USER
# Log out and back in
```

**Save location doesn't exist:**
```bash
# Create directory
mkdir -p /path/to/save/location
```

## Integration with Scripts

**Capture in a script:**
```bash
#!/bin/bash
cd ~/wearable-pin/wearable-pin/pi
python3 capture_image.py -o "capture_$(date +%Y%m%d_%H%M%S).jpg"
```

**Cron job (capture every hour):**
```bash
# Edit crontab
crontab -e

# Add line:
0 * * * * cd /home/pi/wearable-pin/wearable-pin/pi && python3 capture_image.py
```

