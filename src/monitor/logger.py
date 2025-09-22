"""
Event Logging Module

This module provides comprehensive event logging capabilities for the UPS monitor,
including system events, battery status changes, power transitions, and diagnostics.
"""

import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


def setup_logging(log_file: str = "data/logs/ups_monitor.log", debug: bool = False):
    """
    Setup logging configuration for the UPS monitor.
    
    Args:
        log_file: Path to log file
        debug: Enable debug logging
    """
    # Ensure log directory exists
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging level
    level = logging.DEBUG if debug else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


class EventLogger:
    """
    Event logging system for UPS monitor.
    
    Provides structured logging of system events, battery status changes,
    power transitions, and diagnostic information.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize event logger.
        
        Args:
            data_dir: Path to data directory
        """
        self.data_dir = Path(data_dir)
        self.events_file = self.data_dir / "logs" / "events.json"
        
        # Ensure directories exist
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Event history (in-memory cache)
        self.event_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Load existing events
        self._load_events()
        
        # Get logger instance
        self.logger = logging.getLogger(__name__)
    
    def _load_events(self):
        """Load existing events from file."""
        try:
            if self.events_file.exists():
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                    self.event_history = data.get("events", [])[-self.max_history_size:]
        except Exception as e:
            self.logger.error(f"Failed to load events: {e}")
            self.event_history = []
    
    def _save_events(self):
        """Save events to file."""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "event_count": len(self.event_history),
                "events": self.event_history[-self.max_history_size:]
            }
            
            with open(self.events_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save events: {e}")
    
    def log_event(self, event_type: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Log an event.
        
        Args:
            event_type: Type of event (e.g., "BATTERY_LOW", "AC_POWER_LOSS")
            metadata: Additional event metadata
        """
        try:
            event = {
                "timestamp": datetime.now().isoformat(),
                "type": event_type,
                "metadata": metadata or {},
                "unix_timestamp": time.time()
            }
            
            # Add to history
            self.event_history.append(event)
            
            # Trim history if too large
            if len(self.event_history) > self.max_history_size:
                self.event_history = self.event_history[-self.max_history_size:]
            
            # Log to standard logger
            self.logger.info(f"EVENT: {event_type} - {metadata}")
            
            # Save to file periodically (every 10 events)
            if len(self.event_history) % 10 == 0:
                self._save_events()
                
        except Exception as e:
            self.logger.error(f"Failed to log event {event_type}: {e}")
    
    def get_recent_events(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent events.
        
        Args:
            count: Number of recent events to return
            
        Returns:
            List of recent events
        """
        return self.event_history[-count:]
    
    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """
        Get events by type.
        
        Args:
            event_type: Event type to filter by
            
        Returns:
            List of events of specified type
        """
        return [event for event in self.event_history if event["type"] == event_type]
    
    def get_events_in_timerange(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """
        Get events within time range.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of events in time range
        """
        start_timestamp = start_time.timestamp()
        end_timestamp = end_time.timestamp()
        
        return [
            event for event in self.event_history
            if start_timestamp <= event["unix_timestamp"] <= end_timestamp
        ]


# TODO: Implement remaining modules as stubs
class AnalyticsEngine:
    """Analytics engine for battery and power data analysis."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.history = []
        self.logger = logging.getLogger(__name__)
    
    def update(self, readings: Dict[str, Any]):
        """Update analytics with new readings."""
        self.history.append({
            "timestamp": time.time(),
            "readings": readings.copy()
        })
        
        # Keep last 1000 readings
        if len(self.history) > 1000:
            self.history.pop(0)
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get current analytics summary."""
        if not self.history:
            return {}
        
        recent = self.history[-10:]
        voltages = [r["readings"].get("battery_voltage", 0) for r in recent]
        
        return {
            "average_voltage": sum(voltages) / len(voltages) if voltages else 0,
            "voltage_trend": "stable",  # TODO: Implement trend analysis
            "data_points": len(self.history)
        }


class RuntimeEstimator:
    """Runtime estimation based on battery capacity and load."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.last_estimate = None
        self.logger = logging.getLogger(__name__)
    
    def update(self, readings: Dict[str, Any]):
        """Update runtime estimate with new readings."""
        try:
            percentage = readings.get("battery_percentage", 0)
            current = abs(readings.get("battery_current", 1.0))
            
            if current > 0.1:  # Avoid division by zero
                # Simple estimation: assume 2500mAh capacity
                capacity_mah = 2500
                remaining_mah = (percentage / 100) * capacity_mah
                runtime_hours = remaining_mah / (current * 1000)
                
                self.last_estimate = {
                    "minutes": runtime_hours * 60,
                    "hours": runtime_hours,
                    "percentage": percentage,
                    "load_current": current
                }
            else:
                self.last_estimate = {
                    "minutes": 0,
                    "hours": 0,
                    "percentage": percentage,
                    "load_current": 0
                }
                
        except Exception as e:
            self.logger.error(f"Runtime estimation failed: {e}")
    
    def get_runtime_estimate(self) -> Optional[Dict[str, Any]]:
        """Get current runtime estimate."""
        return self.last_estimate


class SafetyManager:
    """Safety management and emergency procedures."""
    
    def __init__(self, config_dir: str = "config", event_logger: Optional[EventLogger] = None):
        self.config_dir = Path(config_dir)
        self.event_logger = event_logger
        self.logger = logging.getLogger(__name__)
        
        # Safety thresholds (TODO: Load from config)
        self.voltage_critical = 3.2
        self.voltage_low = 3.5
        self.temp_high = 60.0
        self.temp_critical = 70.0
        
        # Current status
        self.status = {
            "safe": True,
            "warnings": [],
            "critical": []
        }
    
    def check_safety(self, readings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check safety conditions and return status.
        
        Args:
            readings: Current sensor readings
            
        Returns:
            Safety status dictionary
        """
        warnings = []
        critical = []
        
        # Check battery voltage
        voltage = readings.get("battery_voltage", 4.0)
        if voltage < self.voltage_critical:
            critical.append(f"Battery voltage critically low: {voltage}V")
            if self.event_logger:
                self.event_logger.log_event("BATTERY_CRITICAL", {"voltage": voltage})
        elif voltage < self.voltage_low:
            warnings.append(f"Battery voltage low: {voltage}V")
            if self.event_logger:
                self.event_logger.log_event("BATTERY_LOW", {"voltage": voltage})
        
        # Check temperature
        temp = readings.get("temperature", 25.0)
        if temp > self.temp_critical:
            critical.append(f"Temperature critically high: {temp}°C")
            if self.event_logger:
                self.event_logger.log_event("TEMPERATURE_CRITICAL", {"temperature": temp})
        elif temp > self.temp_high:
            warnings.append(f"Temperature high: {temp}°C")
            if self.event_logger:
                self.event_logger.log_event("TEMPERATURE_HIGH", {"temperature": temp})
        
        # Update status
        self.status = {
            "safe": len(critical) == 0,
            "warnings": warnings,
            "critical": critical
        }
        
        return self.status
    
    def get_status(self) -> Dict[str, Any]:
        """Get current safety status."""
        return self.status.copy()
    
    def emergency_shutdown(self, reason: str):
        """Initiate emergency shutdown."""
        self.logger.critical(f"Emergency shutdown initiated: {reason}")
        if self.event_logger:
            self.event_logger.log_event("EMERGENCY_SHUTDOWN", {"reason": reason})
        
        # TODO: Implement actual shutdown procedure
        print(f"EMERGENCY SHUTDOWN: {reason}")


__all__ = [
    "EventLogger",
    "AnalyticsEngine", 
    "RuntimeEstimator",
    "SafetyManager",
    "setup_logging"
]