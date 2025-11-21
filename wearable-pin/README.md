# Wearable Pin - Raspberry Pi Camera Project

A lightweight camera capture system for Raspberry Pi, designed for wearable and portable applications.

## Overview

This project provides a simple yet robust interface for capturing images using the Raspberry Pi camera module. It includes configuration management, automatic image capture, and systemd service integration for running as a background service.

## Features

- 📷 **Easy Camera Control**: Simple Python interface for camera operations
- ⚙️ **Configurable Settings**: Centralized configuration for resolution, format, and timing
- 🧪 **Comprehensive Testing**: Built-in test suite to verify camera functionality
- 🔄 **System Service**: Run as a systemd service for automatic startup
- 📝 **Detailed Documentation**: Step-by-step setup and troubleshooting guide

## Quick Start

### Prerequisites

- Raspberry Pi (3/4/5 or Zero 2 W)
- Raspberry Pi Camera Module (v2 or v3)
- Python 3.7+
- Raspberry Pi OS (Bullseye or later recommended)

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

3. Test the camera:
```bash
cd pi
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
│   └── services/
│       └── camera.service     # Systemd service file
├── docs/
│   └── pi_camera_setup.md     # Detailed setup guide
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Configuration

Edit `pi/config.py` to customize settings:

```python
# Camera settings
CAMERA_RESOLUTION = (1920, 1080)  # Image resolution
CAMERA_FRAMERATE = 30             # Frames per second
CAMERA_ROTATION = 0               # Rotation (0, 90, 180, 270)

# Image settings
IMAGE_FORMAT = 'jpeg'             # Format (jpeg, png)
IMAGE_QUALITY = 85                # JPEG quality (1-100)
IMAGE_DIR = '~/wearable-pin/images'  # Save directory
```

## Documentation

For detailed setup instructions, troubleshooting, and hardware configuration, see:
- [Pi Camera Setup Guide](docs/pi_camera_setup.md)

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
