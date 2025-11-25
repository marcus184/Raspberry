#!/usr/bin/env python3
"""
LED test script for WS2812/NeoPixel LED on Raspberry Pi Zero 2W
Uses rpi_ws281x library for LED control
Configured for single LED on GPIO 13
"""

import os
import time
import sys

try:
    import rpi_ws281x as ws
    WS281X_AVAILABLE = True
except ImportError:
    WS281X_AVAILABLE = False
    print("Error: rpi_ws281x not available. Install with: pip install rpi-ws281x")
    print("Or on Raspberry Pi: sudo pip3 install rpi-ws281x")
    sys.exit(1)


# LED Configuration
LED_COUNT = 1          # Number of LED pixels
LED_PIN = 13           # GPIO pin connected to the LED data line
LED_FREQ_HZ = 800000   # LED signal frequency in Hz (800kHz)
LED_DMA = 10           # DMA channel to use for generating signal
LED_BRIGHTNESS = 70    # Set to 0 for darkest and 255 for brightest (keep low for wearable)
LED_INVERT = False     # Set to True to invert the signal
LED_CHANNEL = 1        # Set to 1 for GPIO13 (PWM1 channel)
LED_STRIP = ws.WS2811_STRIP_GRB  # Strip type and color ordering
# Alternative: LED_STRIP = ws.SK6812_STRIP_RGBW  # For RGBW LEDs


def initialize_led_strip():
    """Initialize the LED strip with configured parameters."""
    try:
        strip = ws.PixelStrip(
            LED_COUNT,
            LED_PIN,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL,
            LED_STRIP
        )
        strip.begin()
        print("✓ LED strip initialized successfully")
        return strip
    except Exception as e:
        print(f"✗ Failed to initialize LED strip: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure rpi_ws281x is installed: pip install rpi-ws281x")
        print("2. Check GPIO 13 wiring (data line)")
        print("3. Verify power supply (5V)")
        print("4. Check if resistor is present on data line (330-470Ω recommended)")
        print("5. Ensure script is run with sudo (required for hardware access)")
        sys.exit(1)


def set_color(strip, color):
    """Set all pixels to the specified color.
    
    Args:
        strip: LED strip object
        color: Tuple of (R, G, B) or (R, G, B, W) values (0-255)
    """
    for i in range(strip.numPixels()):
        if len(color) == 4:  # RGBW
            strip.setPixelColor(i, ws.Color(color[0], color[1], color[2], color[3]))
        else:  # RGB
            strip.setPixelColor(i, ws.Color(color[0], color[1], color[2]))
    strip.show()


def turn_off(strip):
    """Turn off all LEDs."""
    set_color(strip, (0, 0, 0))
    print("LED turned off")


def main():
    """Main function to cycle through colors."""
    print("=" * 50)
    print("LED Test - WS2812/NeoPixel on GPIO 13")
    print("=" * 50)
    print(f"LED Count: {LED_COUNT}")
    print(f"GPIO Pin: {LED_PIN}")
    print(f"Brightness: {LED_BRIGHTNESS}/255")
    print("=" * 50)
    
    # Check if running with sudo (required for hardware access)
    if os.geteuid() != 0:
        print("⚠ Warning: This script requires root privileges (sudo) for hardware access")
        print("Run with: sudo python3 led_test.py")
        print("Continuing anyway (may fail)...")
    
    # Initialize LED strip
    strip = initialize_led_strip()
    
    # Color definitions (R, G, B)
    colors = {
        'Red': (255, 0, 0),
        'Green': (0, 255, 0),
        'Blue': (0, 0, 255),
        'White': (255, 255, 255),
        'Off': (0, 0, 0)
    }
    
    print("\nStarting color cycle...")
    print("Each color will display for 1 second")
    print("Press Ctrl+C to exit early\n")
    
    try:
        # Cycle through colors
        for color_name, color_value in colors.items():
            print(f"Setting LED to {color_name}...")
            set_color(strip, color_value)
            time.sleep(1)
        
        print("\n✓ Color cycle complete")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        # Cleanly turn off LED before exit
        print("\nTurning off LED...")
        turn_off(strip)
        print("Done!")


if __name__ == "__main__":
    main()

