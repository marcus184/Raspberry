#!/usr/bin/env python3
"""
LED test script for WS2812/NeoPixel LED on Raspberry Pi Zero 2W
Uses CircuitPython neopixel library for LED control
Configured for single LED on GPIO 13
"""

import time

try:
    import board
    import neopixel
    NEOPIXEL_AVAILABLE = True
except ImportError:
    NEOPIXEL_AVAILABLE = False
    print("Error: CircuitPython neopixel library not available.")
    print("Install with: pip install adafruit-circuitpython-neopixel")
    print("Or on Raspberry Pi: sudo pip3 install adafruit-circuitpython-neopixel")
    exit(1)


# LED Configuration
LED_PIN = board.D13   # GPIO13
NUM_LEDS = 1
BRIGHTNESS = 0.3      # Brightness level (0.0 to 1.0, keep low for wearable)


def initialize_led_strip():
    """Initialize the NeoPixel LED strip."""
    try:
        pixels = neopixel.NeoPixel(
            LED_PIN,
            NUM_LEDS,
            brightness=BRIGHTNESS,
            auto_write=True
        )
        print("✓ LED strip initialized successfully")
        return pixels
    except Exception as e:
        print(f"✗ Failed to initialize LED strip: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure adafruit-circuitpython-neopixel is installed:")
        print("   pip install adafruit-circuitpython-neopixel")
        print("2. Check GPIO 13 wiring (data line)")
        print("3. Verify power supply (5V)")
        print("4. Check if resistor is present on data line (330-470Ω recommended)")
        print("5. Ensure script is run with sudo (required for hardware access)")
        exit(1)


def show(pixels, color):
    """Set LED to specified color and wait.
    
    Args:
        pixels: NeoPixel object
        color: Tuple of (R, G, B) values (0-255)
    """
    pixels[0] = color
    time.sleep(1)


def main():
    """Main function to cycle through colors."""
    print("=" * 50)
    print("LED Test - WS2812/NeoPixel on GPIO 13")
    print("=" * 50)
    print(f"LED Count: {NUM_LEDS}")
    print(f"GPIO Pin: {LED_PIN}")
    print(f"Brightness: {BRIGHTNESS}")
    print("=" * 50)
    
    # Check if running with sudo (required for hardware access)
    import os
    if os.geteuid() != 0:
        print("⚠ Warning: This script requires root privileges (sudo) for hardware access")
        print("Run with: sudo python3 led_test.py")
        print("Continuing anyway (may fail)...")
    
    # Initialize LED strip
    pixels = initialize_led_strip()
    
    # Color definitions (R, G, B)
    colors = [
        ((255, 0, 0), "Red"),
        ((0, 255, 0), "Green"),
        ((0, 0, 255), "Blue"),
        ((255, 255, 255), "White"),
        ((0, 0, 0), "Off")
    ]
    
    print("\nStarting color cycle...")
    print("Each color will display for 1 second")
    print("Press Ctrl+C to exit early\n")
    
    try:
        # Cycle through colors
        for color, color_name in colors:
            print(f"Setting LED to {color_name}...")
            show(pixels, color)
        
        print("\n✓ Color cycle complete")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        # Cleanly turn off LED before exit
        print("\nTurning off LED...")
        pixels.deinit()
        print("Done!")


if __name__ == "__main__":
    main()
