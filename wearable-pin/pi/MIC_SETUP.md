# PH0645 I2S Microphone Setup Guide

## Hardware Connection

### PH0645 I2S Mic to Raspberry Pi Zero 2W

```
PH0645 I2S Mic          Raspberry Pi Zero 2W
-----------------       ---------------------------
VDD  ---------------->  3V3      (Pin 1)
GND  ---------------->  GND      (Pin 6)
SCK  ---------------->  GPIO18   (Pin 12)  - I2S BCLK
WS   ---------------->  GPIO19   (Pin 35)  - I2S LRCLK
SD   ---------------->  GPIO20   (Pin 38)  - I2S DIN
```

### Button Connection

```
Button Pin 1  ---------------->  GPIO23   (Pin 16)
Button Pin 2  ---------------->  GND      (Pin 6 or 14)
```

## Physical Pin Layout

**GPIO Pins:**
```
    3.3V  [1] [2]  5V
   GPIO2  [3] [4]  5V
   GPIO3  [5] [6]  GND     ← Mic GND, Button GND
   GPIO4  [7] [8]  GPIO14
     GND  [9] [10] GPIO15
  GPIO17 [11] [12] GPIO18  ← Mic SCK (I2S BCLK)
  GPIO27 [13] [14] GND
  GPIO22 [15] [16] GPIO23  ← Button
    3.3V [17] [18] GPIO24
  GPIO10 [19] [20] GND
   GPIO9 [21] [22] GPIO25
  GPIO11 [23] [24] GPIO8
     GND [25] [26] GPIO7
   GPIO0 [27] [28] GPIO1
   GPIO5 [29] [30] GND
   GPIO6 [31] [32] GPIO12
  GPIO13 [33] [34] GND
  GPIO19 [35] [36] GPIO16  ← Mic WS (I2S LRCLK)
  GPIO26 [37] [38] GPIO20  ← Mic SD (I2S DIN)
     GND [39] [40] GPIO21
```

## Software Setup

### Step 1: Enable I2S Interface

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

### Step 2: Install Audio Tools

```bash
# Install ALSA utilities
sudo apt-get update
sudo apt-get install -y alsa-utils python3-gpiozero
```

### Step 3: Verify I2S Device

```bash
# List audio devices
arecord -l

# Should show I2S device, something like:
# card 0: sndrpihifiberry [snd_rpi_hifiberry_dac], device 0: HifiBerry DAC HiFi wm8804-spdif-0 []
# Or similar I2S device
```

### Step 4: Test Microphone

```bash
# Test recording (5 seconds)
arecord -D hw:0,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav

# Play back (if speaker connected)
aplay test.wav

# Check file
ls -lh test.wav
```

### Step 5: Clone Repository and Test

```bash
# Clone repository
cd ~
git clone https://github.com/marcus184/Raspberry.git wearable-pin
cd wearable-pin/wearable-pin/pi

# Make script executable
chmod +x mic_test.py

# Test button only
python3 mic_test.py --test

# Test full recording
python3 mic_test.py
```

## Configuration

### Adjust Recording Settings

Edit `mic_test.py`:
```python
RECORD_DURATION = 5  # Seconds to record
SAMPLE_RATE = 16000  # Sample rate (16000, 44100, 48000)
CHANNELS = 1  # Mono (1) or Stereo (2)
FORMAT = "wav"  # Audio format
```

### Adjust I2S Device

If microphone is on different device:
```bash
# List devices
arecord -l

# Edit mic_test.py, change:
# "-D", "hw:0,0"  # Change to hw:1,0 or hw:2,0 if needed
```

## Usage

### Test Button Only
```bash
python3 mic_test.py --test
```

### List Audio Devices
```bash
python3 mic_test.py --list
```

### Record on Button Press
```bash
python3 mic_test.py
```

**Press button to record 5 seconds of audio**

## Troubleshooting

### I2S Not Detected
```bash
# Check I2S is enabled
sudo raspi-config  # Interface Options → I2S → Enable

# Check dtoverlay
cat /boot/config.txt | grep i2s
# Should show: dtoverlay=i2s-mmap or similar

# Reboot after enabling
sudo reboot
```

### No Audio Device Found
```bash
# List devices
arecord -l

# Check I2S overlay
dmesg | grep -i i2s

# Check wiring connections
# SCK -> GPIO18, WS -> GPIO19, SD -> GPIO20
```

### Recording Fails
```bash
# Test manually
arecord -D hw:0,0 -f S16_LE -r 16000 -c 1 -d 2 test.wav

# Try different device
arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 -d 2 test.wav

# Check permissions
groups  # Should include audio group
sudo usermod -a -G audio $USER
# Log out and back in
```

### Button Not Working
```bash
# Test button
python3 mic_test.py --test

# Check GPIO
python3 -c "from gpiozero import Button; b=Button(23); b.wait_for_press(); print('OK')"
```

## Audio Device Configuration

### Find Correct Device
```bash
# List all devices
arecord -l

# Test each device
arecord -D hw:0,0 -f S16_LE -r 16000 -c 1 -d 2 test0.wav
arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 -d 2 test1.wav
# etc.

# Check which one has audio
aplay test0.wav
aplay test1.wav
```

### Update Script with Correct Device
Edit `mic_test.py`:
```python
cmd = [
    "arecord",
    "-D", "hw:1,0",  # Change to your device
    # ... rest of command
]
```

## Success Criteria

- [ ] I2S interface enabled
- [ ] Microphone detected (arecord -l shows device)
- [ ] Manual recording works
- [ ] Button test works (--test mode)
- [ ] Button-triggered recording works
- [ ] Audio files saved to ~/recordings/
- [ ] Audio files play back correctly

## File Locations

- **Recordings**: `~/recordings/`
- **Test files**: Removed after test
- **Format**: WAV files
- **Naming**: `recording_YYYYMMDD_HHMMSS.wav`

## Next Steps

1. **Test recording quality**
   - Adjust sample rate if needed
   - Test different durations
   - Verify audio playback

2. **Optimize settings**
   - Find best sample rate for your use case
   - Adjust recording duration
   - Test mono vs stereo

3. **Integration**
   - Combine with camera capture
   - Add to main button script
   - Set up automated recording

