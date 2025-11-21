# Raspberry Pi Update Plan - Arducam 5MP OV5647

## Current Status
- ✅ Code updated for Arducam 5MP OV5647
- ✅ Changes committed locally
- ⏳ Need to: Push to GitHub (requires authentication), then update Pi

## Step 1: Push to GitHub (From Mac)

**Option A: Using GitHub CLI (if installed)**
```bash
cd "/Users/marcustita/Desktop/MAc/Wearable code/Raspberry"
gh auth login  # If not already authenticated
git push origin main
```

**Option B: Configure Git Credentials**
```bash
# Set up credential helper
git config --global credential.helper osxkeychain

# Or use SSH (recommended)
# Generate SSH key if needed: ssh-keygen -t ed25519 -C "your_email@example.com"
# Add to GitHub: https://github.com/settings/keys
# Change remote to SSH:
git remote set-url origin git@github.com:marcus184/Raspberry.git
git push origin main
```

**Option C: Manual Push with Token**
```bash
# Get personal access token from GitHub Settings > Developer settings > Personal access tokens
# Then push:
git push https://YOUR_TOKEN@github.com/marcus184/Raspberry.git main
```

## Step 2: Update Raspberry Pi

### Method 1: Automatic Update (If Auto-Update is Already Set Up)

If the Pi already has the auto-update service running:

1. **Wait for automatic update** (checks every 2 minutes)
   - Or trigger manually: `sudo systemctl start update.service`
   - Check logs: `sudo journalctl -u update.service -f`

2. **Verify update**
   ```bash
   cd ~/wearable-pin/wearable-pin/pi
   git log -1  # Should show latest commit
   cat config.py | grep CAMERA_TYPE  # Should show 'standard'
   ```

3. **Restart camera service** (if running)
   ```bash
   sudo systemctl restart camera.service
   ```

### Method 2: Manual Update (First Time or If Auto-Update Not Set Up)

**Step 2.1: SSH into Raspberry Pi**
```bash
ssh pi@raspberrypi.local
# Or use IP address: ssh pi@192.168.x.x
```

**Step 2.2: Navigate to Repository**
```bash
cd ~/wearable-pin/wearable-pin
```

**Step 2.3: Pull Latest Changes**
```bash
git pull origin main
```

**Step 2.4: Verify Configuration**
```bash
cd pi
cat config.py | grep -A 2 CAMERA_TYPE
# Should show:
# CAMERA_TYPE = 'standard'
# CAMERA_RESOLUTION = (1920, 1080)
```

**Step 2.5: Run Environment Check**
```bash
python3 check_environment.py
```

Verify all checks pass:
- ✓ Pi Model
- ✓ OS Version
- ✓ Camera Interface
- ✓ Python Packages
- ✓ Configuration
- ✓ Camera Init

**Step 2.6: Test Camera**
```bash
python3 test_camera.py
```

Should see successful tests.

**Step 2.7: Capture Test Image**
```bash
python3 capture_image.py
```

Verify image is captured successfully.

**Step 2.8: Set Up Auto-Updates (If Not Already Done)**
```bash
# Copy service files
sudo cp services/update.service /etc/systemd/system/
sudo cp services/update.timer /etc/systemd/system/

# Update paths if needed (check WorkingDirectory and ExecStart)
sudo nano /etc/systemd/system/update.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable update.timer
sudo systemctl start update.timer

# Check status
sudo systemctl status update.timer
```

## Step 3: Verify Everything Works

**Check Configuration:**
```bash
cd ~/wearable-pin/wearable-pin/pi
python3 -c "import config; print(f'Camera Type: {config.CAMERA_TYPE}'); print(f'Resolution: {config.CAMERA_RESOLUTION}')"
```

**Check Camera:**
```bash
libcamera-hello --list-cameras
# Should show OV5647 or standard camera
```

**Capture Test Image:**
```bash
python3 capture_image.py
ls -lh ~/wearable-pin/images/
# Should see image file (~1-2MB for 1080p)
```

**Check Services (if set up):**
```bash
sudo systemctl status camera.service
sudo systemctl status update.timer
```

## Troubleshooting

**"Git pull fails - authentication required":**
```bash
# On Pi, if using HTTPS, you may need to set up credentials
# Or switch to SSH:
git remote set-url origin git@github.com:marcus184/Raspberry.git
```

**"Camera not detected":**
```bash
# Check camera interface
vcgencmd get_camera
# Should show: supported=1 detected=1

# Check with libcamera
libcamera-hello --list-cameras
```

**"Config shows wrong camera type":**
```bash
# Edit config manually
nano config.py
# Set: CAMERA_TYPE = 'standard'
# Set: CAMERA_RESOLUTION = (1920, 1080)
```

**"Update service not working":**
```bash
# Check logs
sudo journalctl -u update.service -n 50

# Test update script manually
cd ~/wearable-pin/wearable-pin/pi
./scripts/update.sh
```

## Quick Update Commands (Copy-Paste)

**If auto-update is set up:**
```bash
sudo systemctl start update.service
sudo journalctl -u update.service -f
```

**If manual update:**
```bash
cd ~/wearable-pin/wearable-pin && git pull origin main && cd pi && python3 check_environment.py && python3 test_camera.py
```

## Success Criteria

- [ ] Changes pushed to GitHub
- [ ] Pi pulls latest code successfully
- [ ] Config shows `CAMERA_TYPE = 'standard'`
- [ ] Config shows `CAMERA_RESOLUTION = (1920, 1080)`
- [ ] Environment check passes
- [ ] Camera test passes
- [ ] Test image captured successfully
- [ ] Auto-update service running (if set up)

## Next Steps After Update

1. Verify camera works with new configuration
2. Test different resolutions if needed (5MP, 720p)
3. Set up systemd services if not already done
4. Configure auto-updates for future changes

