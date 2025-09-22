"""
LED Display Management Module

This module handles LED display functionality for the UPS monitor including:
- Hardware LED control via GPIO
- Software LED representation in terminal
- LED pattern mapping based on battery status
- Display policies and animations
"""

import time
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

# TODO: Replace with actual hardware imports when available
# try:
#     import RPi.GPIO as GPIO
#     HARDWARE_AVAILABLE = True
# except ImportError:
#     HARDWARE_AVAILABLE = False

HARDWARE_AVAILABLE = False  # For development

logger = logging.getLogger(__name__)


class LEDState(Enum):
    """LED state enumeration."""
    OFF = "OFF"
    ON = "ON"
    BLINK_SLOW = "BLINK_SLOW"
    BLINK_FAST = "BLINK_FAST"
    PULSE = "PULSE"


class LEDColor(Enum):
    """LED color enumeration for terminal display."""
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    RESET = "\033[0m"


class LEDManager:
    """
    Manages LED display for UPS status indication.
    
    This class handles both physical LED control (via GPIO) and software
    LED representation in the terminal interface.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize LED manager.
        
        Args:
            config_dir: Path to configuration directory
        """
        self.config_dir = Path(config_dir)
        self.config = self._load_config()
        
        # LED hardware configuration
        self.led_pins = self.config.get("hardware_leds", {}).get("led_pins", {})
        self.led_states = self.config.get("hardware_leds", {}).get("states", {})
        
        # Current LED status
        self.current_pattern = {
            "LED1": LEDState.OFF,
            "LED2": LEDState.OFF,
            "LED3": LEDState.OFF,
            "LED4": LEDState.OFF
        }
        
        # Timing configuration
        self.timing_config = self.config.get("timing", {})
        self.last_blink_time = 0
        self.blink_state = False
        
        # Terminal display configuration
        self.terminal_config = self.config.get("terminal_display", {})
        
        # Initialize hardware if available
        self._initialize_hardware()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load LED configuration from file."""
        config_file = self.config_dir / "led_mapping.yaml"
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"LED configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.warning(f"LED config file not found: {config_file}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Failed to load LED config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default LED configuration."""
        return {
            "hardware_leds": {
                "led_pins": {"LED1": 16, "LED2": 20, "LED3": 21, "LED4": 26},
                "states": {"OFF": 0, "ON": 1, "BLINK_SLOW": 2, "BLINK_FAST": 3, "PULSE": 4}
            },
            "battery_levels": {
                "critical": {"range": [0, 5], "pattern": {"LED1": "BLINK_FAST", "LED2": "OFF", "LED3": "OFF", "LED4": "OFF"}},
                "low": {"range": [6, 25], "pattern": {"LED1": "ON", "LED2": "OFF", "LED3": "OFF", "LED4": "OFF"}},
                "medium": {"range": [26, 50], "pattern": {"LED1": "ON", "LED2": "ON", "LED3": "OFF", "LED4": "OFF"}},
                "high": {"range": [51, 75], "pattern": {"LED1": "ON", "LED2": "ON", "LED3": "ON", "LED4": "OFF"}},
                "full": {"range": [76, 100], "pattern": {"LED1": "ON", "LED2": "ON", "LED3": "ON", "LED4": "ON"}}
            },
            "timing": {
                "blink_slow": {"on_duration": 1000, "off_duration": 1000},
                "blink_fast": {"on_duration": 125, "off_duration": 125},
                "refresh_rate": 100
            },
            "terminal_display": {
                "symbols": {"ON": "●", "OFF": "○", "BLINK_SLOW": "◐", "BLINK_FAST": "◑", "PULSE": "◒"},
                "colors": {"RED": "\033[31m", "GREEN": "\033[32m", "YELLOW": "\033[33m", "RESET": "\033[0m"}
            }
        }
    
    def _initialize_hardware(self):
        """Initialize GPIO for LED control."""
        if not HARDWARE_AVAILABLE:
            logger.warning("GPIO library not available, using software display only")
            return
        
        try:
            # TODO: Initialize GPIO when hardware is available
            # GPIO.setmode(GPIO.BCM)
            # for led, pin in self.led_pins.items():
            #     GPIO.setup(pin, GPIO.OUT)
            #     GPIO.output(pin, GPIO.LOW)
            logger.info("GPIO initialized for LED control")
        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
    
    def update_display(self, readings: Dict[str, Any]):
        """
        Update LED display based on sensor readings.
        
        Args:
            readings: Dictionary containing sensor readings
        """
        try:
            battery_percentage = readings.get("battery_percentage", 0)
            charging_status = readings.get("charging_status", "UNKNOWN")
            ac_present = readings.get("ac_present", False)
            
            # Determine base LED pattern from battery level
            base_pattern = self._get_battery_level_pattern(battery_percentage)
            
            # Apply status modifiers
            final_pattern = self._apply_status_modifiers(
                base_pattern, charging_status, ac_present
            )
            
            # Check for safety overrides
            final_pattern = self._apply_safety_overrides(final_pattern, readings)
            
            # Update display
            self._set_led_pattern(final_pattern)
            
        except Exception as e:
            logger.error(f"Failed to update LED display: {e}")
    
    def _get_battery_level_pattern(self, percentage: int) -> Dict[str, LEDState]:
        """Get LED pattern based on battery percentage."""
        battery_levels = self.config.get("battery_levels", {})
        
        for level_name, level_config in battery_levels.items():
            range_min, range_max = level_config["range"]
            if range_min <= percentage <= range_max:
                pattern = level_config["pattern"]
                return {
                    led: LEDState(state) for led, state in pattern.items()
                }
        
        # Default fallback pattern
        return {
            "LED1": LEDState.OFF,
            "LED2": LEDState.OFF,
            "LED3": LEDState.OFF,
            "LED4": LEDState.OFF
        }
    
    def _apply_status_modifiers(self, pattern: Dict[str, LEDState], 
                              charging_status: str, ac_present: bool) -> Dict[str, LEDState]:
        """Apply charging and power status modifiers to LED pattern."""
        modified_pattern = pattern.copy()
        
        # Charging status modifications
        if charging_status == "CHARGING":
            # Make active LEDs pulse when charging
            for led, state in modified_pattern.items():
                if state == LEDState.ON:
                    modified_pattern[led] = LEDState.PULSE
        
        elif charging_status == "DISCHARGING" and not ac_present:
            # Make highest active LED blink when on battery
            active_leds = [led for led, state in modified_pattern.items() if state == LEDState.ON]
            if active_leds:
                highest_led = max(active_leds, key=lambda x: int(x.replace("LED", "")))
                modified_pattern[highest_led] = LEDState.BLINK_SLOW
        
        return modified_pattern
    
    def _apply_safety_overrides(self, pattern: Dict[str, LEDState], 
                               readings: Dict[str, Any]) -> Dict[str, LEDState]:
        """Apply safety-related LED pattern overrides."""
        # Check for critical conditions
        voltage = readings.get("battery_voltage", 4.0)
        temperature = readings.get("temperature", 25.0)
        
        # Critical battery voltage override
        if voltage < 3.2:
            return {
                "LED1": LEDState.BLINK_FAST,
                "LED2": LEDState.BLINK_FAST,
                "LED3": LEDState.BLINK_FAST,
                "LED4": LEDState.BLINK_FAST
            }
        
        # High temperature warning
        if temperature > 60:
            # Make all active LEDs blink
            for led, state in pattern.items():
                if state == LEDState.ON:
                    pattern[led] = LEDState.BLINK_SLOW
        
        return pattern
    
    def _set_led_pattern(self, pattern: Dict[str, LEDState]):
        """Set the LED pattern on hardware and update internal state."""
        self.current_pattern = pattern.copy()
        
        if HARDWARE_AVAILABLE:
            self._update_hardware_leds()
    
    def _update_hardware_leds(self):
        """Update physical LED hardware based on current pattern."""
        if not HARDWARE_AVAILABLE:
            return
        
        current_time = time.time() * 1000  # Convert to milliseconds
        
        for led_name, state in self.current_pattern.items():
            pin = self.led_pins.get(led_name)
            if pin is None:
                continue
            
            try:
                if state == LEDState.OFF:
                    # TODO: GPIO.output(pin, GPIO.LOW)
                    pass
                elif state == LEDState.ON:
                    # TODO: GPIO.output(pin, GPIO.HIGH)
                    pass
                elif state == LEDState.BLINK_SLOW:
                    # Handle slow blinking
                    blink_config = self.timing_config.get("blink_slow", {"on_duration": 1000, "off_duration": 1000})
                    period = blink_config["on_duration"] + blink_config["off_duration"]
                    phase = current_time % period
                    # TODO: GPIO.output(pin, GPIO.HIGH if phase < blink_config["on_duration"] else GPIO.LOW)
                elif state == LEDState.BLINK_FAST:
                    # Handle fast blinking
                    blink_config = self.timing_config.get("blink_fast", {"on_duration": 125, "off_duration": 125})
                    period = blink_config["on_duration"] + blink_config["off_duration"]
                    phase = current_time % period
                    # TODO: GPIO.output(pin, GPIO.HIGH if phase < blink_config["on_duration"] else GPIO.LOW)
                elif state == LEDState.PULSE:
                    # Handle pulsing (breathing effect)
                    # TODO: Implement PWM pulsing
                    pass
                    
            except Exception as e:
                logger.error(f"Failed to update LED {led_name}: {e}")
    
    def get_current_status(self) -> Dict[str, str]:
        """Get current LED status as string dictionary."""
        return {led: state.value for led, state in self.current_pattern.items()}
    
    def render_terminal_display(self) -> str:
        """Render LED status for terminal display."""
        symbols = self.terminal_config.get("symbols", {})
        colors = self.terminal_config.get("colors", {})
        
        lines = []
        
        # Display LEDs in reverse order (LED4 at top)
        for led_num in range(4, 0, -1):
            led_name = f"LED{led_num}"
            state = self.current_pattern.get(led_name, LEDState.OFF)
            
            # Get symbol for state
            symbol = symbols.get(state.value, "?")
            
            # Get color based on LED state and position
            color = self._get_led_color(led_num, state)
            color_code = colors.get(color, "")
            reset_code = colors.get("RESET", "")
            
            # Format line
            line = f"{led_name}: {color_code}{symbol}{reset_code}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _get_led_color(self, led_num: int, state: LEDState) -> str:
        """Determine color for LED based on position and state."""
        if state == LEDState.OFF:
            return "WHITE"
        elif led_num >= 3:  # LED3, LED4
            return "GREEN"
        elif led_num == 2:  # LED2
            return "YELLOW"
        else:  # LED1
            return "RED"
    
    def test_leds(self) -> bool:
        """
        Test LED functionality by cycling through patterns.
        
        Returns:
            True if test successful, False otherwise
        """
        try:
            logger.info("Starting LED test sequence")
            
            # Test each LED individually
            for led_num in range(1, 5):
                pattern = {f"LED{i}": LEDState.OFF for i in range(1, 5)}
                pattern[f"LED{led_num}"] = LEDState.ON
                self._set_led_pattern(pattern)
                time.sleep(0.5)
            
            # Test all LEDs
            all_on_pattern = {f"LED{i}": LEDState.ON for i in range(1, 5)}
            self._set_led_pattern(all_on_pattern)
            time.sleep(1)
            
            # Test blinking
            blink_pattern = {f"LED{i}": LEDState.BLINK_FAST for i in range(1, 5)}
            self._set_led_pattern(blink_pattern)
            time.sleep(2)
            
            # Clear LEDs
            self.clear_display()
            
            logger.info("LED test sequence completed")
            return True
            
        except Exception as e:
            logger.error(f"LED test failed: {e}")
            return False
    
    def clear_display(self):
        """Clear all LEDs."""
        clear_pattern = {f"LED{i}": LEDState.OFF for i in range(1, 5)}
        self._set_led_pattern(clear_pattern)
    
    def set_custom_pattern(self, pattern: Dict[str, str]):
        """
        Set a custom LED pattern.
        
        Args:
            pattern: Dictionary mapping LED names to state strings
        """
        try:
            led_pattern = {}
            for led, state_str in pattern.items():
                led_pattern[led] = LEDState(state_str)
            
            self._set_led_pattern(led_pattern)
            logger.info(f"Custom LED pattern set: {pattern}")
            
        except Exception as e:
            logger.error(f"Failed to set custom pattern: {e}")
            raise
    
    def get_config(self) -> Dict[str, Any]:
        """Get current LED configuration."""
        return self.config.copy()
    
    def close(self):
        """Clean up LED manager resources."""
        try:
            self.clear_display()
            
            if HARDWARE_AVAILABLE:
                # TODO: GPIO.cleanup()
                pass
            
            logger.info("LED manager closed")
            
        except Exception as e:
            logger.error(f"Error closing LED manager: {e}")


# Utility functions for standalone LED operations
def display_battery_level(percentage: int):
    """Standalone function to display battery level on LEDs."""
    led_manager = LEDManager()
    try:
        readings = {"battery_percentage": percentage}
        led_manager.update_display(readings)
        time.sleep(2)  # Display for 2 seconds
    finally:
        led_manager.close()


def test_led_hardware() -> bool:
    """Standalone function to test LED hardware."""
    led_manager = LEDManager()
    try:
        return led_manager.test_leds()
    finally:
        led_manager.close()