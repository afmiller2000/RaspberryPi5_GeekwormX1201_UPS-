#!/usr/bin/env python3
# UPSMonitor.py - GeekWorm X1201 UPS Monitor v32

from typing import Optional
import time
import random  # Mock-up for sensor readings
import sys

# Optional: color helper
def color_text(text: str, color: str) -> str:
    colors = {
        "RED": "\033[91m",
        "GREEN": "\033[92m",
        "YELLOW": "\033[93m",
        "WHITE": "\033[97m",
        "RESET": "\033[0m"
    }
    return f"{colors.get(color.upper(), colors['WHITE'])}{text}{colors['RESET']}"

class UPSMonitor:
    """
    GeekWorm X1201 UPS monitoring class
    Includes sensors, display, LED mapping, runtime, cumulative energy, and snapshots.
    """
    def __init__(self):
        # Initialize sensor readings
        self.battery_voltage: float = 8.35
        self.battery_percentage: float = 100.0
        self.battery_current: float = 1.2
        self.input_voltage: float = 5.1
        self.output_voltage: float = 5.0
        self.load_current: float = 0.8
        self.cpu_temp: float = 45.2
        self.charge_status: str = "Full"

        # Runtime tracking
        self.total_ac_time: float = 0.0
        self.total_battery_time: float = 0.0
        self.cumulative_energy: float = 0.0
        self.start_time: float = time.time()
        self.on_battery: bool = False

        # LED mock-up
        self.LED1: str = "RED"
        self.LED2: str = "GREEN"
        self.LED3: str = "BLINK_RED"

    # --- Sensor functions ---
    def get_bat_voltage(self) -> float:
        """Return battery voltage"""
        return self.battery_voltage

    def get_bat_percentage(self) -> float:
        """Return battery percentage"""
        return self.battery_percentage

    def get_bat_current(self) -> float:
        """Return battery current"""
        return self.battery_current

    def get_input_voltage(self) -> float:
        """Return input voltage"""
        return self.input_voltage

    def get_output_voltage(self) -> float:
        """Return output voltage"""
        return self.output_voltage

    def get_load_current(self) -> float:
        """Return load current"""
        return self.load_current

    def get_cpu_temp(self) -> float:
        """Return CPU temperature"""
        return self.cpu_temp

    def get_charge_status(self) -> str:
        """Return charge status"""
        return self.charge_status

    # --- LED Mapping ---
    def map_leds(self) -> None:
        """
        Map LED states based on battery percentage and AC power.
        Mock-up logic for demonstration.
        """
        if self.battery_percentage > 80:
            self.LED1 = "GREEN"
        else:
            self.LED1 = "RED"

        if self.on_battery:
            self.LED3 = "BLINK_RED"
        else:
            self.LED3 = "RED"

    # --- Display ---
    def display_metrics(self) -> None:
        """Display the full dashboard"""
        self.map_leds()
        ac_status = "ON" if not self.on_battery else "OFF"
        runtime_est = self.estimate_runtime()
        print("-" * 60)
        print(f"{color_text('UPS Monitor v32', 'WHITE')}")
        print(f"F1+E=Exit | F1+S=Snapshot | F1+L=Launch | F1+C/A=Abort")
        print("-" * 60)
        print(f"AC Status: {color_text(ac_status, 'GREEN' if ac_status=='ON' else 'RED')}")
        print(f"Battery: {color_text(f'{self.battery_percentage:.0f}%', 'WHITE')} | Voltage: {color_text(f'{self.battery_voltage:.2f} V', 'WHITE')} | Current: {color_text(f'{self.battery_current:.2f} A', 'WHITE')}")
        print(f"Input Voltage: {color_text(f'{self.input_voltage:.2f} V', 'WHITE')} | Output Voltage: {color_text(f'{self.output_voltage:.2f} V', 'WHITE')}")
        print(f"Load Current: {color_text(f'{self.load_current:.2f} A', 'WHITE')} | Pi Power: {color_text(f'{self.load_current*self.output_voltage:.2f} W', 'WHITE')}")
        print(f"CPU Temp: {color_text(f'{self.cpu_temp:.1f}°C', 'WHITE')} | Charge Status: {color_text(self.charge_status, 'WHITE')}")
        print(f"LED1: {color_text(self.LED1, self.LED1)} | LED2: {color_text(self.LED2, self.LED2)} | LED3: {color_text(self.LED3, self.LED3)}")
        print(f"Total AC Time: {color_text(f'{self.total_ac_time:.1f} s', 'WHITE')} | Total Battery Time: {color_text(f'{self.total_battery_time:.1f} s', 'WHITE')}")
        print(f"Cumulative Energy: {color_text(f'{self.cumulative_energy:.3f} Wh', 'WHITE')} | Estimated Runtime: {color_text(f'{runtime_est:.1f} min', 'WHITE')}")
        print("-" * 60)

    # --- Snapshots ---
    def snapshot_metrics(self, filename: str) -> None:
        """Save a snapshot of current metrics"""
        with open(filename, "a") as f:
            f.write(f"{time.ctime()} - {self.battery_percentage:.0f}% | {self.battery_voltage:.2f} V | {self.battery_current:.2f} A\n")

    # --- Runtime Tracking ---
    def track_runtime(self) -> None:
        """Update total AC and battery times"""
        elapsed = time.time() - self.start_time
        if self.on_battery:
            self.total_battery_time += elapsed
        else:
            self.total_ac_time += elapsed
        self.start_time = time.time()

    # --- Energy Calculation ---
    def calculate_cumulative_energy(self) -> None:
        """Calculate energy in Wh"""
        self.cumulative_energy += self.load_current * self.output_voltage * ((time.time() - self.start_time)/3600)

    # --- Runtime Estimation ---
    def estimate_runtime(self) -> float:
        """Estimate remaining runtime in minutes"""
        if self.battery_current > 0:
            return (self.battery_voltage * (self.battery_percentage/100) / self.load_current) * 60
        return 0.0

    # --- Emergency Abort ---
    def emergency_abort(self) -> None:
        print("F1+Abort detected. Emergency exit.")
        sys.exit(1)

# --- Main ---
if __name__ == "__main__":
    ups = UPSMonitor()

    # Example loop (replace with actual hardware sensor updates)
    try:
        while True:
            # Mock-up: randomly adjust battery percentage for demo
            ups.battery_percentage = max(0, ups.battery_percentage - random.uniform(0, 0.05))
            ups.track_runtime()
            ups.calculate_cumulative_energy()
            ups.display_metrics()
            time.sleep(1)
    except KeyboardInterrupt:
        ups.emergency_abort()