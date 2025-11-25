# Simple Button-Based Camera Capture Plan

## Goal
Create a minimal system: One button press = Capture one image

## Simplified Approach

### Hardware
- Raspberry Pi Zero 2W
- Arducam 5MP OV5647 camera
- One physical button (GPIO connected)
- Raspberry Pi OS Lite 64-bit

### Software Requirements
- Minimal Python script
- GPIO button handling
- Camera capture on button press
- Save image to simple location

## Phase 1: Clean Start

### Step 1.1: Decide on Repository Strategy
**Option A: New Branch**
- Create new branch: `simple-button`
- Keep existing code in main
- Work on simplified version

**Option B: New Repository**
- Create fresh repository
- Start from scratch
- Minimal codebase

**Option C: Clean Current Repository**
- Remove complex features
- Keep only button + camera capture
- Simplify structure

### Step 1.2: Minimal File Structure
```
simple-camera/
├── button_capture.py    # Main script
├── config.py           # Simple config
└── README.md          # Basic instructions
```

## Phase 2: Core Functionality

### Step 2.1: Button Setup
- Connect button to GPIO pin (e.g., GPIO 18)
- One side to GPIO, other to GND
- Pull-up resistor (internal or external)

### Step 2.2: Minimal Python Script
**Requirements:**
- Detect button press
- Initialize camera
- Capture image
- Save to file
- Clean up

**No need for:**
- Auto-updates
- Systemd services
- Complex configuration
- Multiple resolutions
- Command-line arguments

### Step 2.3: Simple Config
- Camera type: OV5647 (hardcoded)
- Resolution: 1920x1080 (fixed)
- Save location: ~/pictures/ (simple)
- GPIO pin: 18 (configurable)

## Phase 3: Implementation

### Step 3.1: Install Minimal Dependencies
```bash
sudo apt-get install -y python3-picamera2 python3-gpiozero
```

### Step 3.2: Create Simple Script
**button_capture.py:**
- Import picamera2
- Import gpiozero (for button)
- Wait for button press
- Capture image
- Save file
- Exit

### Step 3.3: Test Button
- Physical button connection
- GPIO pin configuration
- Button press detection
- LED feedback (optional)

## Phase 4: Testing

### Step 4.1: Hardware Test
- Button press detected
- GPIO working
- Camera connected

### Step 4.2: Software Test
- Script runs
- Button triggers capture
- Image saved successfully

### Step 4.3: Integration Test
- Full cycle: Button → Capture → Save
- Verify image quality
- Check file location

## Minimal Code Structure

### button_capture.py (Simplified)
```python
#!/usr/bin/env python3
"""Simple button-triggered camera capture"""

from picamera2 import Picamera2
from gpiozero import Button
from datetime import datetime
import time

# Configuration
BUTTON_PIN = 18
SAVE_DIR = "~/pictures"
RESOLUTION = (1920, 1080)

# Setup button
button = Button(BUTTON_PIN)

# Setup camera
camera = Picamera2()
config = camera.create_still_configuration(main={"size": RESOLUTION})
camera.configure(config)
camera.start()
time.sleep(2)  # Warm up

print("Ready. Press button to capture...")

# Wait for button press
button.wait_for_press()

# Capture
filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
filepath = f"{SAVE_DIR}/{filename}"
camera.capture_file(filepath)
print(f"Image saved: {filepath}")

# Cleanup
camera.stop()
```

## Next Steps Decision

**Choose approach:**
1. **New branch** - Keep existing, work on simple version
2. **New repo** - Fresh start, minimal code
3. **Simplify current** - Remove features, keep core

**Then:**
- Implement button_capture.py
- Test hardware connection
- Verify camera capture
- Iterate until working

## Success Criteria

- [ ] Button connected to GPIO
- [ ] Button press detected
- [ ] Camera initializes
- [ ] Image captured on button press
- [ ] Image saved to location
- [ ] Works reliably

## Future Enhancements (After Basic Works)

- Multiple button presses
- LED status indicator
- Multiple save locations
- Image preview (if display added)
- Configuration file
- Error handling improvements

