#!/usr/bin/env python3
"""
Test Suite for Sensor Management Module

This module contains unit tests for the sensor management functionality
including I2C communication, sensor reading, and calibration.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from monitor.sensors import SensorManager


class TestSensorManager(unittest.TestCase):
    """Test cases for SensorManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_dir = Path("test_config")
        self.sensor_manager = SensorManager(config_dir=self.config_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.sensor_manager, 'close'):
            self.sensor_manager.close()
    
    def test_initialization(self):
        """Test sensor manager initialization."""
        self.assertEqual(self.sensor_manager.config_dir, self.config_dir)
        self.assertEqual(self.sensor_manager.ups_address, 0x36)
        self.assertIsNotNone(self.sensor_manager._last_readings)
        self.assertEqual(self.sensor_manager.voltage_offset, 0.0)
        self.assertEqual(self.sensor_manager.voltage_gain, 1.0)
    
    def test_read_all_sensors(self):
        """Test reading all sensors."""
        readings = self.sensor_manager.read_all_sensors()
        
        # Check that all expected keys are present
        expected_keys = [
            "battery_voltage", "battery_current", "battery_percentage",
            "input_voltage", "output_voltage", "load_current",
            "temperature", "ac_present", "charging_status"
        ]
        
        for key in expected_keys:
            self.assertIn(key, readings)
    
    def test_battery_voltage_reading(self):
        """Test battery voltage reading."""
        voltage = self.sensor_manager._read_battery_voltage()
        self.assertIsInstance(voltage, float)
        self.assertGreaterEqual(voltage, 0.0)
        self.assertLessEqual(voltage, 5.0)  # Reasonable range
    
    def test_battery_current_reading(self):
        """Test battery current reading."""
        current = self.sensor_manager._read_battery_current()
        self.assertIsInstance(current, float)
        # Current can be positive (charging) or negative (discharging)
        self.assertGreaterEqual(current, -5.0)
        self.assertLessEqual(current, 5.0)
    
    def test_temperature_reading(self):
        """Test temperature reading."""
        temperature = self.sensor_manager._read_temperature()
        self.assertIsInstance(temperature, float)
        self.assertGreaterEqual(temperature, 0.0)
        self.assertLessEqual(temperature, 100.0)  # Reasonable range
    
    def test_battery_percentage_calculation(self):
        """Test battery percentage calculation."""
        percentage = self.sensor_manager._calculate_battery_percentage()
        self.assertIsInstance(percentage, int)
        self.assertGreaterEqual(percentage, 0)
        self.assertLessEqual(percentage, 100)
    
    def test_charging_status_determination(self):
        """Test charging status determination."""
        status = self.sensor_manager._read_charging_status()
        self.assertIn(status, ["CHARGING", "DISCHARGING", "FULL", "UNKNOWN"])
    
    def test_ac_present_detection(self):
        """Test AC power presence detection."""
        ac_present = self.sensor_manager._read_ac_present()
        self.assertIsInstance(ac_present, bool)
    
    def test_i2c_connection_test(self):
        """Test I2C connection testing."""
        result = self.sensor_manager.test_i2c_connection()
        self.assertIsInstance(result, bool)
    
    def test_sensor_calibration(self):
        """Test sensor calibration application."""
        calibration_data = {
            "voltage_offset": 0.05,
            "voltage_gain": 1.02,
            "current_offset": -0.01,
            "current_gain": 0.98
        }
        
        # Should not raise exception
        self.sensor_manager.calibrate_sensors(calibration_data)
        
        # Check that calibration was applied
        self.assertEqual(self.sensor_manager.voltage_offset, 0.05)
        self.assertEqual(self.sensor_manager.voltage_gain, 1.02)
        self.assertEqual(self.sensor_manager.current_offset, -0.01)
        self.assertEqual(self.sensor_manager.current_gain, 0.98)
    
    def test_sensor_info(self):
        """Test getting sensor information."""
        info = self.sensor_manager.get_sensor_info()
        
        required_keys = [
            "hardware_available", "i2c_address", "calibration",
            "last_update", "cache_timeout"
        ]
        
        for key in required_keys:
            self.assertIn(key, info)
        
        # Check calibration subkeys
        calibration = info["calibration"]
        calibration_keys = ["voltage_offset", "voltage_gain", "current_offset", "current_gain"]
        for key in calibration_keys:
            self.assertIn(key, calibration)
    
    def test_reading_cache(self):
        """Test sensor reading cache functionality."""
        # First reading
        readings1 = self.sensor_manager.read_all_sensors()
        first_update_time = self.sensor_manager._last_update_time
        
        # Second reading immediately (should use cache)
        readings2 = self.sensor_manager.read_all_sensors()
        second_update_time = self.sensor_manager._last_update_time
        
        # Cache should be used (same update time)
        self.assertEqual(first_update_time, second_update_time)
        self.assertEqual(readings1, readings2)
    
    def test_voltage_range_validation(self):
        """Test that voltage readings are in reasonable ranges."""
        readings = self.sensor_manager.read_all_sensors()
        
        # Battery voltage should be reasonable for Li-ion
        battery_voltage = readings["battery_voltage"]
        self.assertGreaterEqual(battery_voltage, 2.0)  # Minimum safe voltage
        self.assertLessEqual(battery_voltage, 4.5)     # Maximum reasonable voltage
        
        # Input/output voltages should be around 5V
        input_voltage = readings["input_voltage"]
        output_voltage = readings["output_voltage"]
        self.assertGreaterEqual(input_voltage, 4.0)
        self.assertLessEqual(input_voltage, 6.0)
        self.assertGreaterEqual(output_voltage, 4.0)
        self.assertLessEqual(output_voltage, 6.0)
    
    def test_current_readings_consistency(self):
        """Test current reading consistency."""
        readings = self.sensor_manager.read_all_sensors()
        
        battery_current = readings["battery_current"]
        load_current = readings["load_current"]
        
        # Load current should always be positive
        self.assertGreaterEqual(load_current, 0.0)
        
        # Battery current can be positive or negative
        self.assertIsInstance(battery_current, float)
    
    def test_percentage_voltage_correlation(self):
        """Test that battery percentage correlates with voltage."""
        readings = self.sensor_manager.read_all_sensors()
        
        voltage = readings["battery_voltage"]
        percentage = readings["battery_percentage"]
        
        # Higher voltage should generally mean higher percentage
        # This is a basic sanity check
        if voltage > 4.0:
            self.assertGreater(percentage, 50)
        elif voltage < 3.4:
            self.assertLess(percentage, 50)


class TestStandaloneFunctions(unittest.TestCase):
    """Test cases for standalone sensor functions."""
    
    def test_read_battery_voltage_function(self):
        """Test standalone battery voltage reading function."""
        from monitor.sensors import read_battery_voltage
        
        voltage = read_battery_voltage()
        self.assertIsInstance(voltage, float)
        self.assertGreaterEqual(voltage, 0.0)
    
    def test_read_battery_percentage_function(self):
        """Test standalone battery percentage reading function."""
        from monitor.sensors import read_battery_percentage
        
        percentage = read_battery_percentage()
        self.assertIsInstance(percentage, int)
        self.assertGreaterEqual(percentage, 0)
        self.assertLessEqual(percentage, 100)
    
    def test_test_hardware_function(self):
        """Test standalone hardware test function."""
        from monitor.sensors import test_hardware
        
        result = test_hardware()
        self.assertIsInstance(result, bool)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in sensor management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sensor_manager = SensorManager()
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.sensor_manager, 'close'):
            self.sensor_manager.close()
    
    def test_invalid_calibration_data(self):
        """Test handling of invalid calibration data."""
        # Test with non-numeric values
        invalid_data = {
            "voltage_offset": "invalid",
            "voltage_gain": None
        }
        
        # Should handle gracefully (not crash)
        try:
            self.sensor_manager.calibrate_sensors(invalid_data)
        except Exception as e:
            # Should be a controlled exception, not a crash
            self.assertIsInstance(e, (ValueError, TypeError))
    
    def test_sensor_reading_error_recovery(self):
        """Test recovery from sensor reading errors."""
        # Even if individual sensor readings fail, the system should continue
        readings = self.sensor_manager.read_all_sensors()
        
        # Should still return a dictionary with at least some values
        self.assertIsInstance(readings, dict)
        self.assertGreater(len(readings), 0)


if __name__ == '__main__':
    # Create test configuration directory if it doesn't exist
    test_config_dir = Path("test_config")
    test_config_dir.mkdir(exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)