"""
Configuration settings for the Raspberry Pi camera wearable pin.
"""

# Camera settings
CAMERA_RESOLUTION = (1920, 1080)  # Default resolution
CAMERA_FRAMERATE = 30
CAMERA_ROTATION = 0  # Rotation in degrees (0, 90, 180, 270)

# Image capture settings
IMAGE_FORMAT = 'jpeg'
IMAGE_QUALITY = 85  # JPEG quality (1-100)
CAPTURE_INTERVAL = 5  # Seconds between captures in continuous mode

# Storage settings
IMAGE_DIR = '/home/pi/wearable-pin/images'
IMAGE_PREFIX = 'capture'
MAX_IMAGES = 1000  # Maximum number of images to store

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = '/home/pi/wearable-pin/camera.log'
