"""
Simple configuration for button camera capture
Edit these values to customize behavior
"""

# GPIO Configuration
BUTTON_PIN = 4  # GPIO pin number (BCM numbering)
# Common GPIO pins: 2, 3, 4, 17, 18, 27, 22, 23, 24, 25

# Camera Settings
RESOLUTION = (1920, 1080)  # Image resolution (width, height)
# Options:
# (1920, 1080)  # 1080p - recommended for Pi Zero 2W
# (2592, 1944)  # Full 5MP - higher quality, slower
# (1280, 720)   # 720p - fastest option

# Save Settings
SAVE_DIR = "~/pictures"  # Directory to save images
# Options:
# "~/pictures"           # Pictures folder
# "~/captures"           # Custom folder
# "/media/usb/captures"  # USB drive
# "/tmp/captures"        # Temporary (cleared on reboot)

# Camera Settings
WARMUP_TIME = 2  # Seconds to wait for camera warmup
IMAGE_FORMAT = "jpeg"  # Image format (jpeg or png)

# Button Settings
BUTTON_DEBOUNCE = 0.5  # Seconds to wait between captures (prevents double-press)

