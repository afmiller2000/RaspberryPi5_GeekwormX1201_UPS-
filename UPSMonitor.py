import time
# Replace with the actual GeekWorm UPS library import
# Example: from ups_hat_library import UPS
# Or use smbus/I2C if using direct I2C communication

class MockUPS:
    """Mock class for demonstration. Replace with actual UPS interface."""
    def get_batt_voltage(self):
        return 8.35  # volts
    def get_batt_current(self):
        return 1.2   # amps
    def get_batt_percent(self):
        return 100   # percent
    def get_input_voltage(self):
        return 5.1   # volts
    def get_output_voltage(self):
        return 5.0   # volts
    def get_load_current(self):
        return 0.8   # amps
    def get_charge_status(self):
        return "Charging"  # or "Full", "Discharging"
    def get_temperature(self):
        return 35.2  # Celsius
    def get_power_events(self):
        return ["None"]

# Initialize UPS
ups = MockUPS()  # replace MockUPS with actual UPS class

def map_leds(percent):
    """Map battery percent to LED pattern."""
    leds = ['OFF', 'OFF', 'OFF', 'OFF']  # 4 green LEDs
    for i in range(4):
        if percent >= (i+1)*25:
            leds[i] = 'GREEN'
    return leds

def display_metrics():
    batt_percent = ups.get_batt_percent()
    led_status = map_leds(batt_percent)

    print("------ GeekWorm UPS Status ------")
    print(f"Battery Voltage: {ups.get_batt_voltage():.2f} V")
    print(f"Battery Current: {ups.get_batt_current():.2f} A")
    print(f"Battery Level: {batt_percent}%")
    print(f"Battery LEDs: {led_status}")
    print(f"Input Voltage: {ups.get_input_voltage():.2f} V")
    print(f"Output Voltage: {ups.get_output_voltage():.2f} V")
    print(f"Load Current: {ups.get_load_current():.2f} A")
    print(f"Charging Status: {ups.get_charge_status()}")
    print(f"Temperature: {ups.get_temperature():.1f} °C")
    print(f"Power Events: {ups.get_power_events()}")
    print("--------------------------------\n")

if __name__ == "__main__":
    while True:
        display_metrics()
        time.sleep(5)  # refresh every 5 seconds