#!/usr/bin/env python3
"""
UPSMonitor.py v33
Created by Alex Miller - 2025-09-07
Monitor GeekWorm X1201 UPS on Raspberry Pi.
Features:
- Battery voltage, capacity, current
- AC/DC input/output voltage & current
- CPU temp
- Power usage in watts
- LED-based battery and UPS status display
- Runtime tracking, cumulative AC/DC time, energy usage
- Snapshot, refresh, quit, shutdown/restart shortcuts
- Keep-on-top option, 2-second auto refresh
"""

import time
from datetime import datetime
import random  # Mocked data; replace with actual sensor readings
import sys
import os

# -----------------------------
# Helper functions for coloring
# -----------------------------
def color_text(text: str, color: str) -> str:
    colors = {
        "RED": "\033[91m",
        "GREEN": "\033[92m",
        "YELLOW": "\033[93m",
        "ORANGE": "\033[33m",
        "WHITE": "\033[97m",
        "DIM": "\033[2m",
        "RESET": "\033[0m"
    }
    return f"{colors.get(color.upper(),'')}{text}{colors['RESET']}"

# -----------------------------
# UPSMonitor Class
# -----------------------------
class UPSMonitor:
    """
    UPSMonitor class for GeekWorm X1201
    Handles reading battery, AC/DC power, and displaying dashboard
    """

    def __init__(self):
        """Initialize monitor with mock values and counters"""
        self.battery_voltage: float = 3.97
        self.battery_percentage: int = 23
        self.battery_current: float = 1.2
        self.ac_input_voltage: float = 5.10
        self.ac_input_current: float = 0.8
        self.dc_output_voltage: float = 5.00
        self.dc_output_current: float = 0.8
        self.load_current: float = 0.8
        self.cpu_temp: float = 45.2
        self.charge_status: str = "Discharging"
        self.led_status: dict = {"LED1": "RED", "LED2": "GREEN", "LED3": "BLINK_RED"}
        self.total_ac_time: float = 0.0
        self.cumulative_battery_time: float = 0.0
        self.last_battery_time: float = 0.0
        self.cumulative_energy: float = 0.0
        self.start_time: float = time.time()
        self.on_ac_power: bool = True
        self.keep_on_top: bool = False
        self.refresh_interval: float = 2.0

    # -----------------------------
    # Mock sensor readings (replace with actual sensors)
    # -----------------------------
    def update_sensors(self):
        """Update sensor readings (mocked for testing)"""
        self.battery_voltage = round(random.uniform(3.7, 4.2), 2)
        self.battery_percentage = random.randint(5, 100)
        self.battery_current = round(random.uniform(0.5, 1.5), 2)
        self.ac_input_voltage = 5.10
        self.ac_input_current = 0.8
        self.dc_output_voltage = 5.00
        self.dc_output_current = 0.8
        self.load_current = 0.8
        self.cpu_temp = round(random.uniform(40.0, 50.0), 1)
        self.on_ac_power = random.choice([True, False])
        self.charge_status = "Charging" if self.on_ac_power else "Discharging"

    # -----------------------------
    # Runtime calculations
    # -----------------------------
    def update_runtime(self):
        """Update cumulative times"""
        elapsed = time.time() - self.start_time
        if self.on_ac_power:
            self.total_ac_time += elapsed
            if self.last_battery_time:
                self.cumulative_battery_time += self.last_battery_time
                self.last_battery_time = 0
        else:
            self.last_battery_time += elapsed
        self.cumulative_energy += self.load_current * self.dc_output_voltage * (elapsed / 3600)  # Wh
        self.start_time = time.time()

    # -----------------------------
    # LED mapping
    # -----------------------------
    def led_display(self):
        """Return string showing LED battery levels and colors"""
        leds = [
            {"range": (76, 100), "label": "LED4", "color": "GREEN"},
            {"range": (51, 75), "label": "LED3", "color": "YELLOW"},
            {"range": (26, 50), "label": "LED2", "color": "ORANGE"},
            {"range": (5, 25), "label": "LED1", "color": "RED"}
        ]
        output = ""
        for led in leds:
            if self.battery_percentage >= led["range"][0]:
                output += color_text(f"{led['label']}: {self.battery_percentage}%", led["color"]) + "\n"
            else:
                output += color_text(f"{led['label']}: ---", "DIM") + "\n"
        return output

    # -----------------------------
    # Dashboard display
    # -----------------------------
    def display_dashboard(self):
        """Print formatted UPS dashboard"""
        os.system('clear')
        self.update_sensors()
        self.update_runtime()
        header = color_text("UPS Monitor v33", "WHITE")
        shortcuts = color_text("F1R=Refresh | F1S=Snapshot | F1Q/F1A=Quit | F1L=Launch | F1K=Keep on top", "WHITE")
        print(header)
        print(shortcuts)
        print("-" * 60)
        print(f"Voltage: {self.battery_voltage:.2f}V")
        print(f"Battery Remaining: {self.battery_percentage}%")
        print(self.led_display())
        print(f"AC Input Voltage: {self.ac_input_voltage:.2f}V")
        print(f"AC Input Current: {self.ac_input_current:.2f}A")
        print(f"DC Output Voltage: {self.dc_output_voltage:.2f}V")
        print(f"DC Output Current: {self.dc_output_current:.2f}A")
        print(f"Load Current: {self.load_current:.2f}A")
        print(f"Power Used: {self.load_current * self.dc_output_voltage:.2f} W")
        print(f"CPU Temp: {self.cpu_temp:.1f}°C")
        ac_status = "On AC Power (Plugged In)" if self.on_ac_power else "Off AC Power (Running on DC)"
        print(f"AC Status: {ac_status}")
        print(f"Charge Status: {self.charge_status}")
        print("-" * 60)
        print(f"Total AC Time: {self.total_ac_time:.1f}s")
        print(f"Last Battery Time: {self.last_battery_time:.1f}s")
        print(f"Cumulative Battery Time: {self.cumulative_battery_time:.1f}s")
        print(f"Cumulative Energy: {self.cumulative_energy:.3f} Wh")
        estimated_runtime = self.battery_percentage * self.dc_output_voltage * self.dc_output_current / self.load_current
        print(f"Estimated Runtime: {estimated_runtime:.1f} min")
        print("-" * 60)

    # -----------------------------
    # Run dashboard loop
    # -----------------------------
    def run(self):
        """Run the dashboard with auto-refresh"""
        try:
            while True:
                self.display_dashboard()
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\nExiting UPS Monitor...")

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    ups_monitor = UPSMonitor()
    ups_monitor.run()