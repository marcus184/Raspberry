#!/usr/bin/env python3
"""
Camera image capture module for Raspberry Pi wearable pin.
Captures images using the Raspberry Pi camera module.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    print("Warning: picamera2 not available. Using mock mode.")

import config


class CameraCapture:
    """Handle camera operations for capturing images."""
    
    def __init__(self):
        """Initialize the camera capture system."""
        self.camera = None
        self.is_mock = not PICAMERA_AVAILABLE
        
    def initialize(self):
        """Initialize the camera hardware."""
        if self.is_mock:
            print("Running in mock mode - no actual camera access")
            return True
            
        try:
            self.camera = Picamera2()
            camera_config = self.camera.create_still_configuration(
                main={
                    "size": config.CAMERA_RESOLUTION,
                    "format": "RGB888"
                }
            )
            self.camera.configure(camera_config)
            self.camera.start()
            time.sleep(2)  # Allow camera to warm up
            print("Camera initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def capture_image(self, filename=None):
        """
        Capture an image and save it to disk.
        
        Args:
            filename: Optional custom filename. If None, generates timestamp-based name.
            
        Returns:
            Path to the saved image file, or None if capture failed.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.{config.IMAGE_FORMAT}"
        
        filepath = os.path.join(config.IMAGE_DIR, filename)
        
        if self.is_mock:
            # Create a mock file for testing
            Path(filepath).touch()
            print(f"Mock image captured: {filepath}")
            return filepath
        
        try:
            if config.CAPTURE_DELAY > 0:
                print(f"Waiting {config.CAPTURE_DELAY} seconds before capture...")
                time.sleep(config.CAPTURE_DELAY)
            
            self.camera.capture_file(filepath)
            print(f"Image captured successfully: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error capturing image: {e}")
            return None
    
    def cleanup(self):
        """Clean up camera resources."""
        if self.camera and not self.is_mock:
            try:
                self.camera.stop()
                self.camera.close()
                print("Camera resources cleaned up")
            except Exception as e:
                print(f"Error cleaning up camera: {e}")


def main():
    """Main function for command-line usage."""
    print("Raspberry Pi Camera Capture")
    print("=" * 40)
    
    camera = CameraCapture()
    
    if not camera.initialize():
        print("Failed to initialize camera")
        sys.exit(1)
    
    try:
        # Capture a single image
        image_path = camera.capture_image()
        
        if image_path:
            print(f"\nImage saved to: {image_path}")
            print(f"File size: {os.path.getsize(image_path)} bytes")
        else:
            print("Image capture failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nCapture interrupted by user")
    finally:
        camera.cleanup()


if __name__ == "__main__":
    main()
