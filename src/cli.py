#!/usr/bin/env python3
"""
Command Line Interface for Raspberry Pi Geekworm X1201 UPS Monitor

This module provides the main command-line interface for the UPS monitoring system.
It handles argument parsing, configuration loading, and coordination of monitoring
components.

Usage:
    python cli.py --monitor              # Start monitoring
    python cli.py --calibrate           # Run calibration
    python cli.py --snapshot            # Take diagnostic snapshot
    python cli.py --test-hardware       # Test hardware connectivity
"""

import argparse
import sys
import os
import signal
import time
import json
from datetime import datetime
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitor import UPSMonitor
from monitor.logger import setup_logging
from monitor.sensors import SensorManager
from monitor.led import LEDManager


class UPSCLIApplication:
    """Main CLI application class for UPS Monitor."""
    
    def __init__(self):
        self.monitor = None
        self.running = False
        self.config_dir = Path("config")
        self.data_dir = Path("data")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.running = False
        if self.monitor:
            self.monitor.stop()
    
    def _setup_directories(self):
        """Ensure required directories exist."""
        directories = [
            self.config_dir,
            self.data_dir / "logs",
            self.data_dir / "snapshots",
            self.data_dir / "calibrations"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def run_monitor(self, args):
        """Start the UPS monitoring system."""
        print("Starting Raspberry Pi Geekworm X1201 UPS Monitor...")
        print("=" * 50)
        
        try:
            # Initialize monitor
            self.monitor = UPSMonitor(
                config_dir=self.config_dir,
                data_dir=self.data_dir,
                debug=args.debug
            )
            
            # Start monitoring
            self.monitor.start()
            self.running = True
            print("Monitor started. Press Ctrl+C to stop.")
            
            while self.running:
                try:
                    # Update and display status
                    self.monitor.update()
                    
                    if not args.quiet:
                        self.monitor.display_status()
                    
                    # Sleep for specified interval
                    time.sleep(args.interval)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error during monitoring: {e}")
                    if args.debug:
                        import traceback
                        traceback.print_exc()
                    time.sleep(1)
            
        except Exception as e:
            print(f"Failed to start monitor: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            return 1
        
        finally:
            if self.monitor:
                self.monitor.stop()
            print("Monitor stopped.")
        
        return 0
    
    def run_calibration(self, args):
        """Run battery calibration procedure."""
        print("Starting Battery Calibration...")
        print("=" * 30)
        
        try:
            # TODO: Implement calibration procedure
            print("Calibration procedure not yet implemented.")
            print("This will be a guided calibration process that:")
            print("1. Verifies battery is fully charged")
            print("2. Monitors discharge curve") 
            print("3. Creates custom battery profile")
            print("4. Validates calibration accuracy")
            
            return 0
            
        except Exception as e:
            print(f"Calibration failed: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            return 1
    
    def take_snapshot(self, args):
        """Take diagnostic snapshot."""
        print("Generating diagnostic snapshot...")
        
        try:
            # Initialize sensor manager for readings
            sensor_manager = SensorManager(config_dir=self.config_dir)
            
            # Collect system information
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "system_info": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "hostname": os.uname().nodename if hasattr(os, 'uname') else "unknown"
                },
                "sensor_readings": {},
                "configuration": {},
                "hardware_status": {}
            }
            
            # Try to get sensor readings
            try:
                readings = sensor_manager.read_all_sensors()
                snapshot["sensor_readings"] = readings
            except Exception as e:
                snapshot["sensor_readings"] = {"error": str(e)}
            
            # Save snapshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnostic_snapshot_{timestamp}.json"
            filepath = self.data_dir / "snapshots" / filename
            
            with open(filepath, 'w') as f:
                json.dump(snapshot, f, indent=2)
            
            print(f"Diagnostic snapshot saved to: {filepath}")
            
            if args.output:
                print(json.dumps(snapshot, indent=2))
            
            return 0
            
        except Exception as e:
            print(f"Failed to create snapshot: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            return 1
    
    def test_hardware(self, args):
        """Test hardware connectivity."""
        print("Testing Hardware Connectivity...")
        print("=" * 30)
        
        try:
            # Test I2C connectivity
            print("Testing I2C connectivity...")
            sensor_manager = SensorManager(config_dir=self.config_dir)
            
            if sensor_manager.test_i2c_connection():
                print("✓ I2C connection successful")
            else:
                print("✗ I2C connection failed")
                return 1
            
            # Test sensor readings
            print("Testing sensor readings...")
            try:
                readings = sensor_manager.read_all_sensors()
                print("✓ Sensor readings successful:")
                for sensor, value in readings.items():
                    print(f"  {sensor}: {value}")
            except Exception as e:
                print(f"✗ Sensor reading failed: {e}")
                return 1
            
            # Test LED functionality
            print("Testing LED functionality...")
            try:
                led_manager = LEDManager(config_dir=self.config_dir)
                if led_manager.test_leds():
                    print("✓ LED test successful")
                else:
                    print("✗ LED test failed")
            except Exception as e:
                print(f"✗ LED test error: {e}")
            
            print("Hardware test completed successfully!")
            return 0
            
        except Exception as e:
            print(f"Hardware test failed: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            return 1
    
    def show_status(self, args):
        """Show current UPS status."""
        try:
            sensor_manager = SensorManager(config_dir=self.config_dir)
            readings = sensor_manager.read_all_sensors()
            
            print("Current UPS Status:")
            print("=" * 20)
            
            for sensor, value in readings.items():
                print(f"{sensor}: {value}")
            
            return 0
            
        except Exception as e:
            print(f"Failed to get status: {e}")
            return 1


def create_argument_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Raspberry Pi Geekworm X1201 UPS Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --monitor                    Start monitoring with default settings
  %(prog)s --monitor --interval 10     Monitor with 10-second intervals
  %(prog)s --calibrate                 Run battery calibration
  %(prog)s --snapshot                  Generate diagnostic snapshot
  %(prog)s --test-hardware             Test hardware connectivity
  %(prog)s --status                    Show current status
        """
    )
    
    # Main operation modes (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--monitor", action="store_true",
        help="Start UPS monitoring"
    )
    mode_group.add_argument(
        "--calibrate", action="store_true",
        help="Run battery calibration procedure"
    )
    mode_group.add_argument(
        "--snapshot", action="store_true",
        help="Generate diagnostic snapshot"
    )
    mode_group.add_argument(
        "--test-hardware", action="store_true",
        help="Test hardware connectivity"
    )
    mode_group.add_argument(
        "--status", action="store_true",
        help="Show current UPS status"
    )
    
    # Monitoring options
    parser.add_argument(
        "--interval", type=float, default=5.0,
        help="Update interval in seconds (default: 5.0)"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress normal output"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable debug output"
    )
    
    # Output options
    parser.add_argument(
        "--output", action="store_true",
        help="Output data to stdout (for snapshot mode)"
    )
    parser.add_argument(
        "--log-file", type=str,
        help="Log file path (default: data/logs/ups_monitor.log)"
    )
    
    # Configuration options
    parser.add_argument(
        "--config-dir", type=str, default="config",
        help="Configuration directory (default: config)"
    )
    parser.add_argument(
        "--data-dir", type=str, default="data",
        help="Data directory (default: data)"
    )
    
    return parser


def main():
    """Main entry point for CLI application."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Create application instance
    app = UPSCLIApplication()
    
    # Override directories if specified
    if args.config_dir:
        app.config_dir = Path(args.config_dir)
    if args.data_dir:
        app.data_dir = Path(args.data_dir)
    
    # Setup directories
    app._setup_directories()
    
    # Setup logging
    log_file = args.log_file or str(app.data_dir / "logs" / "ups_monitor.log")
    setup_logging(log_file, debug=args.debug)
    
    # Route to appropriate handler
    try:
        if args.monitor:
            return app.run_monitor(args)
        elif args.calibrate:
            return app.run_calibration(args)
        elif args.snapshot:
            return app.take_snapshot(args)
        elif args.test_hardware:
            return app.test_hardware(args)
        elif args.status:
            return app.show_status(args)
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 130  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())