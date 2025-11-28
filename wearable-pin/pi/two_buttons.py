#!/usr/bin/env python3
"""
Two Button Control Script for Raspberry Pi Zero 2W
Red button: Toggle recording (start/stop and upload)
- First press: Start audio recording + take photos every 2 seconds
- Second press: Stop recording + upload audio and all photos to cloud

Hardware:
- Red button: GPIO 4 (or configure RED_BUTTON_PIN)
- Second button: GPIO 23 (or configure SECOND_BUTTON_PIN) - reserved for future use
"""

import os
import time
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

try:
    from gpiozero import Button
    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False
    print("Error: gpiozero not available. Install with: sudo apt-get install python3-gpiozero")
    sys.exit(1)

# Import configuration
try:
    import button_config as config
    RED_BUTTON_PIN = 4  # Red button GPIO pin
    SECOND_BUTTON_PIN = 23  # Second button GPIO pin (reserved for future use)
    SAVE_DIR = os.path.expanduser("~/pictures")  # Save location for photos
    RECORDINGS_DIR = os.path.expanduser("~/recordings")  # Save location for audio
    RESOLUTION = f"{config.RESOLUTION[0]}x{config.RESOLUTION[1]}"
    IMAGE_FORMAT = config.IMAGE_FORMAT.replace("jpeg", "jpg")
    QUALITY = 85
    
    # Cloud upload configuration
    UPLOAD_ENABLED = config.UPLOAD_ENABLED
    UPLOAD_SERVER_URL = config.UPLOAD_SERVER_URL
    UPLOAD_MAX_SIZE_MB = config.UPLOAD_MAX_SIZE_MB
    UPLOAD_TIMEOUT = config.UPLOAD_TIMEOUT
except ImportError:
    # Fallback to hardcoded values
    RED_BUTTON_PIN = 4
    SECOND_BUTTON_PIN = 23
    SAVE_DIR = os.path.expanduser("~/pictures")
    RECORDINGS_DIR = os.path.expanduser("~/recordings")
    RESOLUTION = "1920x1080"
    IMAGE_FORMAT = "jpg"
    QUALITY = 85
    UPLOAD_ENABLED = True
    UPLOAD_SERVER_URL = "https://662a630e-2600-4c96-bdad-c6c625b41c0e-00-13s949ql9aoor.janeway.replit.dev:3000"
    UPLOAD_MAX_SIZE_MB = 20
    UPLOAD_TIMEOUT = 30

# Import cloud upload function
try:
    from cloud_upload_test import upload_file
    UPLOAD_AVAILABLE = True
except ImportError:
    UPLOAD_AVAILABLE = False
    print("Warning: Cloud upload not available. Install requests: sudo pip3 install requests")

# Recording configuration
PHOTO_INTERVAL = 2.0  # Take photo every 2 seconds
AUDIO_SAMPLE_RATE = 48000  # 48kHz
AUDIO_CHANNELS = 2  # Stereo
AUDIO_FORMAT = "S32_LE"  # 32-bit signed little-endian


class RecordingSession:
    """Manages a recording session with audio and photos."""
    
    def __init__(self):
        self.is_recording = False
        self.audio_process = None
        self.photo_thread = None
        self.captured_photos = []
        self.audio_file = None
        self.session_id = None
        self.lock = threading.Lock()
        self.stop_photo_capture = False
    
    def start(self):
        """Start recording session."""
        with self.lock:
            if self.is_recording:
                return False
            
            self.is_recording = True
            self.stop_photo_capture = False
            self.captured_photos = []
            
            # Generate session ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_id = f"session_{timestamp}"
            
            # Create directories
            os.makedirs(SAVE_DIR, exist_ok=True)
            os.makedirs(RECORDINGS_DIR, exist_ok=True)
            
            # Start audio recording
            self.audio_file = os.path.join(RECORDINGS_DIR, f"{self.session_id}.wav")
            self._start_audio_recording()
            
            # Start photo capture thread
            self.photo_thread = threading.Thread(target=self._capture_photos_loop, daemon=True)
            self.photo_thread.start()
            
            print(f"\n{'='*50}")
            print(f"🔴 Recording Started: {self.session_id}")
            print(f"{'='*50}")
            print(f"📸 Photos: Every {PHOTO_INTERVAL} seconds")
            print(f"🎤 Audio: Recording to {os.path.basename(self.audio_file)}")
            print(f"Press red button again to stop and upload")
            return True
    
    def stop(self):
        """Stop recording session."""
        with self.lock:
            if not self.is_recording:
                return False
            
            print(f"\n{'='*50}")
            print(f"⏹️  Stopping recording...")
            print(f"{'='*50}")
            
            # Stop photo capture
            self.stop_photo_capture = True
            
            # Stop audio recording
            self._stop_audio_recording()
            
            # Wait for photo thread to finish
            if self.photo_thread and self.photo_thread.is_alive():
                self.photo_thread.join(timeout=3)
            
            self.is_recording = False
            
            print(f"✓ Recording stopped")
            print(f"  Photos captured: {len(self.captured_photos)}")
            if self.audio_file and os.path.exists(self.audio_file):
                size_mb = os.path.getsize(self.audio_file) / (1024 * 1024)
                print(f"  Audio file: {os.path.basename(self.audio_file)} ({size_mb:.2f} MB)")
            
            return True
    
    def _start_audio_recording(self):
        """Start audio recording in background."""
        try:
            cmd = [
                "arecord",
                "-D", "hw:0,0",  # I2S device
                "-f", AUDIO_FORMAT,
                "-r", str(AUDIO_SAMPLE_RATE),
                "-c", str(AUDIO_CHANNELS),
                self.audio_file
            ]
            
            self.audio_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as e:
            print(f"⚠ Error starting audio recording: {e}")
            self.audio_process = None
    
    def _stop_audio_recording(self):
        """Stop audio recording."""
        if self.audio_process:
            try:
                self.audio_process.terminate()
                self.audio_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.audio_process.kill()
                self.audio_process.wait()
            except Exception as e:
                print(f"⚠ Error stopping audio: {e}")
            finally:
                self.audio_process = None
    
    def _capture_photos_loop(self):
        """Capture photos every 2 seconds in a loop."""
        photo_count = 0
        
        while not self.stop_photo_capture:
            try:
                # Capture photo
                photo_count += 1
                filename = f"{self.session_id}_photo_{photo_count:04d}.{IMAGE_FORMAT}"
                filepath = os.path.join(SAVE_DIR, filename)
                
                if self._capture_photo(filepath):
                    with self.lock:
                        self.captured_photos.append(filepath)
                    print(f"📸 Photo {photo_count} captured: {os.path.basename(filepath)}")
                else:
                    print(f"⚠ Photo {photo_count} capture failed")
                
                # Wait for next capture (with small checks to allow early stop)
                elapsed = 0
                while elapsed < PHOTO_INTERVAL and not self.stop_photo_capture:
                    time.sleep(0.1)
                    elapsed += 0.1
                    
            except Exception as e:
                print(f"⚠ Error in photo capture loop: {e}")
                break
    
    def _capture_photo(self, filepath):
        """Capture a single photo using rpicam-still."""
        try:
            cmd = [
                "rpicam-still",
                "-o", filepath,
                "--width", str(RESOLUTION.split("x")[0]),
                "--height", str(RESOLUTION.split("x")[1]),
                "--quality", str(QUALITY),
                "--timeout", "1000",
                "--nopreview"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return result.returncode == 0 and os.path.exists(filepath) and os.path.getsize(filepath) > 0
        except Exception as e:
            print(f"⚠ Capture error: {e}")
            return False
    
    def upload_files(self):
        """Upload all captured files to cloud."""
        if not UPLOAD_AVAILABLE or not UPLOAD_ENABLED:
            print("⚠ Upload not available or disabled")
            return False
        
        files_to_upload = []
        
        # Add audio file
        if self.audio_file and os.path.exists(self.audio_file):
            files_to_upload.append(("audio", self.audio_file))
        
        # Add all photos
        for photo_path in self.captured_photos:
            if os.path.exists(photo_path):
                files_to_upload.append(("photo", photo_path))
        
        if not files_to_upload:
            print("⚠ No files to upload")
            return False
        
        print(f"\n{'='*50}")
        print(f"☁️  Uploading {len(files_to_upload)} file(s) to cloud...")
        print(f"{'='*50}")
        
        max_file_size_bytes = UPLOAD_MAX_SIZE_MB * 1024 * 1024
        success_count = 0
        fail_count = 0
        
        for file_type, filepath in files_to_upload:
            try:
                file_size = os.path.getsize(filepath)
                if file_size > max_file_size_bytes:
                    print(f"⚠ {os.path.basename(filepath)} too large ({file_size / (1024*1024):.2f}MB), skipping")
                    fail_count += 1
                    continue
                
                print(f"📤 Uploading {file_type}: {os.path.basename(filepath)}...")
                result = upload_file(
                    filepath,
                    server_url=UPLOAD_SERVER_URL,
                    max_file_size=max_file_size_bytes,
                    timeout=UPLOAD_TIMEOUT,
                    check_mem=True,
                    verbose=False  # Less verbose for batch uploads
                )
                
                if result["success"]:
                    print(f"  ✓ Uploaded: {os.path.basename(filepath)}")
                    success_count += 1
                else:
                    print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
                    fail_count += 1
                    
            except Exception as e:
                print(f"  ✗ Error uploading {os.path.basename(filepath)}: {e}")
                fail_count += 1
        
        print(f"\n{'='*50}")
        print(f"📊 Upload Summary:")
        print(f"  ✓ Successful: {success_count}")
        print(f"  ✗ Failed: {fail_count}")
        print(f"{'='*50}")
        
        return success_count > 0


def check_dependencies():
    """Check if required tools are available."""
    checks = {
        "rpicam-still": False,
        "arecord": False,
        "gpiozero": GPIOZERO_AVAILABLE
    }
    
    # Check rpicam-still
    try:
        result = subprocess.run(["which", "rpicam-still"], capture_output=True, text=True)
        checks["rpicam-still"] = result.returncode == 0
    except:
        pass
    
    # Check arecord
    try:
        result = subprocess.run(["which", "arecord"], capture_output=True, text=True)
        checks["arecord"] = result.returncode == 0
    except:
        pass
    
    return checks


def main():
    """Main function."""
    print("=" * 50)
    print("Two Button Control - Recording System")
    print("=" * 50)
    print(f"Red Button GPIO: {RED_BUTTON_PIN}")
    print(f"Second Button GPIO: {SECOND_BUTTON_PIN} (reserved)")
    print(f"Photo interval: {PHOTO_INTERVAL} seconds")
    print(f"Photo save: {SAVE_DIR}")
    print(f"Audio save: {RECORDINGS_DIR}")
    print("=" * 50)
    
    # Check dependencies
    print("\nChecking dependencies...")
    deps = check_dependencies()
    for tool, available in deps.items():
        status = "✓" if available else "✗"
        print(f"  {status} {tool}")
    
    if not all([deps["rpicam-still"], deps["arecord"], deps["gpiozero"]]):
        print("\n⚠ Missing dependencies. Install with:")
        if not deps["rpicam-still"]:
            print("  sudo apt-get install -y libcamera-apps")
        if not deps["arecord"]:
            print("  sudo apt-get install -y alsa-utils")
        if not deps["gpiozero"]:
            print("  sudo apt-get install -y python3-gpiozero")
        sys.exit(1)
    
    # Check upload availability
    if UPLOAD_ENABLED:
        if UPLOAD_AVAILABLE:
            print(f"✓ Cloud upload enabled: {UPLOAD_SERVER_URL}")
        else:
            print("⚠ Cloud upload enabled but requests library missing")
            print("  Install with: sudo pip3 install requests")
    else:
        print("⚠ Cloud upload disabled (set UPLOAD_ENABLED=True in button_config.py)")
    
    # Setup buttons
    print(f"\nSetting up buttons...")
    red_button = Button(RED_BUTTON_PIN, pull_up=True)
    second_button = Button(SECOND_BUTTON_PIN, pull_up=True)  # Reserved for future use
    print("✓ Buttons ready")
    
    # Create recording session
    session = RecordingSession()
    
    print("\n" + "=" * 50)
    print("Ready! Press RED button to start/stop recording")
    print("=" * 50)
    print("First press: Start recording (audio + photos every 2s)")
    print("Second press: Stop recording + upload to cloud")
    print("Press Ctrl+C to exit")
    print("=" * 50)
    
    try:
        while True:
            # Wait for red button press
            red_button.wait_for_press()
            time.sleep(0.2)  # Debounce
            
            if not session.is_recording:
                # Start recording
                if session.start():
                    # Wait for second press to stop
                    red_button.wait_for_press()
                    time.sleep(0.2)  # Debounce
                    
                    # Stop recording
                    if session.stop():
                        # Upload files
                        if UPLOAD_ENABLED and UPLOAD_AVAILABLE:
                            session.upload_files()
                        else:
                            print("\n⚠ Upload skipped (disabled or unavailable)")
            else:
                # Already recording, this should not happen, but handle it
                print("⚠ Already recording, ignoring press")
            
            # Small delay before next cycle
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        if session.is_recording:
            print("Stopping active recording...")
            session.stop()
        print("Done!")


if __name__ == "__main__":
    main()

