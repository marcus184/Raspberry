#!/usr/bin/env python3
"""
Raspberry Pi Camera Image Capture Script

This script captures images from the Raspberry Pi camera module.
It can be run standalone or as part of the camera service.
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

try:
    from picamera2 import Picamera2
except ImportError:
    print("Warning: picamera2 not available. Install with: sudo apt install -y python3-picamera2")
    Picamera2 = None

import config


def setup_logging():
    """Configure logging for the application."""
    log_dir = Path(config.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def ensure_image_directory():
    """Create image directory if it doesn't exist."""
    image_dir = Path(config.IMAGE_DIR)
    image_dir.mkdir(parents=True, exist_ok=True)
    return image_dir


def cleanup_old_images(image_dir, max_images):
    """Remove oldest images if count exceeds maximum."""
    images = sorted(image_dir.glob(f'{config.IMAGE_PREFIX}_*.{config.IMAGE_FORMAT}'))
    
    if len(images) >= max_images:
        images_to_delete = len(images) - max_images + 1
        for img in images[:images_to_delete]:
            img.unlink()
            logging.info(f"Deleted old image: {img}")


def capture_single_image(camera, image_dir, logger):
    """Capture a single image from the camera."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{config.IMAGE_PREFIX}_{timestamp}.{config.IMAGE_FORMAT}"
    filepath = image_dir / filename
    
    try:
        camera.capture_file(str(filepath))
        logger.info(f"Image captured: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to capture image: {e}")
        return None


def initialize_camera(logger):
    """Initialize and configure the camera."""
    if Picamera2 is None:
        logger.error("picamera2 module not available")
        return None
    
    try:
        camera = Picamera2()
        
        # Configure camera
        config_dict = camera.create_still_configuration(
            main={"size": config.CAMERA_RESOLUTION}
        )
        camera.configure(config_dict)
        
        # Apply rotation if needed
        if config.CAMERA_ROTATION != 0:
            try:
                camera.set_controls({"Rotation": config.CAMERA_ROTATION})
            except Exception as e:
                logger.warning(f"Could not set rotation (not supported on this camera): {e}")
        
        camera.start()
        time.sleep(2)  # Allow camera to warm up
        
        logger.info("Camera initialized successfully")
        return camera
    except Exception as e:
        logger.error(f"Failed to initialize camera: {e}")
        return None


def main():
    """Main function to capture images."""
    logger = setup_logging()
    logger.info("Starting camera capture script")
    
    # Ensure image directory exists
    image_dir = ensure_image_directory()
    
    # Initialize camera
    camera = initialize_camera(logger)
    if camera is None:
        logger.error("Cannot proceed without camera")
        sys.exit(1)
    
    try:
        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
            logger.info(f"Starting continuous capture mode (interval: {config.CAPTURE_INTERVAL}s)")
            while True:
                cleanup_old_images(image_dir, config.MAX_IMAGES)
                capture_single_image(camera, image_dir, logger)
                time.sleep(config.CAPTURE_INTERVAL)
        else:
            # Single capture mode
            logger.info("Capturing single image")
            cleanup_old_images(image_dir, config.MAX_IMAGES)
            filepath = capture_single_image(camera, image_dir, logger)
            if filepath:
                print(f"Image saved to: {filepath}")
    except KeyboardInterrupt:
        logger.info("Capture interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        if camera:
            camera.stop()
            logger.info("Camera stopped")


if __name__ == '__main__':
    main()
