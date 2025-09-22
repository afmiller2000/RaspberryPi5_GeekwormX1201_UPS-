# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Raspberry Pi Geekworm X1201 UPS Monitor.

## Quick Diagnostic

Run the built-in diagnostic tool first:
```bash
python src/cli.py --diagnostics
```

This will generate a comprehensive report including:
- I2C device status
- Hardware connections
- Software versions
- Configuration validation
- Recent error logs

## Common Issues

### 1. No UPS Device Detected

**Symptoms:**
- "No I2C device found at address 0x36"
- Monitor shows all zero values
- I2C scan shows empty results

**Diagnosis:**
```bash
# Check I2C status
sudo i2cdetect -y 1

# Check I2C interface
ls -la /dev/i2c*

# Verify I2C is enabled
sudo raspi-config
# Interface Options > I2C > Check if enabled
```

**Solutions:**

1. **Enable I2C Interface:**
```bash
sudo raspi-config
# Interface Options > I2C > Enable
sudo reboot
```

2. **Check Physical Connections:**
   - Ensure UPS HAT is firmly seated on GPIO pins
   - Check for bent or damaged pins
   - Verify no loose connections

3. **Install I2C Tools:**
```bash
sudo apt update
sudo apt install i2c-tools
```

4. **Add User to I2C Group:**
```bash
sudo usermod -a -G i2c $USER
# Log out and log back in
```

### 2. Incorrect Battery Readings

**Symptoms:**
- Battery percentage doesn't match actual charge
- Voltage readings seem wrong
- Runtime estimates are inaccurate

**Diagnosis:**
```bash
# Check raw voltage readings
python src/cli.py --raw-voltage

# Compare with multimeter reading
# Difference should be < 0.1V
```

**Solutions:**

1. **Calibrate Battery:**
```bash
python src/cli.py --calibrate
# Follow the guided calibration process
```

2. **Check Battery Profile:**
```bash
nano config/battery_profiles.yaml
# Ensure correct battery type is selected
```

3. **Verify Battery Health:**
   - Old batteries may not hold charge properly
   - Check for physical damage or swelling
   - Test with known good battery

### 3. Service Won't Start

**Symptoms:**
- systemd service fails to start
- Service exits immediately
- "Failed to start ups-monitor.service"

**Diagnosis:**
```bash
# Check service status
sudo systemctl status ups-monitor.service

# View service logs
sudo journalctl -u ups-monitor.service -f

# Check service file
cat /etc/systemd/system/ups-monitor.service
```

**Solutions:**

1. **Fix File Paths:**
```bash
# Edit service file
sudo nano /etc/systemd/system/ups-monitor.service

# Ensure paths are correct:
# WorkingDirectory=/home/pi/RaspberryPi5_GeekwormX1201_UPS-
# ExecStart=/home/pi/RaspberryPi5_GeekwormX1201_UPS-/venv/bin/python src/cli.py --monitor
```

2. **Fix Permissions:**
```bash
# Make sure service user has access
sudo chown -R pi:pi /home/pi/RaspberryPi5_GeekwormX1201_UPS-
chmod +x src/cli.py
```

3. **Reload and Restart:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ups-monitor.service
sudo systemctl start ups-monitor.service
```

### 4. LED Display Not Working

**Symptoms:**
- Physical LEDs don't match displayed status
- LEDs stay on/off regardless of battery level
- Incorrect LED colors

**Diagnosis:**
```bash
# Test LED functionality
python src/cli.py --test-leds

# Check LED mapping configuration
cat config/led_mapping.yaml
```

**Solutions:**

1. **Update LED Configuration:**
```bash
nano config/led_mapping.yaml
# Adjust LED pin assignments and logic
```

2. **Check GPIO Permissions:**
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
```

3. **Test Individual LEDs:**
```bash
# Manual LED control for testing
python src/cli.py --led-test --led 1 --state on
```

### 5. High CPU Usage

**Symptoms:**
- System becomes slow when monitor is running
- High CPU usage in htop/top
- Thermal throttling

**Diagnosis:**
```bash
# Monitor CPU usage
htop
# Look for python processes using high CPU

# Check monitoring interval
python src/cli.py --status
```

**Solutions:**

1. **Increase Monitoring Interval:**
```bash
# Edit configuration or use command line
python src/cli.py --monitor --interval 10
# Increases from default 5s to 10s
```

2. **Optimize Logging:**
```bash
nano config/logger_config.yaml
# Reduce log verbosity
# Disable debug logging in production
```

3. **Check for Infinite Loops:**
   - Review recent code changes
   - Check error logs for repeated errors

### 6. Memory Leaks

**Symptoms:**
- Memory usage increases over time
- System becomes unresponsive after days/weeks
- Out of memory errors

**Diagnosis:**
```bash
# Monitor memory usage
free -h
# Watch for increasing memory usage over time

# Use memory profiler
pip install memory-profiler
python -m memory_profiler src/cli.py --monitor
```

**Solutions:**

1. **Restart Service Regularly:**
```bash
# Add to crontab for daily restart
0 3 * * * sudo systemctl restart ups-monitor.service
```

2. **Update Dependencies:**
```bash
pip install --upgrade -r requirements.txt
```

3. **Check for Resource Leaks in Code:**
   - Review file handle usage
   - Ensure proper cleanup of I2C connections

### 7. Configuration Errors

**Symptoms:**
- "Configuration file not found"
- "Invalid YAML syntax"
- Settings not being applied

**Diagnosis:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/led_mapping.yaml'))"

# Check file permissions
ls -la config/
```

**Solutions:**

1. **Fix YAML Syntax:**
```bash
# Use a YAML validator
python -m yaml config/led_mapping.yaml
```

2. **Reset to Defaults:**
```bash
# Backup current config
cp config/led_mapping.yaml config/led_mapping.yaml.backup

# Copy from example
cp config/examples/led_mapping.yaml config/
```

3. **Check File Permissions:**
```bash
chmod 644 config/*.yaml
```

## Hardware-Specific Issues

### Raspberry Pi 5 Compatibility

**Issue:** GPIO changes in Pi 5 may affect functionality

**Solution:**
```bash
# Update GPIO library
pip install --upgrade RPi.GPIO

# Check for Pi 5 specific code paths
python src/cli.py --hardware-info
```

### Power Supply Issues

**Issue:** Inadequate power supply causes instability

**Diagnosis:**
- Check for rainbow square in top-right corner
- Monitor voltage: `sudo vcgencmd measure_volts`
- Should be > 4.8V under load

**Solution:**
- Use official Raspberry Pi power supply
- Check cable quality
- Monitor power consumption

### Temperature Issues

**Issue:** High temperatures affect battery readings

**Diagnosis:**
```bash
# Check CPU temperature
vcgencmd measure_temp

# Check UPS temperature
python src/cli.py --temperature
```

**Solution:**
- Improve ventilation/cooling
- Enable temperature compensation
- Monitor thermal throttling

## Network and Connectivity

### SSH Connection Issues

**Issue:** Can't connect remotely to monitor status

**Solution:**
```bash
# Enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Check firewall
sudo ufw status
```

### Remote Monitoring Setup

**Issue:** Want to monitor UPS from another device

**Solution:**
```bash
# Install web interface (future feature)
# For now, use SSH or log file monitoring

# Monitor logs remotely
tail -f data/logs/ups_monitor.log
```

## Performance Optimization

### Reduce I2C Traffic

```bash
# Adjust reading frequency in config
nano config/sensor_config.yaml

sensor_polling:
  voltage_interval: 5    # Read voltage every 5 seconds
  current_interval: 2    # Read current every 2 seconds
  temperature_interval: 30  # Read temperature every 30 seconds
```

### Optimize Logging

```bash
# Configure log rotation
nano config/logging.yaml

logging:
  level: INFO  # Change from DEBUG in production
  max_size: 10MB
  backup_count: 5
  rotation: daily
```

## Getting Additional Help

### Create Diagnostic Report

```bash
# Generate comprehensive diagnostic report
python src/cli.py --full-diagnostics > diagnostic_report.txt

# Include in GitHub issue or support request
```

### Useful Debug Commands

```bash
# Enable verbose logging
python src/cli.py --monitor --verbose

# Test individual components
python src/cli.py --test-sensors
python src/cli.py --test-leds
python src/cli.py --test-i2c

# Export configuration
python src/cli.py --export-config > current_config.json
```

### Log File Locations

- **Application logs:** `data/logs/ups_monitor.log`
- **System logs:** `sudo journalctl -u ups-monitor.service`
- **I2C errors:** `dmesg | grep i2c`
- **GPIO errors:** `dmesg | grep gpio`

### Community Support

- **GitHub Issues:** Report bugs and request features
- **Discussions:** Ask questions and share experiences
- **Wiki:** Community-maintained documentation

Remember to include your diagnostic report and system information when asking for help!