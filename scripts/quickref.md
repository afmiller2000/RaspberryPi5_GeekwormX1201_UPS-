# Quick Reference Guide

## Command Line Usage

### Basic Commands
```bash
# Start monitoring
python src/cli.py --monitor

# Show current status
python src/cli.py --status

# Test hardware
python src/cli.py --test-hardware

# Generate diagnostic snapshot
python src/cli.py --snapshot

# Run calibration
python src/cli.py --calibrate
```

### Advanced Options
```bash
# Monitor with custom interval
python src/cli.py --monitor --interval 10

# Debug mode
python src/cli.py --monitor --debug

# Quiet mode (minimal output)
python src/cli.py --monitor --quiet

# Custom config/data directories
python src/cli.py --monitor --config-dir /custom/config --data-dir /custom/data
```

## Hardware Testing

### I2C Testing
```bash
# Scan for I2C devices
./scripts/i2c_scan.sh

# Manual I2C detection
sudo i2cdetect -y 1

# Test UPS communication
sudo i2cget -y 1 0x36 0x00
```

### GPIO Testing
```bash
# Check GPIO configuration
./scripts/gpio_check.sh

# Add user to gpio group
sudo usermod -a -G gpio $USER
# Then logout and login again
```

## Configuration Files

### LED Mapping (`config/led_mapping.yaml`)
```yaml
battery_levels:
  critical: {range: [0, 5], pattern: {LED1: "BLINK_FAST"}}
  low: {range: [6, 25], pattern: {LED1: "ON"}}
  medium: {range: [26, 50], pattern: {LED1: "ON", LED2: "ON"}}
  high: {range: [51, 75], pattern: {LED1: "ON", LED2: "ON", LED3: "ON"}}
  full: {range: [76, 100], pattern: {LED1: "ON", LED2: "ON", LED3: "ON", LED4: "ON"}}
```

### Battery Profiles (`config/battery_profiles.yaml`)
```yaml
18650_standard:
  chemistry: "Li-ion"
  capacity_mah: 2500
  voltage_curve:
    100: 4.20
    50: 3.75
    0: 2.50
```

## Troubleshooting

### Common Issues

#### "No I2C device found"
1. Enable I2C: `sudo raspi-config` → Interface Options → I2C
2. Check connections: Run `./scripts/i2c_scan.sh`
3. Reboot system: `sudo reboot`

#### "Permission denied" errors
1. Add to gpio group: `sudo usermod -a -G gpio $USER`
2. Add to i2c group: `sudo usermod -a -G i2c $USER`
3. Logout and login again

#### Incorrect battery readings
1. Run calibration: `python src/cli.py --calibrate`
2. Check battery profile in `config/battery_profiles.yaml`
3. Verify hardware connections

#### LEDs not working
1. Check GPIO permissions: `./scripts/gpio_check.sh`
2. Verify pin mapping in `config/led_mapping.yaml`
3. Test hardware: `python src/cli.py --test-hardware`

## File Locations

### Configuration
- `config/led_mapping.yaml` - LED display configuration
- `config/battery_profiles.yaml` - Battery type profiles
- `config/hardware_calibration.yaml` - Hardware calibration data

### Data
- `data/logs/ups_monitor.log` - Application logs
- `data/logs/events.json` - Event history
- `data/snapshots/` - Diagnostic snapshots
- `data/calibrations/` - Calibration data

### Scripts
- `scripts/i2c_scan.sh` - I2C device scanner
- `scripts/gpio_check.sh` - GPIO configuration checker
- `scripts/ups1.sh` - UPS control script

## LED Status Codes

### Battery Level
- **4 LEDs**: 76-100% (Green)
- **3 LEDs**: 51-75% (Green)
- **2 LEDs**: 26-50% (Yellow)
- **1 LED**: 5-25% (Red)
- **Blinking**: <5% (Critical)

### Power Status
- **Solid**: On AC power
- **Pulsing**: Charging
- **Slow blink**: On battery power
- **Fast blink**: Critical battery

### System Status
- **All blinking**: System fault
- **Alternating**: Communication error

## Service Installation

### systemd Service
```bash
# Install service
sudo cp service/ups-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ups-monitor.service
sudo systemctl start ups-monitor.service

# Check status
sudo systemctl status ups-monitor.service

# View logs
sudo journalctl -u ups-monitor.service -f
```

## Emergency Procedures

### Low Battery Shutdown
1. System will warn at 25% battery
2. Critical alert at 5% battery
3. Automatic shutdown at 3% battery

### Manual Shutdown
```bash
# Graceful shutdown
sudo shutdown -h now

# Emergency power off
sudo poweroff
```

### Reset Configuration
```bash
# Backup current config
cp -r config config.backup

# Reset to defaults
git checkout HEAD -- config/

# Or manually edit configuration files
```

## Development

### Mock Mode (No Hardware)
The system includes mock implementations for development without hardware:
```bash
# All commands work without hardware
python src/cli.py --monitor --debug
```

### Adding Custom Battery Profile
1. Edit `config/battery_profiles.yaml`
2. Add new profile with voltage curve
3. Update `config/hardware_calibration.yaml` to use new profile
4. Run calibration to fine-tune

### Custom LED Patterns
1. Edit `config/led_mapping.yaml`
2. Define custom patterns for different states
3. Test with: `python src/cli.py --test-hardware`

## Support

### Getting Help
1. Check logs: `data/logs/ups_monitor.log`
2. Create diagnostic snapshot: `python src/cli.py --snapshot`
3. Run hardware test: `python src/cli.py --test-hardware`
4. Check documentation in `docs/`

### Reporting Issues
Include the following in bug reports:
1. Diagnostic snapshot
2. Hardware test results
3. System information (Pi model, OS version)
4. Relevant log files