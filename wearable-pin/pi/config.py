"""
Configuration settings for the Raspberry Pi camera wearable pin.
Supports Arducam 5MP OV5647 and standard Raspberry Pi cameras.
"""

import os

# Camera type: 'standard' for Arducam OV5647 or Pi camera, 'arducam_16mp' for IMX519, 'auto' for auto-detect
CAMERA_TYPE = 'standard'  # Options: 'standard', 'arducam_16mp', 'auto'
# Note: Arducam 5MP OV5647 works as 'standard' camera type

# Camera settings
# Arducam 5MP OV5647: Max resolution 2592 x 1944 (5MP)
# Standard Pi Camera: Max resolution varies by model
# Recommended for OV5647: 1920x1080 (1080p) for best performance
CAMERA_RESOLUTION = (1920, 1080)  # 1080p recommended for OV5647
# Alternative resolutions for OV5647:
# CAMERA_RESOLUTION = (2592, 1944)  # Full 5MP - slower but higher quality
# CAMERA_RESOLUTION = (1280, 720)    # 720p - fastest option
CAMERA_FRAMERATE = 30
CAMERA_ROTATION = 0
CAMERA_ISO = 0  # Auto ISO

# Image settings
IMAGE_FORMAT = 'jpeg'
IMAGE_QUALITY = 85
# Image directory - change this path to save images to a specific location
IMAGE_DIR = os.path.expanduser('~/wearable-pin/images')
# Alternative locations:
# IMAGE_DIR = '/home/pi/Pictures'  # Save to Pictures folder
# IMAGE_DIR = '/media/usb'  # Save to USB drive
# IMAGE_DIR = '/tmp/captures'  # Save to temp (cleared on reboot)

# Capture settings
CAPTURE_DELAY = 0  # Seconds before capture
PREVIEW_TIME = 2  # Seconds to show preview

# Ensure image directory exists
os.makedirs(IMAGE_DIR, exist_ok=True)

# Service settings
SERVICE_PORT = 8080
SERVICE_HOST = '0.0.0.0'
