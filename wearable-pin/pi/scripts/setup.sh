#!/bin/bash
#
# Setup script for Raspberry Pi wearable-pin project
# Installs dependencies and configures the system
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PI_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Wearable Pin - Setup Script"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
echo ""
echo "Installing required packages..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-picamera2 \
    git \
    systemd

# Check OS version (Arducam requires Raspberry Pi OS, not Raspbian)
echo ""
echo "Checking OS compatibility..."
if [ -f /etc/os-release ]; then
    if grep -qi "raspbian" /etc/os-release; then
        echo "WARNING: Raspbian detected. Arducam 16MP requires Raspberry Pi OS (not Raspbian)."
        echo "Please upgrade to Raspberry Pi OS for Arducam support."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "Raspberry Pi OS detected - compatible with Arducam"
    fi
fi

# Enable camera interface
echo ""
echo "Checking camera interface..."
if ! vcgencmd get_camera 2>/dev/null | grep -q "supported=1"; then
    echo "Warning: Camera interface may not be enabled."
    echo "For Arducam 16MP:"
    echo "  1. Run: sudo raspi-config"
    echo "  2. Navigate to: Interface Options -> Camera -> Enable"
    echo "  3. Select 'Yes' to enable camera interface"
    echo "  4. Reboot after enabling"
    read -p "Press Enter to continue (or Ctrl+C to exit and enable camera)..."
fi

# Check for Arducam specifically
echo ""
echo "Checking for Arducam camera..."
if libcamera-hello --list-cameras 2>/dev/null | grep -qi "imx519\|arducam"; then
    echo "Arducam 16MP IMX519 detected!"
    echo "Camera will be configured for 16MP (4656 x 3496) resolution"
elif libcamera-hello --list-cameras 2>/dev/null | grep -q "camera"; then
    echo "Standard Raspberry Pi camera detected"
    echo "Camera will use configured resolution"
else
    echo "Warning: No camera detected. Please check:"
    echo "  1. Camera is properly connected to CSI port"
    echo "  2. Camera interface is enabled"
    echo "  3. For Arducam: Ensure you're using Raspberry Pi OS (not Raspbian)"
    libcamera-hello --list-cameras 2>&1 || echo "  (libcamera-hello not available)"
fi

# Create image directory
echo ""
echo "Creating image directory..."
mkdir -p ~/wearable-pin/images

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x "$SCRIPT_DIR"/*.sh

# Add user to video group if needed
if ! groups | grep -q video; then
    echo ""
    echo "Adding user to video group..."
    sudo usermod -a -G video "$USER"
    echo "Note: You may need to log out and back in for this to take effect"
fi

# Test camera
echo ""
echo "Testing camera..."
cd "$PI_DIR"
if python3 test_camera.py; then
    echo "Camera test passed!"
else
    echo "Warning: Camera test failed. Check camera connection and permissions."
fi

echo ""
echo "=========================================="
echo "Setup completed!"
echo "=========================================="
echo ""
echo "To set up auto-updates, run:"
echo "  sudo cp $PI_DIR/services/update.service /etc/systemd/system/"
echo "  sudo cp $PI_DIR/services/update.timer /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable update.timer"
echo "  sudo systemctl start update.timer"

