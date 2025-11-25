# Fresh Raspberry Pi OS Legacy 32-bit Lite Setup Plan

## Overview
Complete plan to set up a fresh Raspberry Pi OS Legacy 32-bit Lite installation, download the repository, and test the button functionality.

## Prerequisites
- ✅ Raspberry Pi Zero 2W
- ✅ Fresh Raspberry Pi OS Legacy 32-bit Lite installed on SD card
- ✅ Arducam 5MP OV5647 camera connected (optional for button test)
- ✅ PH0645 I2S microphone connected (optional for mic test)
- ✅ Button connected to GPIO 4 (camera) or GPIO 23 (microphone)
- ✅ Network connection (WiFi or Ethernet)
- ✅ SSH access or direct terminal access

## Phase 1: Initial Pi Setup

### Step 1.1: Boot Raspberry Pi
- Insert SD card with Pi OS Legacy 32-bit Lite
- Connect power supply
- Wait for boot (30-60 seconds)
- LED should stop blinking when ready

### Step 1.2: Initial Access
**Option A: SSH (if configured)**
```bash
ssh pi@raspberrypi.local
# Or use IP address: ssh pi@192.168.x.x
```

**Option B: Direct Terminal**
- Connect keyboard and monitor
- Login with default credentials (usually pi/raspberry)

### Step 1.3: Verify System
```bash
# Check OS version
cat /etc/os-release
# Should show: Raspberry Pi OS Legacy

# Check architecture
uname -m
# Should show: armv7l (32-bit)

# Check Pi model
cat /proc/device-tree/model
# Should show: Raspberry Pi Zero 2 W
```

### Step 1.4: Update System
```bash
# Update package lists
sudo apt-get update

# Upgrade system (optional but recommended)
sudo apt-get upgrade -y
```

## Phase 2: Install Dependencies

### Step 2.1: Install Git
```bash
sudo apt-get install -y git
```

### Step 2.2: Install libcamera-apps
```bash
# Install libcamera tools (for rpicam-still)
sudo apt-get install -y libcamera-apps

# Verify installation
which rpicam-still
rpicam-still --version
```

### Step 2.3: Install Python GPIO Library
```bash
# Install gpiozero for button handling
sudo apt-get install -y python3-gpiozero

# Verify installation
python3 -c "import gpiozero; print('gpiozero OK')"
```

### Step 2.4: Install Audio Tools (For Microphone)
```bash
# Install ALSA utilities for microphone recording
sudo apt-get install -y alsa-utils

# Verify installation
which arecord
arecord --version
```

### Step 2.5: Install Python Dependencies
```bash
# Install any other Python packages needed
sudo apt-get install -y python3-pip
```

## Phase 3: Enable Interfaces

### Step 3.1: Enable Camera Interface (If Testing Camera)
```bash
# Open configuration
sudo raspi-config
```

**Navigate:**
1. **Interface Options** (or **Interfacing Options**)
2. **Camera**
3. Select **Yes** to enable
4. **Finish**
5. Choose **Yes** to reboot

### Step 3.2: Enable I2S Interface (If Testing Microphone)
**Option A: Using raspi-config**
```bash
# Open configuration
sudo raspi-config
```

**Navigate:**
1. **Interface Options**
2. **I2S** (or **Audio**)
3. Select **Yes** to enable I2S
4. **Finish**
5. Choose **Yes** to reboot

**Option B: Manual Configuration (Recommended for PH0645)**
```bash
# Edit boot configuration
# Legacy OS: /boot/config.txt
# Newer OS: /boot/firmware/config.txt
sudo nano /boot/config.txt
```

**Add these THREE lines at the bottom:**
```
dtparam=i2s=on
dtoverlay=i2s-mmap
dtoverlay=googlevoicehat-soundcard
```

**Save:** `CTRL+O`, `ENTER`, `CTRL+X`

**Reboot:**
```bash
sudo reboot
```

### Step 3.3: Verify After Reboot
```bash
# After reboot, SSH back in

# Check camera status (if camera connected)
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test camera (if connected)
rpicam-still -o /tmp/test.jpg
ls -lh /tmp/test.jpg

# Check I2S microphone (if mic connected)
arecord -l
# Should show I2S audio device
```

## Phase 4: Clone Repository

### Step 4.1: Navigate to Home Directory
```bash
cd ~
pwd  # Should show /home/pi
```

### Step 4.2: Clone Repository
```bash
git clone https://github.com/marcus184/Raspberry.git wearable-pin
```

**If clone fails:**
- Check internet: `ping -c 3 github.com`
- Repository is public, should work without authentication

### Step 4.3: Navigate to Project
```bash
cd wearable-pin/wearable-pin/pi
ls -la  # Verify files are present
```

### Step 4.4: Make Script Executable
```bash
chmod +x button_capture.py
```

## Phase 5: Configure Buttons

### Step 5.1: Verify Camera Button Connection
**Hardware (Camera Button):**
- Button pin 1 → GPIO 4 (Physical Pin 7)
- Button pin 2 → GND (Physical Pin 6 or 14)

### Step 5.2: Verify Microphone Button Connection
**Hardware (Microphone Button):**
- Button pin 1 → GPIO 23 (Physical Pin 16)
- Button pin 2 → GND (Physical Pin 6 or 14)

**Physical Pin Layout:**
```
    3.3V  [1] [2]  5V
   GPIO2  [3] [4]  5V
   GPIO3  [5] [6]  GND     ← GND here
   GPIO4  [7] [8]  GPIO14  ← Button here (GPIO 4)
     GND  [9] [10] GPIO15
```

### Step 5.3: Verify GPIO Pins in Scripts
```bash
# Check camera button pin
cat button_capture.py | grep BUTTON_PIN
# Should show: BUTTON_PIN = 4

# Check microphone button pin
cat mic_test.py | grep BUTTON_PIN
# Should show: BUTTON_PIN = 23
```

## Phase 6: Test Buttons

### Step 6.1: Test Camera Button (No Camera)
```bash
# Run camera button test mode
python3 button_capture.py --test
```

### Step 6.2: Test Microphone Button (No Microphone)
```bash
# Run microphone button test mode
python3 mic_test.py --test
```

**Expected output:**
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

**What to verify:**
- ✓ Script starts without errors
- ✓ "Waiting for button press..." message appears
- ✓ Button press shows timestamp and count
- ✓ Multiple presses are detected

### Step 6.2: Troubleshoot Button Issues

**If button not detected:**
```bash
# Test GPIO manually
python3 -c "
from gpiozero import Button
import time
button = Button(4, pull_up=True)
print('Waiting for button press...')
button.wait_for_press()
print('Button works!')
"
```

**If permission errors:**
```bash
# Check user groups
groups
# Should include 'gpio' or 'gpiozero' group

# Add to gpio group if needed (usually not needed with gpiozero)
# gpiozero handles permissions automatically
```

**If wrong GPIO pin:**
```bash
# Edit button pin
nano button_capture.py
# Change: BUTTON_PIN = 4  to your GPIO pin
```

## Phase 7: Test Camera Capture (Optional)

### Step 7.1: Test Camera (If Connected)
```bash
# Test camera manually
rpicam-still -o /tmp/test.jpg
ls -lh /tmp/test.jpg
# Should show JPEG file
```

### Step 7.2: Test Full Camera Button Capture
```bash
# Run full camera capture mode
python3 button_capture.py
```

## Phase 8: Test Microphone Recording (Optional)

### Step 8.1: Test Microphone (If Connected)
```bash
# Test microphone manually
arecord -D hw:0,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav
ls -lh test.wav
# Should show WAV file

# Play back (if speaker connected)
aplay test.wav
```

### Step 8.2: List Audio Devices
```bash
# List available audio devices
python3 mic_test.py --list
# Or
arecord -l
```

### Step 8.3: Test Full Microphone Button Recording
```bash
# Run full microphone recording mode
python3 mic_test.py
```

**Expected output:**
```
==================================================
Button Camera Capture
==================================================
Button GPIO: 4
Resolution: 1920x1080
Save location: /home/pi/pictures
==================================================
✓ rpicam-still found
Save directory: /home/pi/pictures
Setting up button on GPIO 4...
Button ready!
Testing camera...
✓ Image captured: /home/pi/pictures/test_camera.jpg
  Size: 1234567 bytes (1.18 MB)
✓ Camera test successful
==================================================
Ready! Press button to capture image...
Press Ctrl+C to exit
==================================================
```

### Step 7.3: Verify Captured Images
```bash
# List captured images
ls -lh ~/pictures/

# Check image details
file ~/pictures/*.jpg
```

## Phase 9: Verify Complete Setup

### Step 9.1: Check All Components
```bash
# Verify git repository
cd ~/wearable-pin/wearable-pin/pi
git log -1

# Verify dependencies
which rpicam-still
which arecord
python3 -c "import gpiozero; print('OK')"

# Verify scripts
python3 button_capture.py --help
python3 mic_test.py --help
```

### Step 9.2: Final Test Sequence
```bash
# 1. Test camera button only
python3 button_capture.py --test
# Press button a few times, then Ctrl+C

# 2. Test microphone button only
python3 mic_test.py --test
# Press button a few times, then Ctrl+C

# 3. Test full camera capture (if camera connected)
python3 button_capture.py
# Press button to capture, then Ctrl+C

# 4. Test full microphone recording (if mic connected)
python3 mic_test.py
# Press button to record, then Ctrl+C

# 5. Verify files saved
ls -lh ~/pictures/     # Camera images
ls -lh ~/recordings/   # Microphone recordings
```

## Troubleshooting

### Button Not Working
```bash
# Check wiring
# Verify GPIO 4 to button, GND to button

# Test with simple script
python3 -c "from gpiozero import Button; b=Button(4); b.wait_for_press(); print('OK')"

# Check for conflicts
# Make sure no other process is using GPIO 4
```

### Camera Not Working
```bash
# Check camera interface
vcgencmd get_camera

# Enable if needed
sudo raspi-config  # Interface Options → Camera → Enable

# Test camera
rpicam-still -o test.jpg
```

### Repository Clone Fails
```bash
# Check internet
ping github.com

# Try again
git clone https://github.com/marcus184/Raspberry.git wearable-pin

# Check if directory exists
ls -la ~/wearable-pin
```

### Script Errors
```bash
# Check Python version
python3 --version
# Should be 3.7+

# Check dependencies
python3 -c "import gpiozero; print('gpiozero OK')"
which rpicam-still

# Check script permissions
ls -l button_capture.py
chmod +x button_capture.py
```

## Quick Setup Commands (Copy-Paste)

**Complete setup sequence:**
```bash
# 1. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install dependencies
sudo apt-get install -y git libcamera-apps python3-gpiozero alsa-utils

# 3. Enable interfaces
sudo raspi-config
# Interface Options → Camera → Enable (if camera)
# Interface Options → I2S → Enable (if microphone)
# Reboot

# 4. Clone repository
cd ~ && git clone https://github.com/marcus184/Raspberry.git wearable-pin

# 5. Setup project
cd wearable-pin/wearable-pin/pi
chmod +x button_capture.py mic_test.py

# 6. Test camera button
python3 button_capture.py --test

# 7. Test microphone button
python3 mic_test.py --test

# 8. Test full camera capture (if camera connected)
python3 button_capture.py

# 9. Test full microphone recording (if mic connected)
python3 mic_test.py
```

## Success Criteria

- [ ] Pi OS Legacy 32-bit Lite booted
- [ ] System updated
- [ ] Dependencies installed (git, libcamera-apps, gpiozero, alsa-utils)
- [ ] Camera interface enabled (if testing camera)
- [ ] I2S interface enabled (if testing microphone)
- [ ] Repository cloned successfully
- [ ] Camera button test works (GPIO 4, shows presses in command line)
- [ ] Microphone button test works (GPIO 23, shows presses in command line)
- [ ] Camera button capture works (if camera connected)
- [ ] Microphone button recording works (if mic connected)
- [ ] Images saved to ~/pictures/ (if camera connected)
- [ ] Recordings saved to ~/recordings/ (if mic connected)

## Next Steps After Testing

1. **If button test works:**
   - Button wiring is correct
   - GPIO 4 is working
   - Ready for camera testing

2. **If button capture works:**
   - Full system functional
   - Can use for actual captures
   - Consider setting up as service

3. **If issues found:**
   - Check troubleshooting section
   - Verify wiring
   - Check dependencies
   - Review error messages

