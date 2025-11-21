"""
Configuration settings for the Raspberry Pi camera wearable pin.
"""

import os

# Camera settings
CAMERA_RESOLUTION = (1920, 1080)
CAMERA_FRAMERATE = 30
CAMERA_ROTATION = 0
CAMERA_ISO = 0  # Auto ISO

# Image settings
IMAGE_FORMAT = 'jpeg'
IMAGE_QUALITY = 85
IMAGE_DIR = os.path.expanduser('~/wearable-pin/images')

# Capture settings
CAPTURE_DELAY = 0  # Seconds before capture
PREVIEW_TIME = 2  # Seconds to show preview

# Ensure image directory exists
os.makedirs(IMAGE_DIR, exist_ok=True)

# Service settings
SERVICE_PORT = 8080
SERVICE_HOST = '0.0.0.0'
