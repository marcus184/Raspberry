#!/usr/bin/env python3
"""
Camera image capture module for Raspberry Pi wearable pin.
Supports Arducam 5MP OV5647, Arducam 16MP IMX519, and standard Raspberry Pi cameras.
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
        self.camera_type = config.CAMERA_TYPE
        
    def _detect_camera_type(self):
        """Detect camera type automatically."""
        if self.camera_type == 'auto':
            try:
                # Try to get camera info
                camera_info = self.camera.camera_properties
                model = camera_info.get('Model', '')
                
                # Check if it's Arducam 16MP (IMX519)
                if 'imx519' in model.lower():
                    return 'arducam_16mp'
                # OV5647 and other standard cameras will be detected as 'standard'
                else:
                    return 'standard'
            except:
                # Default to standard if detection fails (includes OV5647)
                return 'standard'
        return self.camera_type
        
    def initialize(self):
        """Initialize the camera hardware."""
        if self.is_mock:
            print("Running in mock mode - no actual camera access")
            return True
            
        try:
            # Initialize camera
            self.camera = Picamera2()
            
            # Detect camera type if auto
            detected_type = self._detect_camera_type()
            
            if detected_type == 'arducam_16mp':
                print("Detected Arducam 16MP IMX519 camera")
                # Arducam 16MP IMX519 configuration
                # Max resolution: 4656 x 3496
                # Ensure resolution doesn't exceed camera capabilities
                width, height = config.CAMERA_RESOLUTION
                if width > 4656:
                    width = 4656
                if height > 3496:
                    height = 3496
                resolution = (width, height)
                
                # Create configuration optimized for Arducam
                camera_config = self.camera.create_still_configuration(
                    main={
                        "size": resolution,
                        "format": "RGB888"
                    }
                )
            else:
                # Standard Pi camera or Arducam OV5647 configuration
                # OV5647 max resolution: 2592 x 1944 (5MP)
                # Ensure resolution doesn't exceed camera capabilities
                width, height = config.CAMERA_RESOLUTION
                if width > 2592:
                    width = 2592
                if height > 1944:
                    height = 1944
                resolution = (width, height)
                
                print("Detected standard Raspberry Pi camera (or Arducam OV5647)")
                # Standard Pi camera configuration (works for OV5647)
                camera_config = self.camera.create_still_configuration(
                    main={
                        "size": resolution,
                        "format": "RGB888"
                    }
                )
            
            # Configure camera
            self.camera.configure(camera_config)
            
            # Set camera controls
            if detected_type == 'arducam_16mp':
                # Arducam-specific settings
                # Optimized for Pi Zero 2W (512MB RAM) - use conservative settings
                try:
                    self.camera.set_controls({
                        "ExposureTime": 10000,  # 10ms default exposure
                        "AnalogueGain": 1.0,
                    })
                except Exception as e:
                    # Some controls may not be available, continue anyway
                    print(f"Note: Some camera controls not available: {e}")
            
            # Start camera
            self.camera.start()
            
            # Allow camera to warm up (Arducam may need more time)
            warmup_time = 3 if detected_type == 'arducam_16mp' else 2
            print(f"Warming up camera ({warmup_time}s)...")
            time.sleep(warmup_time)
            
            print(f"Camera initialized successfully ({detected_type})")
            print(f"Resolution: {config.CAMERA_RESOLUTION}")
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            print("\nTroubleshooting tips:")
            print("1. Ensure camera is properly connected to CSI port")
            print("2. Check that camera interface is enabled: sudo raspi-config")
            print("3. Verify camera detection: libcamera-hello --list-cameras")
            print("4. Check camera status: vcgencmd get_camera")
            print("5. For Pi OS Lite 64-bit: Ensure python3-picamera2 is installed")
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
            
            # Capture image
            # For Pi Zero 2W with 16MP, capture_file is more memory-efficient than capture_array
            self.camera.capture_file(filepath)
            
            # Verify file was created and has content
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                if file_size > 0:
                    print(f"Image captured successfully: {filepath}")
                    print(f"File size: {file_size / (1024*1024):.2f} MB")
                    return filepath
                else:
                    print(f"Error: Captured file is empty")
                    return None
            else:
                print(f"Error: Captured file was not created")
                return None
        except MemoryError:
            print("Error: Out of memory during capture")
            print("Tip: Try using lower resolution (e.g., 3840x2160) for Pi Zero 2W")
            return None
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
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Capture image with Arducam 5MP OV5647 on Raspberry Pi Zero 2W',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Capture with default filename
  %(prog)s -o myphoto.jpg     # Save as myphoto.jpg
  %(prog)s -d /tmp/images     # Save to custom directory
  %(prog)s -r 2592 1944       # Capture at 5MP resolution
        """
    )
    parser.add_argument('-o', '--output', type=str, default=None,
                       help='Output filename (default: auto-generated timestamp)')
    parser.add_argument('-d', '--directory', type=str, default=None,
                       help='Output directory (default: from config.py)')
    parser.add_argument('-r', '--resolution', nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'),
                       default=None,
                       help='Image resolution WIDTH HEIGHT (default: from config.py)')
    parser.add_argument('-q', '--quality', type=int, default=None,
                       help='JPEG quality 1-100 (default: from config.py)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Override config if command-line arguments provided
    if args.directory:
        config.IMAGE_DIR = os.path.expanduser(args.directory)
        os.makedirs(config.IMAGE_DIR, exist_ok=True)
    
    if args.resolution:
        config.CAMERA_RESOLUTION = tuple(args.resolution)
    
    if args.quality:
        if 1 <= args.quality <= 100:
            config.IMAGE_QUALITY = args.quality
        else:
            print("Error: Quality must be between 1 and 100")
            sys.exit(1)
    
    if args.verbose:
        print("Raspberry Pi Camera Capture")
        print("=" * 40)
        print(f"Camera Type: {config.CAMERA_TYPE}")
        print(f"Resolution: {config.CAMERA_RESOLUTION}")
        print(f"Output Directory: {config.IMAGE_DIR}")
        print(f"Image Format: {config.IMAGE_FORMAT}")
        print(f"Image Quality: {config.IMAGE_QUALITY}")
        print("=" * 40)
    else:
        print("Raspberry Pi Camera Capture (Arducam 5MP OV5647)")
    
    camera = CameraCapture()
    
    if not camera.initialize():
        print("Failed to initialize camera")
        sys.exit(1)
    
    try:
        # Capture a single image
        image_path = camera.capture_image(args.output)
        
        if image_path:
            file_size = os.path.getsize(image_path)
            file_size_mb = file_size / (1024 * 1024)
            print(f"\n✓ Image captured successfully!")
            print(f"  File: {image_path}")
            print(f"  Size: {file_size:,} bytes ({file_size_mb:.2f} MB)")
        else:
            print("✗ Image capture failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n✗ Capture interrupted by user")
        sys.exit(1)
    finally:
        camera.cleanup()


if __name__ == "__main__":
    main()
