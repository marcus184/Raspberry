# Wearable Pin - Raspberry Pi Camera Project

A Raspberry Pi-based camera system for continuous image capture, designed for wearable applications.

## Overview

This project provides a complete solution for capturing images using a Raspberry Pi camera module. It includes scripts for image capture, camera testing, system service configuration, and comprehensive documentation.

## Features

- **Automated Image Capture**: Continuous or single-shot image capture modes
- **Configurable Settings**: Easily adjust resolution, quality, interval, and storage
- **System Service**: Run as a background service with automatic startup
- **Image Management**: Automatic cleanup of old images based on configurable limits
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Testing Suite**: Verify camera functionality before deployment

## Project Structure

```
wearable-pin/
├── pi/
│   ├── capture_image.py      # Main image capture script
│   ├── config.py              # Configuration settings
│   ├── test_camera.py         # Camera testing suite
│   └── services/
│       └── camera.service     # Systemd service file
├── docs/
│   └── pi_camera_setup.md     # Setup and configuration guide
├── .gitignore
└── README.md
```

## Quick Start

### Prerequisites

- Raspberry Pi (3, 4, or Zero 2 W recommended)
- Raspberry Pi Camera Module (v2, v3, or HQ Camera)
- Raspberry Pi OS (Bullseye or later)

### Installation

1. **Set up the hardware**: Connect the camera module to your Raspberry Pi's CSI port

2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y python3-picamera2
   ```

3. **Copy project files to your Pi**:
   ```bash
   mkdir -p /home/pi/wearable-pin
   cd /home/pi/wearable-pin
   # Copy the contents of this repository
   ```

4. **Test the camera**:
   ```bash
   cd /home/pi/wearable-pin/pi
   python3 test_camera.py
   ```

5. **Capture a test image**:
   ```bash
   python3 capture_image.py
   ```

For detailed setup instructions, see [docs/pi_camera_setup.md](docs/pi_camera_setup.md)

## Usage

### Single Image Capture

```bash
cd /home/pi/wearable-pin/pi
python3 capture_image.py
```

Images are saved to `/home/pi/wearable-pin/images/` by default.

### Continuous Capture Mode

```bash
python3 capture_image.py --continuous
```

This will capture images at the interval specified in `config.py` (default: 5 seconds).

### Running as a Service

Install and enable the systemd service for automatic startup:

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

View logs:
```bash
sudo journalctl -u camera.service -f
```

## Configuration

Edit `pi/config.py` to customize the camera behavior:

- **Resolution**: `CAMERA_RESOLUTION = (1920, 1080)`
- **Capture Interval**: `CAPTURE_INTERVAL = 5` (seconds)
- **Image Format**: `IMAGE_FORMAT = 'jpeg'`
- **Storage Location**: `IMAGE_DIR = '/home/pi/wearable-pin/images'`
- **Max Images**: `MAX_IMAGES = 1000`
- **Image Quality**: `IMAGE_QUALITY = 85` (1-100)

After changing configuration, restart the service if running:
```bash
sudo systemctl restart camera.service
```

## Testing

Run the complete test suite to verify camera functionality:

```bash
cd /home/pi/wearable-pin/pi
python3 test_camera.py
```

The test suite checks:
- Configuration validation
- Camera detection
- Camera initialization
- Image capture functionality

## Documentation

- [Complete Setup Guide](docs/pi_camera_setup.md) - Detailed installation and configuration instructions
- [Troubleshooting](docs/pi_camera_setup.md#troubleshooting) - Common issues and solutions

## File Descriptions

- **capture_image.py**: Main script for capturing images from the camera. Supports single-shot and continuous modes.
- **config.py**: Configuration file containing all customizable settings for camera operation.
- **test_camera.py**: Automated test suite to verify camera hardware and software functionality.
- **services/camera.service**: Systemd service file for running the capture script as a background service.

## Requirements

- Python 3.7+
- picamera2 library
- libcamera
- Raspberry Pi OS Bullseye or later

## License

This project is open source and available for educational and personal use.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For setup instructions and troubleshooting, see the [Setup Guide](docs/pi_camera_setup.md).
