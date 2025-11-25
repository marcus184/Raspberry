#!/usr/bin/env python3
"""
Simple button-triggered camera capture for Raspberry Pi Zero 2W
Arducam 5MP OV5647 camera
Uses rpicam-still command-line tool
"""

import os
import time
import subprocess
from datetime import datetime
from pathlib import Path

try:
    from gpiozero import Button
    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False
    print("Error: gpiozero not available. Install with: sudo apt-get install python3-gpiozero")
    exit(1)


# Configuration
BUTTON_PIN = 4  # GPIO pin for button (change if needed)
SAVE_DIR = os.path.expanduser("~/pictures")  # Save location
RESOLUTION = "1920x1080"  # 1080p for OV5647 (or use 2592x1944 for 5MP)
IMAGE_FORMAT = "jpg"
QUALITY = 85  # JPEG quality 1-100


def check_rpicam():
    """Check if rpicam-still is available."""
    try:
        result = subprocess.run(
            ["which", "rpicam-still"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
        else:
            return False
    except:
        return False


def capture_image(filepath):
    """Capture image using rpicam-still and save to filepath."""
    try:
        # Build rpicam-still command
        cmd = [
            "rpicam-still",
            "-o", filepath,
            "--width", str(RESOLUTION.split("x")[0]),
            "--height", str(RESOLUTION.split("x")[1]),
            "--quality", str(QUALITY),
            "--timeout", "1000",  # 1 second timeout
            "--nopreview"  # No preview window
        ]
        
        # Execute capture
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            file_size_mb = file_size / (1024 * 1024)
            print(f"✓ Image captured: {filepath}")
            print(f"  Size: {file_size:,} bytes ({file_size_mb:.2f} MB)")
            return True
        else:
            print(f"✗ Capture failed")
            if result.stderr:
                print(f"  Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Capture timed out")
        return False
    except Exception as e:
        print(f"✗ Capture failed: {e}")
        return False


def test_button():
    """Test button functionality - shows presses in command line."""
    print("=" * 50)
    print("Button Test Mode")
    print("=" * 50)
    print(f"Testing button on GPIO {BUTTON_PIN}")
    print("Press the button to test...")
    print("Press Ctrl+C to exit")
    print("=" * 50)
    
    try:
        from gpiozero import Button
    except ImportError:
        print("Error: gpiozero not available. Install with: sudo apt-get install python3-gpiozero")
        return
    
    button = Button(BUTTON_PIN, pull_up=True)
    press_count = 0
    
    print("\nWaiting for button press...")
    
    try:
        while True:
            button.wait_for_press()
            press_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Button pressed! (Count: {press_count})")
            
            # Small delay to prevent multiple detections from button bounce
            time.sleep(0.3)
            
    except KeyboardInterrupt:
        print(f"\n\nTest complete. Total presses detected: {press_count}")
        print("Button is working correctly!" if press_count > 0 else "No presses detected.")


def main():
    """Main function."""
    import sys
    
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] in ['--test', '-t', 'test']:
        test_button()
        return
    
    print("=" * 50)
    print("Button Camera Capture")
    print("=" * 50)
    print(f"Button GPIO: {BUTTON_PIN}")
    print(f"Resolution: {RESOLUTION}")
    print(f"Save location: {SAVE_DIR}")
    print("=" * 50)
    
    # Check if rpicam-still is available
    if not check_rpicam():
        print("✗ Error: rpicam-still not found")
        print("\nInstall with:")
        print("  sudo apt-get install -y libcamera-apps")
        print("\nOr check if it's in PATH:")
        print("  which rpicam-still")
        exit(1)
    
    print("✓ rpicam-still found")
    
    # Create save directory
    os.makedirs(SAVE_DIR, exist_ok=True)
    print(f"Save directory: {SAVE_DIR}")
    
    # Setup button
    print(f"\nSetting up button on GPIO {BUTTON_PIN}...")
    button = Button(BUTTON_PIN, pull_up=True)
    print("Button ready!")
    
    # Test camera
    print("\nTesting camera...")
    test_file = os.path.join(SAVE_DIR, "test_camera.jpg")
    if capture_image(test_file):
        print("✓ Camera test successful")
        # Remove test file
        try:
            os.remove(test_file)
        except:
            pass
    else:
        print("✗ Camera test failed")
        print("\nTroubleshooting:")
        print("1. Check camera is connected to CSI port")
        print("2. Enable camera: sudo raspi-config")
        print("3. Check camera: rpicam-still --list-cameras")
        print("4. Test manually: rpicam-still -o test.jpg")
        exit(1)
    
    # Main loop
    print("\n" + "=" * 50)
    print("Ready! Press button to capture image...")
    print("Press Ctrl+C to exit")
    print("=" * 50)
    
    try:
        while True:
            # Wait for button press
            button.wait_for_press()
            print("\nButton pressed! Capturing...")
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.{IMAGE_FORMAT}"
            filepath = os.path.join(SAVE_DIR, filename)
            
            # Capture image
            if capture_image(filepath):
                print("Ready for next capture...")
            else:
                print("Capture failed. Ready to try again...")
            
            # Small delay to prevent multiple captures from button bounce
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        print("Done!")


if __name__ == "__main__":
    import sys
    
    # Show usage if help requested
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print("Button Camera Capture")
        print("\nUsage:")
        print("  python3 button_capture.py          # Normal mode - capture images")
        print("  python3 button_capture.py --test  # Test mode - test button only")
        print("  python3 button_capture.py -t      # Test mode (short)")
        print("\nTest mode:")
        print("  Tests button functionality without camera")
        print("  Shows button presses in command line")
        sys.exit(0)
    
    main()

