#!/usr/bin/env python3
"""
Test script for Raspberry Pi camera functionality.

This script performs basic tests to verify the camera is working correctly.
"""

import sys
import time
from pathlib import Path

try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    print("Warning: picamera2 not available")
    print("Install with: sudo apt install -y python3-picamera2")
    PICAMERA_AVAILABLE = False

import config


def test_camera_detection():
    """Test if camera is detected by the system."""
    print("Test 1: Camera Detection")
    print("-" * 40)
    
    if not PICAMERA_AVAILABLE:
        print("✗ FAILED: picamera2 module not installed")
        return False
    
    try:
        camera = Picamera2()
        camera_info = camera.camera_properties
        print(f"✓ PASSED: Camera detected")
        print(f"  Model: {camera_info.get('Model', 'Unknown')}")
        print(f"  Location: {camera_info.get('Location', 'Unknown')}")
        return True
    except Exception as e:
        print(f"✗ FAILED: Camera not detected - {e}")
        return False


def test_camera_initialization():
    """Test camera initialization and configuration."""
    print("\nTest 2: Camera Initialization")
    print("-" * 40)
    
    if not PICAMERA_AVAILABLE:
        print("✗ SKIPPED: picamera2 not available")
        return False
    
    try:
        camera = Picamera2()
        
        # Configure camera
        config_dict = camera.create_still_configuration(
            main={"size": config.CAMERA_RESOLUTION}
        )
        camera.configure(config_dict)
        
        print(f"✓ PASSED: Camera configured")
        print(f"  Resolution: {config.CAMERA_RESOLUTION}")
        
        camera.start()
        time.sleep(1)
        camera.stop()
        
        print(f"✓ PASSED: Camera started and stopped successfully")
        return True
    except Exception as e:
        print(f"✗ FAILED: Camera initialization failed - {e}")
        return False


def test_image_capture():
    """Test capturing a single image."""
    print("\nTest 3: Image Capture")
    print("-" * 40)
    
    if not PICAMERA_AVAILABLE:
        print("✗ SKIPPED: picamera2 not available")
        return False
    
    test_dir = Path("/tmp/wearable-pin-test")
    test_dir.mkdir(parents=True, exist_ok=True)
    test_image = test_dir / "test_capture.jpg"
    
    camera = None
    try:
        camera = Picamera2()
        config_dict = camera.create_still_configuration()
        camera.configure(config_dict)
        camera.start()
        time.sleep(2)  # Allow camera to warm up
        
        camera.capture_file(str(test_image))
        
        if test_image.exists() and test_image.stat().st_size > 0:
            print(f"✓ PASSED: Image captured successfully")
            print(f"  Location: {test_image}")
            print(f"  Size: {test_image.stat().st_size} bytes")
            
            # Cleanup
            test_image.unlink()
            return True
        else:
            print(f"✗ FAILED: Image file not created or is empty")
            return False
            
    except Exception as e:
        print(f"✗ FAILED: Image capture failed - {e}")
        return False
    finally:
        if camera is not None:
            camera.stop()


def test_configuration():
    """Test configuration settings."""
    print("\nTest 4: Configuration Validation")
    print("-" * 40)
    
    try:
        # Check resolution
        assert len(config.CAMERA_RESOLUTION) == 2, "Resolution must be a tuple of 2 values"
        assert all(isinstance(x, int) and x > 0 for x in config.CAMERA_RESOLUTION), \
            "Resolution values must be positive integers"
        print(f"✓ Resolution: {config.CAMERA_RESOLUTION}")
        
        # Check framerate
        assert isinstance(config.CAMERA_FRAMERATE, int) and config.CAMERA_FRAMERATE > 0, \
            "Framerate must be a positive integer"
        print(f"✓ Framerate: {config.CAMERA_FRAMERATE}")
        
        # Check rotation
        assert config.CAMERA_ROTATION in [0, 90, 180, 270], \
            "Rotation must be 0, 90, 180, or 270"
        print(f"✓ Rotation: {config.CAMERA_ROTATION}°")
        
        # Check image format
        assert config.IMAGE_FORMAT in ['jpeg', 'png', 'bmp'], \
            "Image format must be jpeg, png, or bmp"
        print(f"✓ Image format: {config.IMAGE_FORMAT}")
        
        # Check quality
        assert 1 <= config.IMAGE_QUALITY <= 100, \
            "Image quality must be between 1 and 100"
        print(f"✓ Image quality: {config.IMAGE_QUALITY}")
        
        print("✓ PASSED: All configuration settings are valid")
        return True
        
    except AssertionError as e:
        print(f"✗ FAILED: Configuration validation - {e}")
        return False


def run_all_tests():
    """Run all camera tests."""
    print("=" * 40)
    print("Raspberry Pi Camera Test Suite")
    print("=" * 40)
    
    results = []
    
    # Run tests
    results.append(("Configuration", test_configuration()))
    results.append(("Camera Detection", test_camera_detection()))
    results.append(("Camera Initialization", test_camera_initialization()))
    results.append(("Image Capture", test_image_capture()))
    
    # Print summary
    print("\n" + "=" * 40)
    print("Test Summary")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print("-" * 40)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 40)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
