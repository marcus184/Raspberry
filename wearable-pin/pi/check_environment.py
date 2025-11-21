#!/usr/bin/env python3
"""
Environment check script for Raspberry Pi Zero 2W with Arducam 5MP OV5647.
Verifies system compatibility, camera detection, and configuration.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def check_pi_model():
    """Check Raspberry Pi model."""
    print("\n" + "=" * 50)
    print("Raspberry Pi Model Check")
    print("=" * 50)
    
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
            print(f"✓ Detected: {model}")
            
            if 'Zero 2' in model or 'Zero 2 W' in model:
                print("✓ Raspberry Pi Zero 2W detected - Compatible")
                return True, model
            elif 'Raspberry Pi' in model:
                print("✓ Raspberry Pi detected - Compatible")
                return True, model
            else:
                print("⚠ Unknown model - May still work")
                return True, model
    except FileNotFoundError:
        print("✗ Not running on Raspberry Pi")
        return False, "Unknown"

def check_os_version():
    """Check OS version and compatibility."""
    print("\n" + "=" * 50)
    print("OS Version Check")
    print("=" * 50)
    
    try:
        with open('/etc/os-release', 'r') as f:
            os_info = f.read()
            
        if 'Raspbian' in os_info:
            print("✗ Raspbian detected")
            print("  ERROR: Arducam 16MP requires Raspberry Pi OS (not Raspbian)")
            print("  Please upgrade to Raspberry Pi OS")
            return False
        elif 'Raspberry Pi OS' in os_info or 'Debian' in os_info:
            print("✓ Raspberry Pi OS detected - Compatible with Arducam")
            
            # Check version
            for line in os_info.split('\n'):
                if 'VERSION_ID=' in line:
                    version = line.split('=')[1].strip('"')
                    print(f"  Version: {version}")
                    if int(version.split('.')[0]) >= 11:  # Bullseye or later
                        print("✓ OS version compatible (Bullseye or later)")
                    else:
                        print("⚠ OS version may be too old (recommend Bullseye or later)")
            return True
        else:
            print("⚠ Unknown OS - May still work")
            return True
    except FileNotFoundError:
        print("⚠ Cannot read OS info")
        return True

def check_camera_interface():
    """Check if camera interface is enabled."""
    print("\n" + "=" * 50)
    print("Camera Interface Check")
    print("=" * 50)
    
    try:
        result = subprocess.run(['vcgencmd', 'get_camera'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"  {output}")
            if 'supported=1' in output:
                if 'detected=1' in output:
                    print("✓ Camera interface enabled and camera detected")
                    return True
                else:
                    print("⚠ Camera interface enabled but no camera detected")
                    print("  Check camera connection")
                    return False
            else:
                print("✗ Camera interface not enabled")
                print("  Run: sudo raspi-config")
                print("  Navigate to: Interface Options -> Camera -> Enable")
                return False
        else:
            print("⚠ Cannot check camera interface (vcgencmd failed)")
            return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠ vcgencmd not available - trying libcamera instead")
        return check_camera_libcamera()

def check_camera_libcamera():
    """Check camera using libcamera."""
    print("\n" + "=" * 50)
    print("Camera Detection (libcamera)")
    print("=" * 50)
    
    try:
        result = subprocess.run(['libcamera-hello', '--list-cameras'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout
            print("  Camera list:")
            print(output)
            
            if 'imx519' in output.lower():
                print("✓ Arducam 16MP IMX519 detected!")
                return True
            elif 'ov5647' in output.lower() or ('arducam' in output.lower() and '5647' in output.lower()):
                print("✓ Arducam 5MP OV5647 detected!")
                return True
            elif 'arducam' in output.lower():
                print("✓ Arducam camera detected (check model)")
                return True
            elif 'camera' in output.lower():
                print("✓ Camera detected (may be standard Pi camera)")
                return True
            else:
                print("✗ No camera detected")
                return False
        else:
            print(f"✗ libcamera-hello failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("✗ libcamera-hello not installed")
        print("  Install with: sudo apt-get install libcamera-apps")
        return False
    except subprocess.TimeoutExpired:
        print("✗ libcamera-hello timed out")
        return False

def check_python_packages():
    """Check required Python packages."""
    print("\n" + "=" * 50)
    print("Python Packages Check")
    print("=" * 50)
    
    packages = {
        'picamera2': 'python3-picamera2',
    }
    
    all_ok = True
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"✓ {module} installed")
        except ImportError:
            print(f"✗ {module} not installed")
            print(f"  Install with: sudo apt-get install {package}")
            all_ok = False
    
    return all_ok

def check_system_resources():
    """Check system resources (memory, disk)."""
    print("\n" + "=" * 50)
    print("System Resources Check")
    print("=" * 50)
    
    # Check memory
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if 'MemTotal:' in line:
                    mem_kb = int(line.split()[1])
                    mem_mb = mem_kb // 1024
                    print(f"  Total RAM: {mem_mb} MB")
                    
                    if mem_mb < 512:
                        print("⚠ Low memory - Pi Zero 2W has 512MB")
                        print("  Consider using lower resolution for 16MP captures")
                    elif mem_mb == 512:
                        print("✓ Pi Zero 2W (512MB) - Compatible")
                        print("  Note: 16MP images (~25MB) may use significant memory")
                    else:
                        print("✓ Sufficient memory")
                    break
    except:
        print("⚠ Cannot read memory info")
    
    # Check disk space
    try:
        stat = os.statvfs(os.path.expanduser('~'))
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        print(f"  Free disk space: {free_gb:.2f} GB")
        
        if free_gb < 1:
            print("⚠ Low disk space")
            print("  OV5647 5MP images: ~2-5MB each")
            print("  OV5647 1080p images: ~1-2MB each")
        else:
            print("✓ Sufficient disk space")
    except:
        print("⚠ Cannot check disk space")

def check_configuration():
    """Check configuration settings."""
    print("\n" + "=" * 50)
    print("Configuration Check")
    print("=" * 50)
    
    try:
        import config
        
        print(f"  Camera Type: {config.CAMERA_TYPE}")
        print(f"  Resolution: {config.CAMERA_RESOLUTION}")
        print(f"  Image Format: {config.IMAGE_FORMAT}")
        print(f"  Image Quality: {config.IMAGE_QUALITY}")
        print(f"  Image Directory: {config.IMAGE_DIR}")
        
        # Check if image directory exists
        if os.path.exists(config.IMAGE_DIR):
            print(f"✓ Image directory exists: {config.IMAGE_DIR}")
        else:
            print(f"⚠ Image directory does not exist: {config.IMAGE_DIR}")
            print("  Will be created automatically")
        
        # Check resolution for camera type
        width, height = config.CAMERA_RESOLUTION
        if width == 4656 and height == 3496:
            print("⚠ Full 16MP resolution (4656x3496) - for IMX519 only")
            print("  Pi Zero 2W can handle this but may be slower")
        elif width == 2592 and height == 1944:
            print("✓ Full 5MP resolution (2592x1944) - for OV5647")
            print("  Good quality, moderate speed")
        elif width == 1920 and height == 1080:
            print("✓ 1080p resolution (1920x1080) - recommended for OV5647")
            print("  Good balance of quality and speed")
        elif width <= 1920 and height <= 1080:
            print("✓ Resolution appropriate for Pi Zero 2W and OV5647")
        else:
            print("✓ Resolution configured")
        
        return True
    except ImportError as e:
        print(f"✗ Cannot import config: {e}")
        return False
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def check_camera_initialization():
    """Test camera initialization."""
    print("\n" + "=" * 50)
    print("Camera Initialization Test")
    print("=" * 50)
    
    try:
        from capture_image import CameraCapture
        
        camera = CameraCapture()
        print("  Attempting to initialize camera...")
        
        if camera.initialize():
            print("✓ Camera initialized successfully")
            camera.cleanup()
            return True
        else:
            print("✗ Camera initialization failed")
            return False
    except Exception as e:
        print(f"✗ Camera test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all environment checks."""
    print("\n" + "=" * 50)
    print("Raspberry Pi Zero 2W + Arducam 16MP Environment Check")
    print("=" * 50)
    
    results = {}
    
    # Run checks
    pi_ok, model = check_pi_model()
    results['Pi Model'] = pi_ok
    
    os_ok = check_os_version()
    results['OS Version'] = os_ok
    
    camera_interface_ok = check_camera_interface()
    if camera_interface_ok is not None:
        results['Camera Interface'] = camera_interface_ok
    
    packages_ok = check_python_packages()
    results['Python Packages'] = packages_ok
    
    check_system_resources()  # Informational only
    
    config_ok = check_configuration()
    results['Configuration'] = config_ok
    
    if all([pi_ok, os_ok, packages_ok, config_ok]):
        init_ok = check_camera_initialization()
        results['Camera Init'] = init_ok
    else:
        print("\n⚠ Skipping camera initialization test due to previous failures")
        results['Camera Init'] = None
    
    # Summary
    print("\n" + "=" * 50)
    print("Check Summary")
    print("=" * 50)
    
    for check_name, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ SKIP"
        print(f"{status} - {check_name}")
    
    all_passed = all(r for r in results.values() if r is not None)
    
    if all_passed:
        print("\n✓ All checks passed! Environment is ready for camera capture.")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

