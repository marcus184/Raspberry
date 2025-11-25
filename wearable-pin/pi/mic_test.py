#!/usr/bin/env python3
"""
Microphone test script for PH0645 I2S microphone
Button-triggered audio recording
Uses arecord with I2S interface
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
SAMPLE_RATE = 48000  # Sample rate in Hz (48kHz)
CHANNELS = 2  # Stereo recording
AUDIO_FORMAT = "S32_LE"  # 32-bit signed little-endian
FORMAT = "wav"  # Audio file format


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


def record_audio_while_pressed(filepath, button, sample_rate=SAMPLE_RATE):
    """Record audio while button is pressed using arecord."""
    try:
        # Build arecord command for I2S microphone
        # For PH0645 with googlevoicehat-soundcard: hw:0,0
        # Format: arecord -D hw:0,0 -f S32_LE -r 48000 -c 2 test.wav
        cmd = [
            "arecord",
            "-D", "hw:0,0",  # I2S device (card 0, device 0 for PH0645)
            "-f", AUDIO_FORMAT,  # 32-bit signed little-endian
            "-r", str(sample_rate),  # Sample rate (48kHz)
            "-c", str(CHANNELS),  # Channels (stereo)
            filepath
        ]
        
        print("Recording... (release button to stop)")
        
        # Start recording process
        recording_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for button release
        button.wait_for_release()
        
        # Stop recording
        recording_process.terminate()
        
        # Wait a moment for process to finish
        try:
            recording_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            recording_process.kill()
            recording_process.wait()
        
        # Check if file was created
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            file_size = os.path.getsize(filepath)
            file_size_kb = file_size / 1024
            file_size_mb = file_size / (1024 * 1024)
            print(f"✓ Audio recorded: {filepath}")
            print(f"  Size: {file_size:,} bytes ({file_size_kb:.2f} KB / {file_size_mb:.2f} MB)")
            return True
        else:
            print(f"✗ Recording failed - file not created or empty")
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
    print(f"Recording Mode: Press and hold button (release to stop)")
    print(f"Format: {AUDIO_FORMAT}")
    print(f"Sample Rate: {SAMPLE_RATE} Hz")
    print(f"Channels: {CHANNELS} (Stereo)")
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
        print("2. Check /boot/config.txt has:")
        print("   dtparam=i2s=on")
        print("   dtoverlay=i2s-mmap")
        print("   dtoverlay=googlevoicehat-soundcard")
        print("3. Check wiring connections")
        print("4. Verify device: arecord -l")
        print("   Should show: card 0: sndrpigooglevoi")
        print("5. Reboot after config changes")
        print("\nContinuing anyway...")
    
    # Create save directory
    os.makedirs(SAVE_DIR, exist_ok=True)
    print(f"Save directory: {SAVE_DIR}")
    
    # Setup button
    print(f"\nSetting up button on GPIO {BUTTON_PIN}...")
    button = Button(BUTTON_PIN, pull_up=True)
    print("Button ready!")
    
    # Test recording (quick 1 second test)
    print("\nTesting microphone...")
    test_file = os.path.join(SAVE_DIR, "test_mic.wav")
    test_cmd = [
        "arecord",
        "-D", "hw:0,0",
        "-f", AUDIO_FORMAT,
        "-r", str(SAMPLE_RATE),
        "-c", str(CHANNELS),
        "-d", "1",  # 1 second test
        test_file
    ]
    try:
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            print(f"✓ Microphone test successful ({file_size} bytes)")
            # Remove test file
            try:
                os.remove(test_file)
            except:
                pass
        else:
            print("✗ Microphone test failed")
            print("\nTroubleshooting:")
            print("1. Check I2S is enabled: sudo raspi-config")
            print("2. Check /boot/config.txt has googlevoicehat-soundcard overlay")
            print("3. Check wiring: SCK->GPIO18, WS->GPIO19, SD->GPIO20")
            print("4. Check device: arecord -l")
            print(f"5. Try: arecord -D hw:0,0 -f {AUDIO_FORMAT} -r {SAMPLE_RATE} -c {CHANNELS} -d 1 test.wav")
            exit(1)
    except Exception as e:
        print(f"✗ Microphone test failed: {e}")
        exit(1)
    
    # Main loop
    print("\n" + "=" * 50)
    print("Ready! Press button to record audio...")
    print("Press Ctrl+C to exit")
    print("=" * 50)
    
    try:
        while True:
            # Wait for button press
            print("\nPress and HOLD button to start recording...")
            button.wait_for_press()
            print("Button pressed! Recording started...")
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.{FORMAT}"
            filepath = os.path.join(SAVE_DIR, filename)
            
            # Record audio while button is pressed
            if record_audio_while_pressed(filepath, button):
                print("Ready for next recording...")
            else:
                print("Recording failed. Ready to try again...")
            
            # Small delay to prevent multiple recordings from button bounce
            time.sleep(0.3)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        print("Done!")


if __name__ == "__main__":
    main()

