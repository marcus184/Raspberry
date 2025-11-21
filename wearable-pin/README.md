# Wearable Pin - Raspberry Pi Camera Project

A lightweight camera capture system for Raspberry Pi, designed for wearable and portable applications.

## Overview

This project provides a simple yet robust interface for capturing images using the Raspberry Pi camera module. It includes configuration management, automatic image capture, and systemd service integration for running as a background service.

## Features

- 📷 **Easy Camera Control**: Simple Python interface for camera operations
- 🎯 **Arducam 5MP OV5647 Support**: Full support for Arducam 5MP OV5647 (2592 x 1944 resolution, 1080p recommended)
- 🔍 **Auto-Detection**: Automatically detects camera type (Arducam OV5647, IMX519, or standard Pi camera)
- ⚙️ **Configurable Settings**: Centralized configuration for resolution, format, and timing
- 🧪 **Comprehensive Testing**: Built-in test suite to verify camera functionality
- 🔄 **System Service**: Run as a systemd service for automatic startup
- 🔁 **Auto-Updates**: Automatic code updates from GitHub every 2 minutes
- 📝 **Detailed Documentation**: Step-by-step setup and troubleshooting guide

## Quick Start

### Prerequisites

- Raspberry Pi (3/4/5 or Zero 2 W)
- **Arducam 5MP OV5647** (Recommended) or Arducam 16MP IMX519 or Raspberry Pi Camera Module (v2 or v3)
- Python 3.7+
- **Raspberry Pi OS** (Bullseye or later) or **Raspbian** (OV5647 works on both)

### Installation

1. Clone the repository:
```bash
cd ~
git clone <repository-url>
cd wearable-pin
```

2. Install dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-picamera2
```

3. Check environment (recommended for Pi Zero 2W):
```bash
cd pi
python3 check_environment.py
```

4. Test the camera:
```bash
python3 test_camera.py
```

### Usage

#### Capture a Single Image

```bash
python3 capture_image.py
```

Images are saved to `~/wearable-pin/images/` by default.

#### Run Tests

```bash
python3 test_camera.py
```

#### Install as System Service

```bash
sudo cp services/camera.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable camera.service
sudo systemctl start camera.service
```

Check service status:
```bash
sudo systemctl status camera.service
```

## Project Structure

```
wearable-pin/
├── pi/
│   ├── capture_image.py      # Main camera capture module
│   ├── config.py              # Configuration settings
│   ├── test_camera.py         # Test suite
│   ├── scripts/
│   │   ├── deploy.sh          # Initial deployment script
│   │   ├── update.sh          # Auto-update script
│   │   └── setup.sh           # Setup script
│   └── services/
│       ├── camera.service     # Systemd service file
│       ├── update.service     # Auto-update service
│       └── update.timer       # Auto-update timer (every 2 min)
├── scripts/
│   ├── deploy.sh              # Mac deployment script
│   └── quick-deploy.sh        # Quick deployment helper
├── docs/
│   ├── pi_camera_setup.md     # Detailed setup guide
│   └── deployment.md          # Deployment workflow guide
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Configuration

Edit `pi/config.py` to customize settings:

```python
# Camera type: 'standard' for OV5647, 'arducam_16mp' for IMX519, or 'auto'
CAMERA_TYPE = 'standard'  # For Arducam 5MP OV5647 (works as standard camera)

# Camera settings
# Arducam 5MP OV5647: Max resolution 2592 x 1944 (5MP)
CAMERA_RESOLUTION = (1920, 1080)  # 1080p recommended for OV5647
# CAMERA_RESOLUTION = (2592, 1944)  # Full 5MP for OV5647
# CAMERA_RESOLUTION = (1280, 720)   # 720p fastest option
CAMERA_FRAMERATE = 30             # Frames per second
CAMERA_ROTATION = 0               # Rotation (0, 90, 180, 270)

# Image settings
IMAGE_FORMAT = 'jpeg'             # Format (jpeg, png)
IMAGE_QUALITY = 85                # JPEG quality (1-100)
IMAGE_DIR = '~/wearable-pin/images'  # Save directory
```

## Deployment & Auto-Updates

This project includes automated deployment and update capabilities:

### Initial Setup on Raspberry Pi

1. **Quick Setup** (recommended):
```bash
cd ~
git clone https://github.com/marcus184/Raspberry.git wearable-pin
cd wearable-pin/wearable-pin/pi
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/deploy.sh
```

2. **Manual Setup**:
   - Clone the repository
   - Install dependencies
   - Set up systemd services (see [Deployment Guide](docs/deployment.md))

### Auto-Update System

The Raspberry Pi automatically checks for updates from GitHub every 2 minutes and restarts the camera service when changes are detected.

- **Update Timer**: Runs every 2 minutes
- **Update Service**: Pulls latest code from GitHub
- **Auto-Restart**: Camera service restarts automatically after updates

### Deploying from Mac

To push code updates to GitHub and optionally trigger immediate update on Pi:

```bash
# From the wearable-pin directory
./scripts/deploy.sh "Your commit message"

# Or use the quick deploy script
./scripts/quick-deploy.sh "Your commit message"
```

The Pi will automatically pick up changes within 2 minutes, or you can trigger an immediate update via SSH.

For detailed deployment instructions, see [Deployment Guide](docs/deployment.md).

## Documentation

For detailed setup instructions, troubleshooting, and hardware configuration, see:
- [Pi Camera Setup Guide](docs/pi_camera_setup.md)
- [Deployment Guide](docs/deployment.md)

## Requirements

- Python 3.7+
- picamera2 (for Raspberry Pi OS Bullseye+)
- Raspberry Pi with camera module

## Development

### Running Tests

```bash
cd pi
python3 test_camera.py
```

The test suite includes:
- Configuration validation
- Camera initialization tests
- Image capture tests
- Cleanup verification

### Environment Check (Pi Zero 2W)

For Raspberry Pi Zero 2W, run a comprehensive environment check:

```bash
cd pi
python3 check_environment.py
```

This checks:
- Pi model detection
- OS compatibility
- Camera interface status
- Python packages
- System resources (memory, disk)
- Configuration settings
- Camera initialization

### Mock Mode

The camera module automatically runs in mock mode when `picamera2` is not available, allowing development and testing on non-Raspberry Pi systems.

## Troubleshooting

### Camera Not Detected

```bash
vcgencmd get_camera
# Should show: supported=1 detected=1
```

### Enable Camera Interface

```bash
sudo raspi-config
# Navigate to Interface Options → Camera → Enable
sudo reboot
```

### Permission Issues

```bash
sudo usermod -a -G video $USER
# Log out and back in
```

For more troubleshooting, see [docs/pi_camera_setup.md](docs/pi_camera_setup.md).

## License

This project is part of the Raspberry peripheral connection suite.

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- Tests pass before submitting
- Documentation is updated for new features

## Support

For issues or questions:
- Check the [setup guide](docs/pi_camera_setup.md)
- Review existing issues
- Open a new issue with details

## Related Projects

Part of the Raspberry Pi peripherals connection project.
