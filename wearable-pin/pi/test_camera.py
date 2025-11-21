#!/usr/bin/env python3
"""
Test script for Raspberry Pi camera functionality.
Tests camera initialization, capture, and cleanup.
"""

import os
import sys
import time
from pathlib import Path

import config
from capture_image import CameraCapture


def test_camera_initialization():
    """Test camera initialization."""
    print("\n[TEST] Camera Initialization")
    print("-" * 40)
    
    camera = CameraCapture()
    result = camera.initialize()
    
    if result:
        print("✓ Camera initialized successfully")
        camera.cleanup()
        return True
    else:
        print("✗ Camera initialization failed")
        return False


def test_image_capture():
    """Test image capture functionality."""
    print("\n[TEST] Image Capture")
    print("-" * 40)
    
    camera = CameraCapture()
    
    if not camera.initialize():
        print("✗ Cannot test capture - initialization failed")
        return False
    
    try:
        # Test capture with default filename
        image_path = camera.capture_image()
        
        if image_path and os.path.exists(image_path):
            print(f"✓ Image captured successfully: {image_path}")
            file_size = os.path.getsize(image_path)
            print(f"  File size: {file_size} bytes")
            
            # Test custom filename
            custom_path = camera.capture_image("test_custom.jpg")
            if custom_path and os.path.exists(custom_path):
                print(f"✓ Custom filename capture successful: {custom_path}")
            else:
                print("✗ Custom filename capture failed")
                return False
            
            return True
        else:
            print("✗ Image capture failed")
            return False
            
    finally:
        camera.cleanup()


def test_config_settings():
    """Test configuration settings."""
    print("\n[TEST] Configuration Settings")
    print("-" * 40)
    
    tests_passed = True
    
    # Check required config attributes
    required_attrs = [
        'CAMERA_RESOLUTION',
        'CAMERA_FRAMERATE',
        'IMAGE_FORMAT',
        'IMAGE_DIR'
    ]
    
    for attr in required_attrs:
        if hasattr(config, attr):
            value = getattr(config, attr)
            print(f"✓ {attr}: {value}")
        else:
            print(f"✗ Missing configuration: {attr}")
            tests_passed = False
    
    # Check if image directory exists
    if os.path.exists(config.IMAGE_DIR):
        print(f"✓ Image directory exists: {config.IMAGE_DIR}")
    else:
        print(f"✗ Image directory not found: {config.IMAGE_DIR}")
        tests_passed = False
    
    return tests_passed


def test_cleanup():
    """Test cleanup functionality."""
    print("\n[TEST] Camera Cleanup")
    print("-" * 40)
    
    camera = CameraCapture()
    camera.initialize()
    
    try:
        camera.cleanup()
        print("✓ Camera cleanup completed")
        return True
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        return False


def run_all_tests():
    """Run all camera tests."""
    print("\n" + "=" * 40)
    print("Raspberry Pi Camera Test Suite")
    print("=" * 40)
    
    results = {
        "Configuration": test_config_settings(),
        "Initialization": test_camera_initialization(),
        "Image Capture": test_image_capture(),
        "Cleanup": test_cleanup()
    }
    
    print("\n" + "=" * 40)
    print("Test Results Summary")
    print("=" * 40)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(results.values())


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
