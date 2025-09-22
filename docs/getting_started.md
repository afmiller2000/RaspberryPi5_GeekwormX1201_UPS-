# Getting Started

Welcome to the Raspberry Pi Geekworm X1201 UPS Monitor project! This guide will help you get up and running quickly.

## Prerequisites

### Hardware Requirements
- Raspberry Pi 4B or 5 (recommended)
- Geekworm X1201 UPS HAT v1.1 or newer
- MicroSD card (32GB+ recommended)
- 18650 batteries (1 or 2, depending on your needs)

### Software Requirements
- Raspberry Pi OS (Bookworm or newer) or Ubuntu 22.04+
- Python 3.8 or newer
- I2C interface enabled

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/afmiller2000/RaspberryPi5_GeekwormX1201_UPS-.git
cd RaspberryPi5_GeekwormX1201_UPS-
```

### 2. Enable I2C Interface

On Raspberry Pi OS:
```bash
sudo raspi-config
# Navigate to: Interface Options > I2C > Enable
sudo reboot
```

On Ubuntu:
```bash
# Add to /boot/firmware/config.txt
echo "dtparam=i2c_arm=on" | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

### 3. Install System Dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-venv i2c-tools git
```

### 4. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 5. Verify Hardware Connection

```bash
# Check I2C devices
sudo i2cdetect -y 1

# Should show UPS device at address 0x36 (or similar)
# Run hardware diagnostic
./scripts/i2c_scan.sh
```

## Quick Start

### Basic Monitoring

```bash
# Activate virtual environment
source venv/bin/activate

# Start basic monitoring
python src/cli.py --monitor

# Run with debug output
python src/cli.py --monitor --debug

# Generate diagnostic snapshot
python src/cli.py --snapshot
```

### Configuration

1. **Copy example configurations:**
```bash
cp config/led_mapping.yaml config/local_led_mapping.yaml
cp config/battery_profiles.yaml config/local_battery_profiles.yaml
```

2. **Edit configurations for your setup:**
```bash
nano config/local_battery_profiles.yaml
# Adjust for your battery type and capacity
```

### System Service (Optional)

To run the monitor as a background service:

```bash
# Install service
sudo cp service/ups-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ups-monitor.service
sudo systemctl start ups-monitor.service

# Check status
sudo systemctl status ups-monitor.service
```

## Basic Usage

### Command Line Interface

```bash
# Display help
python src/cli.py --help

# Monitor with refresh every 5 seconds
python src/cli.py --monitor --interval 5

# Run calibration routine
python src/cli.py --calibrate

# Export diagnostic snapshot
python src/cli.py --snapshot --output diagnostics.json

# Test hardware connectivity
python src/cli.py --test-hardware
```

### Understanding the Display

The monitor shows several key metrics:

```
Battery Voltage: 3.97V
Battery Remaining: 23%
LED1: 23% (RED)
LED2: --- (GREEN)
LED3: --- (GREEN)  
LED4: --- (GREEN)

AC Input Voltage: 5.10V
AC Input Current: 0.8A
DC Output Voltage: 5.00V
DC Output Current: 0.8A
```

## Configuration Files

### LED Mapping (`config/led_mapping.yaml`)
Controls how battery levels are displayed on LEDs.

### Battery Profiles (`config/battery_profiles.yaml`)
Defines voltage curves for different battery types.

### Hardware Calibration (`config/hardware_calibration.yaml`)
Stores calibration values for accurate readings.

## Troubleshooting

### Common Issues

1. **"No I2C device found"**
   - Ensure I2C is enabled: `sudo raspi-config`
   - Check connections between Pi and UPS HAT
   - Run: `sudo i2cdetect -y 1`

2. **Permission errors**
   - Make sure you're in the correct group: `sudo usermod -a -G i2c $USER`
   - Log out and log back in

3. **Incorrect readings**
   - Run calibration: `python src/cli.py --calibrate`
   - Check battery profile settings

4. **Service won't start**
   - Check logs: `sudo journalctl -u ups-monitor.service -f`
   - Verify file paths in service file

### Getting Help

- Check the [Troubleshooting Guide](troubleshooting.md)
- Review [GitHub Issues](https://github.com/afmiller2000/RaspberryPi5_GeekwormX1201_UPS-/issues)
- Create a diagnostic snapshot: `python src/cli.py --snapshot`

## Next Steps

- Read the [Calibration Guide](calibration_guide.md) for accurate battery monitoring
- Check the [Project Roadmap](roadmap.md) for upcoming features
- Consider contributing to the project - see [CONTRIBUTING.md](../CONTRIBUTING.md)

## Safety Notes

⚠️ **Important Safety Information:**

- Always use appropriate 18650 batteries with protection circuits
- Never leave batteries charging unattended
- Monitor temperature during operation
- Follow proper shutdown procedures during low battery conditions
- Keep firmware updated for latest safety features