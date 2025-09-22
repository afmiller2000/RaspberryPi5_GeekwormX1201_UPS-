#!/bin/bash
# I2C Device Scanner for Geekworm X1201 UPS
# This script scans for I2C devices and verifies UPS connectivity

set -e

echo "Raspberry Pi I2C Device Scanner"
echo "==============================="
echo

# Check if running as root for I2C access
if [[ $EUID -ne 0 ]]; then
    echo "Warning: Running as non-root user. May need sudo for I2C access."
    echo
fi

# Check if I2C tools are installed
if ! command -v i2cdetect &> /dev/null; then
    echo "ERROR: i2c-tools not installed"
    echo "Install with: sudo apt-get install i2c-tools"
    exit 1
fi

# Check if I2C interface is enabled
if [ ! -e /dev/i2c-1 ]; then
    echo "ERROR: I2C interface not found at /dev/i2c-1"
    echo "Enable I2C with: sudo raspi-config"
    echo "Navigate to: Interface Options > I2C > Enable"
    exit 1
fi

echo "Scanning I2C bus 1 for devices..."
echo

# Scan I2C bus 1 (default for Raspberry Pi)
i2cdetect -y 1

echo
echo "Device Analysis:"
echo "---------------"

# Check for common UPS addresses
UPS_ADDRESSES=("0x36" "0x17" "0x62")

for addr in "${UPS_ADDRESSES[@]}"; do
    addr_dec=$((addr))
    addr_hex=$(printf "0x%02x" $addr_dec)
    
    echo -n "Checking address $addr_hex: "
    
    if i2cget -y 1 $addr_dec 0x00 &>/dev/null; then
        echo "DEVICE FOUND"
        
        # Try to identify device
        if [ "$addr_hex" = "0x36" ]; then
            echo "  -> Likely Geekworm X1201 UPS"
        elif [ "$addr_hex" = "0x17" ]; then
            echo "  -> Possible UPS secondary address"
        fi
    else
        echo "No device"
    fi
done

echo
echo "System Information:"
echo "------------------"
echo "Raspberry Pi Model: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unknown')"
echo "Kernel Version: $(uname -r)"
echo "I2C Kernel Modules:"
lsmod | grep i2c || echo "  No I2C modules loaded"

echo
echo "I2C Configuration:"
echo "-----------------"
if [ -f /boot/config.txt ]; then
    echo "I2C settings in /boot/config.txt:"
    grep -E "^(dtparam=i2c|device_tree_param=i2c)" /boot/config.txt 2>/dev/null || echo "  No I2C settings found"
elif [ -f /boot/firmware/config.txt ]; then
    echo "I2C settings in /boot/firmware/config.txt:"
    grep -E "^(dtparam=i2c|device_tree_param=i2c)" /boot/firmware/config.txt 2>/dev/null || echo "  No I2C settings found"
else
    echo "  Boot config file not found"
fi

echo
echo "Recommendations:"
echo "---------------"

# Check if UPS is detected
if i2cget -y 1 0x36 0x00 &>/dev/null; then
    echo "✓ UPS detected at address 0x36"
    echo "  The Geekworm X1201 UPS appears to be connected and responding"
    echo "  You can proceed with running the UPS monitor software"
else
    echo "✗ No UPS detected at expected address 0x36"
    echo "  1. Check physical connections between Pi and UPS HAT"
    echo "  2. Ensure UPS HAT is properly seated on GPIO pins"
    echo "  3. Verify power connections and LED indicators on UPS"
    echo "  4. Try reseating the UPS HAT"
fi

echo
echo "Scan completed."