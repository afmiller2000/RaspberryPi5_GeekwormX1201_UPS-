#!/usr/bin/env python3
"""
Test Suite for LED Display Management Module

This module contains unit tests for the LED display functionality
including pattern mapping, terminal rendering, and hardware control.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from monitor.led import LEDManager, LEDState, LEDColor


class TestLEDManager(unittest.TestCase):
    """Test cases for LEDManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_dir = Path("test_config")
        self.led_manager = LEDManager(config_dir=self.config_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.led_manager, 'close'):
            self.led_manager.close()
    
    def test_initialization(self):
        """Test LED manager initialization."""
        self.assertEqual(self.led_manager.config_dir, self.config_dir)
        self.assertIsInstance(self.led_manager.config, dict)
        self.assertIsInstance(self.led_manager.current_pattern, dict)
        
        # Check that all LEDs are initialized
        for i in range(1, 5):
            led_name = f"LED{i}"
            self.assertIn(led_name, self.led_manager.current_pattern)
            self.assertEqual(self.led_manager.current_pattern[led_name], LEDState.OFF)
    
    def test_battery_level_pattern_mapping(self):
        """Test battery level to LED pattern mapping."""
        test_cases = [
            (0, "critical"),    # 0% should be critical
            (3, "critical"),    # 3% should be critical
            (10, "low"),        # 10% should be low
            (35, "medium"),     # 35% should be medium
            (60, "high"),       # 60% should be high
            (85, "full"),       # 85% should be full
            (100, "full")       # 100% should be full
        ]
        
        for percentage, expected_level in test_cases:
            pattern = self.led_manager._get_battery_level_pattern(percentage)
            self.assertIsInstance(pattern, dict)
            
            # Check that pattern contains all LEDs
            for i in range(1, 5):
                led_name = f"LED{i}"
                self.assertIn(led_name, pattern)
                self.assertIsInstance(pattern[led_name], LEDState)
    
    def test_critical_battery_pattern(self):
        """Test critical battery pattern (should blink)."""
        pattern = self.led_manager._get_battery_level_pattern(3)  # 3% critical
        
        # At least LED1 should be blinking for critical
        led1_state = pattern.get("LED1", LEDState.OFF)
        self.assertIn(led1_state, [LEDState.BLINK_FAST, LEDState.BLINK_SLOW])
    
    def test_full_battery_pattern(self):
        """Test full battery pattern (all LEDs on)."""
        pattern = self.led_manager._get_battery_level_pattern(90)  # 90% full
        
        # All LEDs should be on for full battery
        for i in range(1, 5):
            led_name = f"LED{i}"
            self.assertEqual(pattern[led_name], LEDState.ON)
    
    def test_charging_status_modifier(self):
        """Test charging status modifiers."""
        base_pattern = {
            "LED1": LEDState.ON,
            "LED2": LEDState.ON,
            "LED3": LEDState.OFF,
            "LED4": LEDState.OFF
        }
        
        # Test charging modifier (should make active LEDs pulse)
        charging_pattern = self.led_manager._apply_status_modifiers(
            base_pattern, "CHARGING", True
        )
        
        self.assertEqual(charging_pattern["LED1"], LEDState.PULSE)
        self.assertEqual(charging_pattern["LED2"], LEDState.PULSE)
        self.assertEqual(charging_pattern["LED3"], LEDState.OFF)
        self.assertEqual(charging_pattern["LED4"], LEDState.OFF)
    
    def test_discharging_status_modifier(self):
        """Test discharging status modifiers."""
        base_pattern = {
            "LED1": LEDState.ON,
            "LED2": LEDState.ON,
            "LED3": LEDState.ON,
            "LED4": LEDState.OFF
        }
        
        # Test discharging modifier (highest LED should blink)
        discharging_pattern = self.led_manager._apply_status_modifiers(
            base_pattern, "DISCHARGING", False
        )
        
        # LED3 is the highest active LED, should blink
        self.assertEqual(discharging_pattern["LED3"], LEDState.BLINK_SLOW)
        self.assertEqual(discharging_pattern["LED1"], LEDState.ON)
        self.assertEqual(discharging_pattern["LED2"], LEDState.ON)
    
    def test_safety_overrides(self):
        """Test safety-related LED overrides."""
        base_pattern = {
            "LED1": LEDState.ON,
            "LED2": LEDState.ON,
            "LED3": LEDState.OFF,
            "LED4": LEDState.OFF
        }
        
        # Test critical voltage override
        critical_readings = {
            "battery_voltage": 3.1,  # Critical voltage
            "temperature": 40.0
        }
        
        critical_pattern = self.led_manager._apply_safety_overrides(
            base_pattern, critical_readings
        )
        
        # All LEDs should blink fast for critical voltage
        for i in range(1, 5):
            led_name = f"LED{i}"
            self.assertEqual(critical_pattern[led_name], LEDState.BLINK_FAST)
    
    def test_high_temperature_override(self):
        """Test high temperature LED override."""
        base_pattern = {
            "LED1": LEDState.ON,
            "LED2": LEDState.ON,
            "LED3": LEDState.OFF,
            "LED4": LEDState.OFF
        }
        
        high_temp_readings = {
            "battery_voltage": 3.8,
            "temperature": 65.0  # High temperature
        }
        
        temp_pattern = self.led_manager._apply_safety_overrides(
            base_pattern, high_temp_readings
        )
        
        # Active LEDs should blink for high temperature
        self.assertEqual(temp_pattern["LED1"], LEDState.BLINK_SLOW)
        self.assertEqual(temp_pattern["LED2"], LEDState.BLINK_SLOW)
        self.assertEqual(temp_pattern["LED3"], LEDState.OFF)
        self.assertEqual(temp_pattern["LED4"], LEDState.OFF)
    
    def test_update_display(self):
        """Test LED display update with sensor readings."""
        readings = {
            "battery_percentage": 45,
            "charging_status": "CHARGING",
            "ac_present": True,
            "battery_voltage": 3.75,
            "temperature": 35.0
        }
        
        # Should not raise exception
        self.led_manager.update_display(readings)
        
        # Check that pattern was updated
        pattern = self.led_manager.current_pattern
        self.assertIsInstance(pattern, dict)
        
        # For 45% battery, should have LED1 and LED2 active
        # Since charging, they should pulse
        self.assertIn(pattern["LED1"], [LEDState.ON, LEDState.PULSE])
        self.assertIn(pattern["LED2"], [LEDState.ON, LEDState.PULSE])
    
    def test_terminal_display_rendering(self):
        """Test terminal display rendering."""
        # Set a known pattern
        test_pattern = {
            "LED1": LEDState.ON,
            "LED2": LEDState.BLINK_SLOW,
            "LED3": LEDState.OFF,
            "LED4": LEDState.PULSE
        }
        self.led_manager.current_pattern = test_pattern
        
        terminal_output = self.led_manager.render_terminal_display()
        
        # Should be a string
        self.assertIsInstance(terminal_output, str)
        
        # Should contain LED labels
        for i in range(1, 5):
            self.assertIn(f"LED{i}", terminal_output)
    
    def test_led_color_determination(self):
        """Test LED color determination based on position and state."""
        # Test different LED positions
        self.assertEqual(self.led_manager._get_led_color(4, LEDState.ON), "GREEN")  # LED4
        self.assertEqual(self.led_manager._get_led_color(3, LEDState.ON), "GREEN")  # LED3
        self.assertEqual(self.led_manager._get_led_color(2, LEDState.ON), "YELLOW") # LED2
        self.assertEqual(self.led_manager._get_led_color(1, LEDState.ON), "RED")    # LED1
        
        # OFF LEDs should be white regardless of position
        for i in range(1, 5):
            self.assertEqual(self.led_manager._get_led_color(i, LEDState.OFF), "WHITE")
    
    def test_led_test_functionality(self):
        """Test LED testing functionality."""
        # LED test should return boolean
        result = self.led_manager.test_leds()
        self.assertIsInstance(result, bool)
        
        # After test, LEDs should be cleared
        for i in range(1, 5):
            led_name = f"LED{i}"
            self.assertEqual(self.led_manager.current_pattern[led_name], LEDState.OFF)
    
    def test_clear_display(self):
        """Test clearing LED display."""
        # Set some LEDs on
        test_pattern = {
            "LED1": LEDState.ON,
            "LED2": LEDState.BLINK_FAST,
            "LED3": LEDState.PULSE,
            "LED4": LEDState.ON
        }
        self.led_manager.current_pattern = test_pattern
        
        # Clear display
        self.led_manager.clear_display()
        
        # All LEDs should be off
        for i in range(1, 5):
            led_name = f"LED{i}"
            self.assertEqual(self.led_manager.current_pattern[led_name], LEDState.OFF)
    
    def test_custom_pattern_setting(self):
        """Test setting custom LED patterns."""
        custom_pattern = {
            "LED1": "BLINK_FAST",
            "LED2": "ON",
            "LED3": "PULSE",
            "LED4": "OFF"
        }
        
        # Should not raise exception
        self.led_manager.set_custom_pattern(custom_pattern)
        
        # Check that pattern was applied
        self.assertEqual(self.led_manager.current_pattern["LED1"], LEDState.BLINK_FAST)
        self.assertEqual(self.led_manager.current_pattern["LED2"], LEDState.ON)
        self.assertEqual(self.led_manager.current_pattern["LED3"], LEDState.PULSE)
        self.assertEqual(self.led_manager.current_pattern["LED4"], LEDState.OFF)
    
    def test_get_current_status(self):
        """Test getting current LED status."""
        status = self.led_manager.get_current_status()
        
        # Should be a dictionary with string values
        self.assertIsInstance(status, dict)
        
        for i in range(1, 5):
            led_name = f"LED{i}"
            self.assertIn(led_name, status)
            self.assertIsInstance(status[led_name], str)
    
    def test_get_config(self):
        """Test getting LED configuration."""
        config = self.led_manager.get_config()
        
        # Should be a dictionary
        self.assertIsInstance(config, dict)
        
        # Should contain expected configuration sections
        expected_sections = ["battery_levels", "timing", "terminal_display"]
        for section in expected_sections:
            self.assertIn(section, config)


class TestLEDEnums(unittest.TestCase):
    """Test LED enumeration classes."""
    
    def test_led_state_enum(self):
        """Test LEDState enumeration."""
        # Test that all expected states exist
        expected_states = ["OFF", "ON", "BLINK_SLOW", "BLINK_FAST", "PULSE"]
        
        for state in expected_states:
            self.assertTrue(hasattr(LEDState, state))
            self.assertEqual(LEDState[state].value, state)
    
    def test_led_color_enum(self):
        """Test LEDColor enumeration."""
        # Test that color codes are strings
        for color in LEDColor:
            self.assertIsInstance(color.value, str)
            # ANSI color codes should start with escape sequence
            if color != LEDColor.RESET:
                self.assertTrue(color.value.startswith('\033['))


class TestStandaloneFunctions(unittest.TestCase):
    """Test standalone LED functions."""
    
    def test_display_battery_level(self):
        """Test standalone battery level display function."""
        from monitor.led import display_battery_level
        
        # Should not raise exception
        try:
            display_battery_level(75)
        except Exception as e:
            self.fail(f"display_battery_level raised exception: {e}")
    
    def test_test_led_hardware(self):
        """Test standalone LED hardware test function."""
        from monitor.led import test_led_hardware
        
        result = test_led_hardware()
        self.assertIsInstance(result, bool)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in LED management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.led_manager = LEDManager()
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.led_manager, 'close'):
            self.led_manager.close()
    
    def test_invalid_pattern_handling(self):
        """Test handling of invalid LED patterns."""
        # Test with invalid LED state
        invalid_pattern = {
            "LED1": "INVALID_STATE",
            "LED2": "ON"
        }
        
        # Should raise exception for invalid state
        with self.assertRaises(ValueError):
            self.led_manager.set_custom_pattern(invalid_pattern)
    
    def test_missing_sensor_data(self):
        """Test handling of missing sensor data."""
        incomplete_readings = {
            "battery_percentage": 50
            # Missing other required fields
        }
        
        # Should handle gracefully (not crash)
        try:
            self.led_manager.update_display(incomplete_readings)
        except Exception as e:
            self.fail(f"update_display should handle missing data gracefully: {e}")
    
    def test_invalid_percentage_values(self):
        """Test handling of invalid percentage values."""
        invalid_readings = [
            {"battery_percentage": -10},  # Negative percentage
            {"battery_percentage": 150},  # Over 100%
            {"battery_percentage": "invalid"}  # Non-numeric
        ]
        
        for readings in invalid_readings:
            try:
                self.led_manager.update_display(readings)
                # Should still have a valid pattern after handling invalid data
                pattern = self.led_manager.current_pattern
                self.assertIsInstance(pattern, dict)
            except Exception as e:
                # If exception is raised, it should be handled gracefully
                self.assertIsInstance(e, (ValueError, TypeError))


if __name__ == '__main__':
    # Create test configuration directory if it doesn't exist
    test_config_dir = Path("test_config")
    test_config_dir.mkdir(exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)