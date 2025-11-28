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

# Cloud Upload Settings
UPLOAD_ENABLED = True  # Set to True to enable automatic upload after capture
UPLOAD_SERVER_URL = "https://662a630e-2600-4c96-bdad-c6c625b41c0e-00-13s949ql9aoor.janeway.replit.dev:3000"  # Replit server URL
# For local development, use: "http://localhost:5001"
# Replit URL format: "https://your-repl-name.replit.app" or your deployment URL
UPLOAD_MAX_SIZE_MB = 20  # Maximum file size in MB (Pi Zero 2W optimized, Replit allows 50MB)
UPLOAD_TIMEOUT = 30  # Upload timeout in seconds

