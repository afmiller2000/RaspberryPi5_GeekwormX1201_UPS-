"""
Raspberry Pi Geekworm X1201 UPS Monitor

A comprehensive monitoring and management system for the Geekworm X1201 UPS
on Raspberry Pi 5 and other Linux distributions.

This package provides:
- Real-time UPS monitoring
- Battery status tracking  
- LED display management
- Event logging and diagnostics
- Safety and reliability protocols
- Configuration management
"""

__version__ = "0.1.0"
__author__ = "Alex Miller"
__license__ = "MIT"

# Import main components for easy access
from .cli import main as cli_main
from .monitor import UPSMonitor

__all__ = [
    "cli_main",
    "UPSMonitor",
    "__version__",
    "__author__",
    "__license__"
]