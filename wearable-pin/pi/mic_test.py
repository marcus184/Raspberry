#!/usr/bin/env python3
"""
Microphone test script for PH0645 I2S microphone
Button-triggered audio recording
"""

import os
import time
import subprocess
from datetime import datetime

try:
    from gpiozero import Button
    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False
    print("Error: gpiozero not available. Install with: sudo apt-get install python3-gpiozero")
    exit(1)


# Configuration
BUTTON_PIN = 23  # GPIO pin for button
SAVE_DIR = os.path.expanduser("~/recordings")  # Save location
RECORD_DURATION = 5  # Seconds to record
SAMPLE_RATE = 16000  # Sample rate in Hz (16kHz for I2S mic)
CHANNELS = 1  # Mono recording
FORMAT = "wav"  # Audio format


def check_arecord():
    """Check if arecord is available."""
    try:
        result = subprocess.run(
            ["which", "arecord"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False


def check_i2s_mic():
    """Check if I2S microphone is detected."""
    try:
        # Check if I2S device exists
        result = subprocess.run(
            ["arecord", "-l"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "card" in result.stdout.lower():
            return True
        return False
    except:
        return False


def list_audio_devices():
    """List available audio devices."""
    try:
        result = subprocess.run(
            ["arecord", "-l"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print("Available audio devices:")
        print(result.stdout)
        return result.stdout
    except Exception as e:
        print(f"Error listing devices: {e}")
        return None


def record_audio(filepath, duration=RECORD_DURATION, sample_rate=SAMPLE_RATE):
    """Record audio using arecord and save to filepath."""
    try:
        # Build arecord command for I2S microphone
        # Use hw:0,0 for first I2S device (adjust if needed)
        cmd = [
            "arecord",
            "-D", "hw:0,0",  # I2S device (may need to adjust)
            "-f", "S16_LE",  # 16-bit signed little-endian
            "-r", str(sample_rate),  # Sample rate
            "-c", str(CHANNELS),  # Channels
            "-d", str(duration),  # Duration in seconds
            filepath
        ]
        
        print(f"Recording {duration} seconds...")
        
        # Execute recording
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=duration + 5
        )
        
        if result.returncode == 0 and os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            file_size_kb = file_size / 1024
            print(f"✓ Audio recorded: {filepath}")
            print(f"  Size: {file_size:,} bytes ({file_size_kb:.2f} KB)")
            return True
        else:
            print(f"✗ Recording failed")
            if result.stderr:
                print(f"  Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Recording timed out")
        return False
    except Exception as e:
        print(f"✗ Recording failed: {e}")
        return False


def test_button():
    """Test button functionality - shows presses in command line."""
    print("=" * 50)
    print("Button Test Mode (Microphone)")
    print("=" * 50)
    print(f"Testing button on GPIO {BUTTON_PIN}")
    print("Press the button to test...")
    print("Press Ctrl+C to exit")
    print("=" * 50)
    
    button = Button(BUTTON_PIN, pull_up=True)
    press_count = 0
    
    print("\nWaiting for button press...")
    
    try:
        while True:
            button.wait_for_press()
            press_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Button pressed! (Count: {press_count})")
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
    
    # Check for help
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print("Microphone Test - PH0645 I2S Mic")
        print("\nUsage:")
        print("  python3 mic_test.py          # Normal mode - record on button press")
        print("  python3 mic_test.py --test  # Test mode - test button only")
        print("  python3 mic_test.py --list  # List audio devices")
        sys.exit(0)
    
    # Check for list devices
    if len(sys.argv) > 1 and sys.argv[1] in ['--list', '-l', 'list']:
        list_audio_devices()
        return
    
    print("=" * 50)
    print("Microphone Test - PH0645 I2S Mic")
    print("=" * 50)
    print(f"Button GPIO: {BUTTON_PIN}")
    print(f"Record Duration: {RECORD_DURATION} seconds")
    print(f"Sample Rate: {SAMPLE_RATE} Hz")
    print(f"Save location: {SAVE_DIR}")
    print("=" * 50)
    
    # Check if arecord is available
    if not check_arecord():
        print("✗ Error: arecord not found")
        print("\nInstall with:")
        print("  sudo apt-get install -y alsa-utils")
        exit(1)
    
    print("✓ arecord found")
    
    # List audio devices
    print("\nChecking audio devices...")
    devices = list_audio_devices()
    
    # Check I2S microphone
    if not check_i2s_mic():
        print("⚠ Warning: I2S microphone may not be detected")
        print("\nTroubleshooting:")
        print("1. Check I2S is enabled: sudo raspi-config")
        print("2. Check wiring connections")
        print("3. Verify device: arecord -l")
        print("4. Try different device: arecord -D hw:1,0 -l")
        print("\nContinuing anyway...")
    
    # Create save directory
    os.makedirs(SAVE_DIR, exist_ok=True)
    print(f"Save directory: {SAVE_DIR}")
    
    # Setup button
    print(f"\nSetting up button on GPIO {BUTTON_PIN}...")
    button = Button(BUTTON_PIN, pull_up=True)
    print("Button ready!")
    
    # Test recording
    print("\nTesting microphone...")
    test_file = os.path.join(SAVE_DIR, "test_mic.wav")
    if record_audio(test_file, duration=2):
        print("✓ Microphone test successful")
        # Remove test file
        try:
            os.remove(test_file)
        except:
            pass
    else:
        print("✗ Microphone test failed")
        print("\nTroubleshooting:")
        print("1. Check I2S is enabled: sudo raspi-config")
        print("2. Check wiring: SCK->GPIO18, WS->GPIO19, SD->GPIO20")
        print("3. Check device: arecord -l")
        print("4. Try: arecord -D hw:0,0 -f S16_LE -r 16000 -c 1 -d 2 test.wav")
        exit(1)
    
    # Main loop
    print("\n" + "=" * 50)
    print("Ready! Press button to record audio...")
    print("Press Ctrl+C to exit")
    print("=" * 50)
    
    try:
        while True:
            # Wait for button press
            button.wait_for_press()
            print("\nButton pressed! Recording...")
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.{FORMAT}"
            filepath = os.path.join(SAVE_DIR, filename)
            
            # Record audio
            if record_audio(filepath, duration=RECORD_DURATION):
                print("Ready for next recording...")
            else:
                print("Recording failed. Ready to try again...")
            
            # Small delay to prevent multiple recordings from button bounce
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        print("Done!")


if __name__ == "__main__":
    main()

