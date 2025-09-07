#!/usr/bin/env python3
"""
UPSMonitor.py v34
Created by: Alex Miller
Date: 2025-09-07

Monitors Geekworm X1201 UPS on a Raspberry Pi.

Features:
- Battery voltage, percentage, current
- AC/DC input/output voltage and current
- Load current
- Power used in watts
- CPU temperature
- Charge status (charging/discharging)
- LED display mapping (number of LEDs active, color-coded)
- Last power event, cumulative energy, estimated runtime
- Snapshot functionality
- Auto-refresh with configurable interval
- Shortcut keys: Refresh, Snapshot, Quit, Launch, Keep on top, Shutdown, Restart
"""

import time
import random  # Mock data, replace with actual UPS readings
import datetime

# =================== CONFIGURABLE OPTIONS ===================
REFRESH_INTERVAL = 10  # seconds
WINDOW_SIZE = (400, 300)  # width x height, for GUI if implemented
BACKGROUND_COLOR = "black"
BORDER_COLOR = "red"

# =================== MOCK UPS DATA FUNCTIONS ===================
# Replace these mocks with actual code to read from UPS HAT or ADC

def get_bat_voltage() -> float:
    """Return battery voltage in volts."""
    return round(random.uniform(3.7, 4.2), 2)

def get_bat_percentage() -> int:
    """Return battery percentage (0-100%)."""
    return int(random.uniform(5, 100))

def get_bat_current() -> float:
    """Return battery current in amperes."""
    return round(random.uniform(0.5, 1.5), 2)

def get_input_voltage() -> float:
    """Return AC input voltage in volts."""
    return round(random.uniform(5.0, 5.2), 2)

def get_input_current() -> float:
    """Return AC input current in amperes."""
    return round(random.uniform(0.5, 1.0), 2)

def get_output_voltage() -> float:
    """Return DC output voltage in volts."""
    return round(random.uniform(4.9, 5.1), 2)

def get_output_current() -> float:
    """Return DC output current in amperes."""
    return round(random.uniform(0.5, 1.0), 2)

def get_load_current() -> float:
    """Return load current in amperes."""
    return get_output_current()

def get_cpu_temp() -> float:
    """Return CPU temperature in Celsius."""
    return round(random.uniform(42.0, 47.0), 1)

# =================== UPS STATE TRACKING ===================
cumulative_battery_time = 0.0  # seconds
last_battery_start = None
cumulative_energy = 0.0  # Wh
last_power_event = "System startup"

# =================== DISPLAY UTILITIES ===================
def map_leds(battery_percent: int):
    """Determine number of LEDs active (1-4) and their colors."""
    if battery_percent >= 76:
        return 4, "green"
    elif battery_percent >= 51:
        return 3, "yellow"
    elif battery_percent >= 26:
        return 2, "orange"
    else:
        return 1, "red"

def color_text(text: str, color: str) -> str:
    """Return color-coded text for terminal display (mock)."""
    colors = {"green": "\033[92m", "yellow": "\033[93m",
              "orange": "\033[33m", "red": "\033[91m", "reset": "\033[0m"}
    return f"{colors.get(color,'')}{text}{colors['reset']}"

# =================== MAIN DASHBOARD DISPLAY ===================
def display_dashboard():
    global last_battery_start, cumulative_battery_time, cumulative_energy, last_power_event
    
    voltage = get_bat_voltage()
    percent = get_bat_percentage()
    bat_current = get_bat_current()
    ac_voltage = get_input_voltage()
    ac_current = get_input_current()
    dc_voltage = get_output_voltage()
    dc_current = get_output_current()
    load = get_load_current()
    cpu_temp = get_cpu_temp()
    
    # Determine AC/DC state
    ac_present = ac_voltage > 0
    if ac_present:
        charge_status = "Charging" if percent < 100 else "Fully charged"
        if last_battery_start:
            duration = time.time() - last_battery_start
            cumulative_battery_time += duration
            last_battery_start = None
        ac_state_str = "On AC Power (Plugged In)"
    else:
        charge_status = "Discharging"
        if not last_battery_start:
            last_battery_start = time.time()
        ac_state_str = "Off AC Power (Running on DC)"
    
    # Update cumulative energy (simplified)
    cumulative_energy += dc_voltage * dc_current * (REFRESH_INTERVAL / 3600)  # Wh

    # LED mapping
    leds_active, led_color = map_leds(percent)
    
    # Last power event formatting
    print(color_text(f"LAST POWER EVENT: {last_power_event}", "red"))
    
    # ------------------ Dashboard ------------------
    print("------------------------------------------------------------")
    print(f"Voltage: {voltage}V")
    print(f"Battery Remaining: {color_text(str(percent)+'%', led_color)}")
    
    for i in range(4, 0, -1):
        if i <= leds_active:
            line_color = led_color
        else:
            line_color = "green"  # dimmed inactive LEDs
        print(f"LED{i}: {color_text(str(percent if i <= leds_active else '---') + '%', line_color)}")
    
    print()
    print(f"AC Input Voltage: {ac_voltage}V")
    print(f"AC Input Current: {ac_current}A")
    print(f"DC Output Voltage: {dc_voltage}V")
    print(f"DC Output Current: {dc_current}A")
    print(f"Load Current: {load}A")
    print(f"Power Used: {round(dc_voltage*dc_current,2)} W")
    print(f"CPU Temp: {cpu_temp}°C")
    print(f"AC Status: {ac_state_str}")
    print(f"Charge Status: {charge_status}")
    print("------------------------------------------------------------")
    
    # Time & energy tracking
    total_ac_time = 0  # Placeholder, can track since reboot
    last_battery_time = 0 if not last_battery_start else time.time() - last_battery_start
    print(f"Total AC Time: {round(total_ac_time,1)}s")
    print(f"Last Battery Time: {round(last_battery_time,1)}s")
    print(f"Cumulative Battery Time: {round(cumulative_battery_time,1)}s")
    print(f"Cumulative Energy: {round(cumulative_energy,3)} Wh")
    
    # Estimated runtime
    estimated_runtime = percent / 100 * 400  # mock estimate
    print(f"Estimated Runtime: {round(estimated_runtime,1)} min")
    print("------------------------------------------------------------")

# =================== AUTO-REFRESH LOOP ===================
def refresh_loop():
    try:
        while True:
            print("\033c", end="")  # Clear terminal
            display_dashboard()
            time.sleep(REFRESH_INTERVAL)
    except KeyboardInterrupt:
        print("Exiting UPS Monitor...")

# =================== MAIN ===================
if __name__ == "__main__":
    refresh_loop()
