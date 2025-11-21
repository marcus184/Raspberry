#!/bin/bash
#
# Initial deployment script for Raspberry Pi wearable-pin project
# Clones repository, installs dependencies, and sets up services
#

set -e

# Configuration
REPO_URL="${1:-https://github.com/marcus184/Raspberry.git}"
INSTALL_DIR="$HOME/wearable-pin"
BRANCH="main"

echo "=========================================="
echo "Wearable Pin - Raspberry Pi Deployment"
echo "=========================================="
echo ""

# Check if directory already exists
if [ -d "$INSTALL_DIR" ]; then
    echo "Directory $INSTALL_DIR already exists."
    read -p "Do you want to remove it and re-clone? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing directory..."
        rm -rf "$INSTALL_DIR"
    else
        echo "Using existing directory. Updating instead..."
        cd "$INSTALL_DIR"
        git pull origin "$BRANCH"
        exit 0
    fi
fi

# Clone repository
echo "Cloning repository from $REPO_URL..."
if ! git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"; then
    echo "ERROR: Failed to clone repository"
    exit 1
fi

cd "$INSTALL_DIR/wearable-pin/pi" || {
    echo "ERROR: Failed to change to pi directory"
    exit 1
}

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-picamera2 python3-pip

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x scripts/*.sh 2>/dev/null || true

# Set up systemd services
echo ""
echo "Setting up systemd services..."

# Copy and configure camera service
sudo cp services/camera.service /etc/systemd/system/
sudo sed -i "s|/home/pi/wearable-pin|$INSTALL_DIR/wearable-pin|g" /etc/systemd/system/camera.service

# Copy and configure update service
sudo cp services/update.service /etc/systemd/system/
sudo sed -i "s|/home/pi/wearable-pin|$INSTALL_DIR/wearable-pin|g" /etc/systemd/system/update.service

# Copy and configure update timer
sudo cp services/update.timer /etc/systemd/system/
sudo sed -i "s|/home/pi/wearable-pin|$INSTALL_DIR/wearable-pin|g" /etc/systemd/system/update.timer

# Reload systemd
sudo systemctl daemon-reload

# Enable services
echo ""
echo "Enabling services..."
sudo systemctl enable camera.service
sudo systemctl enable update.timer

# Start services
echo ""
echo "Starting services..."
sudo systemctl start update.timer
sudo systemctl start camera.service

# Check status
echo ""
echo "Service status:"
sudo systemctl status camera.service --no-pager -l || true
sudo systemctl status update.timer --no-pager -l || true

echo ""
echo "=========================================="
echo "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  - Check service logs: sudo journalctl -u camera.service -f"
echo "  - Check update logs: sudo journalctl -u update.service -f"
echo "  - Test camera: cd $INSTALL_DIR/wearable-pin/pi && python3 test_camera.py"

