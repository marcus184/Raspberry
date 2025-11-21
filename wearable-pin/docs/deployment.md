# Deployment Guide - Wearable Pin Project

This guide covers the complete deployment workflow for the Wearable Pin Raspberry Pi project, including initial setup, auto-updates, and Mac-side deployment scripts.

## Overview

The deployment system consists of:

1. **Raspberry Pi Side**: Auto-update service that pulls code from GitHub every 2 minutes
2. **Mac Side**: Deployment scripts to push code updates to GitHub
3. **GitHub**: Central repository that serves as the source of truth

## Initial Setup on Raspberry Pi

### Option 1: Automated Setup (Recommended)

The easiest way to set up the project on your Raspberry Pi:

```bash
cd ~
git clone https://github.com/marcus184/Raspberry.git wearable-pin
cd wearable-pin/wearable-pin/pi
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/deploy.sh
```

This will:
- Install all required dependencies
- Set up systemd services
- Enable auto-updates
- Start the camera service

### Option 2: Manual Setup

If you prefer to set up manually:

1. **Clone the repository:**
```bash
cd ~
git clone https://github.com/marcus184/Raspberry.git wearable-pin
cd wearable-pin/wearable-pin/pi
```

2. **Install dependencies:**
```bash
sudo apt-get update
sudo apt-get install -y python3-picamera2 python3-pip
```

3. **Run setup script:**
```bash
chmod +x scripts/*.sh
./scripts/setup.sh
```

4. **Set up systemd services:**
```bash
# Copy service files
sudo cp services/camera.service /etc/systemd/system/
sudo cp services/update.service /etc/systemd/system/
sudo cp services/update.timer /etc/systemd/system/

# Update paths in service files if needed
sudo nano /etc/systemd/system/camera.service
sudo nano /etc/systemd/system/update.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable camera.service
sudo systemctl enable update.timer
sudo systemctl start update.timer
sudo systemctl start camera.service
```

## Auto-Update System

### How It Works

1. **Systemd Timer**: `update.timer` triggers every 2 minutes
2. **Update Service**: `update.service` runs the `update.sh` script
3. **Update Script**: 
   - Fetches latest changes from GitHub
   - Pulls updates if available
   - Restarts camera service if changes detected
   - Logs all activities

### Configuration

The update frequency is set in `pi/services/update.timer`:

```ini
[Timer]
OnBootSec=2min
OnUnitActiveSec=2min
```

To change the update frequency, edit this file and reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart update.timer
```

### Monitoring Updates

Check update service status:
```bash
# Check timer status
sudo systemctl status update.timer

# Check last update run
sudo systemctl status update.service

# View update logs
sudo journalctl -u update.service -f

# View recent update logs
sudo journalctl -u update.service -n 50
```

### Manual Update Trigger

To trigger an update immediately:
```bash
sudo systemctl start update.service
```

## Deploying from Mac

### Prerequisites

- Git repository cloned on your Mac
- SSH access to Raspberry Pi (optional, for immediate updates)
- GitHub repository access

### Basic Deployment

1. **Make your code changes**

2. **Deploy using the script:**
```bash
cd wearable-pin
./scripts/deploy.sh "Your commit message"
```

3. **Or use quick deploy:**
```bash
./scripts/quick-deploy.sh "Your commit message"
```

### Deployment Script Options

The `deploy.sh` script:
- Stages all changes
- Commits with your message
- Pushes to GitHub
- Optionally triggers immediate update on Pi via SSH

**Environment Variables** (optional):
```bash
# Set Pi hostname (default: raspberrypi.local)
export PI_HOST=192.168.1.100

# Set Pi username (default: pi)
export PI_USER=pi

# Set SSH key path (if using key-based auth)
export SSH_KEY=~/.ssh/id_rsa

# Then run deploy
./scripts/deploy.sh "Update message"
```

### Workflow Example

```bash
# 1. Make code changes
nano pi/config.py

# 2. Deploy to GitHub
./scripts/deploy.sh "Updated camera resolution"

# 3. Pi will auto-update within 2 minutes
# Or trigger immediately:
ssh pi@raspberrypi.local "sudo systemctl start update.service"
```

## Service Management

### Camera Service

```bash
# Check status
sudo systemctl status camera.service

# Start service
sudo systemctl start camera.service

# Stop service
sudo systemctl stop camera.service

# Restart service
sudo systemctl restart camera.service

# View logs
sudo journalctl -u camera.service -f
```

### Update Service

```bash
# Check timer status
sudo systemctl status update.timer

# Enable/disable auto-updates
sudo systemctl enable update.timer
sudo systemctl disable update.timer

# Start/stop timer
sudo systemctl start update.timer
sudo systemctl stop update.timer
```

## Troubleshooting

### Updates Not Working

1. **Check network connectivity:**
```bash
ping github.com
```

2. **Check git repository:**
```bash
cd ~/wearable-pin/wearable-pin
git status
git remote -v
```

3. **Check update service logs:**
```bash
sudo journalctl -u update.service -n 100
```

4. **Test update script manually:**
```bash
cd ~/wearable-pin/wearable-pin/pi
./scripts/update.sh
```

### Service Won't Start

1. **Check service status:**
```bash
sudo systemctl status camera.service
```

2. **Check logs:**
```bash
sudo journalctl -u camera.service -n 50
```

3. **Verify paths in service file:**
```bash
sudo cat /etc/systemd/system/camera.service
```

4. **Test script manually:**
```bash
cd ~/wearable-pin/wearable-pin/pi
python3 capture_image.py
```

### Git Authentication Issues

If you encounter authentication issues when pulling:

1. **Use HTTPS with token** (recommended):
   - Generate a GitHub personal access token
   - Update remote URL: `git remote set-url origin https://TOKEN@github.com/marcus184/Raspberry.git`

2. **Use SSH keys**:
   - Set up SSH keys on Pi
   - Update remote URL: `git remote set-url origin git@github.com:marcus184/Raspberry.git`

### Permission Issues

If scripts fail due to permissions:

```bash
# Make scripts executable
chmod +x ~/wearable-pin/wearable-pin/pi/scripts/*.sh

# Check service user
sudo cat /etc/systemd/system/update.service | grep User
```

## Best Practices

1. **Always test locally** before deploying
2. **Use descriptive commit messages** when deploying
3. **Monitor logs** after deployment to ensure updates work
4. **Keep Pi updated** with `sudo apt-get update && sudo apt-get upgrade`
5. **Backup configuration** before major changes

## Security Considerations

1. **GitHub Access**: Use personal access tokens or SSH keys, not passwords
2. **SSH Access**: Use key-based authentication for Pi access
3. **Service Permissions**: Services run as `pi` user with limited privileges
4. **Network Security**: Ensure Pi is on a secure network

## Advanced Configuration

### Custom Update Frequency

Edit `pi/services/update.timer`:
```ini
[Timer]
OnUnitActiveSec=5min  # Change to desired interval
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart update.timer
```

### Custom Branch

Edit `pi/scripts/update.sh`:
```bash
BRANCH="develop"  # Change from "main" to your branch
```

### Multiple Pi Deployment

To deploy to multiple Pis, use the deploy script with different hosts:
```bash
PI_HOST=pi1.local ./scripts/deploy.sh "Update message"
PI_HOST=pi2.local ./scripts/deploy.sh "Update message"
```

## Support

For issues or questions:
- Check service logs: `sudo journalctl -u update.service -f`
- Review [Pi Camera Setup Guide](pi_camera_setup.md)
- Check GitHub repository issues

