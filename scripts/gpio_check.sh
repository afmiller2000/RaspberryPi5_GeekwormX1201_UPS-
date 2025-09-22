#!/bin/bash
# GPIO Pin Checker for Geekworm X1201 UPS
# Verifies GPIO pin configurations and tests LED functionality

set -e

echo "Raspberry Pi GPIO Checker for UPS Monitor"
echo "========================================="
echo

# GPIO pins used by UPS (from led_mapping.yaml)
LED_PINS=(16 20 21 26)
CONTROL_PINS=(18 19)  # Shutdown signal, power button

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "Warning: Running as non-root user. GPIO access may be limited."
    echo "For full functionality, run with: sudo $0"
    echo
fi

# Function to check if GPIO is exported
check_gpio_export() {
    local pin=$1
    if [ -d "/sys/class/gpio/gpio$pin" ]; then
        echo "GPIO $pin: Exported"
        return 0
    else
        echo "GPIO $pin: Not exported"
        return 1
    fi
}

# Function to export GPIO pin
export_gpio() {
    local pin=$1
    if [ ! -d "/sys/class/gpio/gpio$pin" ]; then
        echo $pin > /sys/class/gpio/export 2>/dev/null || true
        sleep 0.1
    fi
}

# Function to set GPIO direction
set_gpio_direction() {
    local pin=$1
    local direction=$2
    if [ -d "/sys/class/gpio/gpio$pin" ]; then
        echo $direction > /sys/class/gpio/gpio$pin/direction 2>/dev/null || true
    fi
}

# Function to set GPIO value
set_gpio_value() {
    local pin=$1
    local value=$2
    if [ -d "/sys/class/gpio/gpio$pin" ]; then
        echo $value > /sys/class/gpio/gpio$pin/value 2>/dev/null || true
    fi
}

# Function to cleanup GPIO
cleanup_gpio() {
    local pin=$1
    if [ -d "/sys/class/gpio/gpio$pin" ]; then
        echo $pin > /sys/class/gpio/unexport 2>/dev/null || true
    fi
}

echo "Checking GPIO Pin Status:"
echo "------------------------"

# Check LED pins
for pin in "${LED_PINS[@]}"; do
    echo -n "LED GPIO $pin: "
    if [ -c "/dev/gpiomem" ] || [ -w "/sys/class/gpio/export" ]; then
        echo "Accessible"
    else
        echo "Not accessible (need root or gpio group)"
    fi
done

# Check control pins
for pin in "${CONTROL_PINS[@]}"; do
    echo -n "Control GPIO $pin: "
    if [ -c "/dev/gpiomem" ] || [ -w "/sys/class/gpio/export" ]; then
        echo "Accessible"
    else
        echo "Not accessible (need root or gpio group)"
    fi
done

echo
echo "GPIO Groups and Permissions:"
echo "----------------------------"
echo "Current user: $(whoami)"
echo "User groups: $(groups)"

if groups | grep -q gpio; then
    echo "✓ User is in gpio group"
else
    echo "✗ User not in gpio group"
    echo "  Add user to gpio group: sudo usermod -a -G gpio $(whoami)"
    echo "  Then log out and log back in"
fi

echo
echo "Testing LED Functionality:"
echo "-------------------------"

if [[ $EUID -eq 0 ]] || [ -c "/dev/gpiomem" ]; then
    echo "Testing LED pins (will blink each LED)..."
    
    # Test each LED pin
    for pin in "${LED_PINS[@]}"; do
        echo "Testing LED on GPIO $pin..."
        
        # Export GPIO
        export_gpio $pin
        set_gpio_direction $pin "out"
        
        # Blink LED
        for i in {1..3}; do
            set_gpio_value $pin 1
            sleep 0.2
            set_gpio_value $pin 0
            sleep 0.2
        done
        
        echo "  GPIO $pin test completed"
        
        # Cleanup
        cleanup_gpio $pin
    done
    
    echo "LED test sequence completed"
else
    echo "Skipping LED test (requires root or gpio access)"
    echo "Run with sudo to test LED functionality"
fi

echo
echo "GPIO Configuration Check:"
echo "------------------------"

# Check device tree configuration
if [ -f /boot/config.txt ]; then
    CONFIG_FILE="/boot/config.txt"
elif [ -f /boot/firmware/config.txt ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
else
    CONFIG_FILE=""
fi

if [ -n "$CONFIG_FILE" ]; then
    echo "Checking $CONFIG_FILE for GPIO settings:"
    
    # Check for GPIO-related settings
    if grep -q "gpio" "$CONFIG_FILE"; then
        echo "GPIO settings found:"
        grep "gpio" "$CONFIG_FILE" | grep -v "^#"
    else
        echo "No GPIO settings found in config"
    fi
    
    # Check for conflicting settings
    if grep -q "audio=on" "$CONFIG_FILE"; then
        echo "⚠ WARNING: Audio is enabled, may conflict with GPIO pins"
    fi
else
    echo "Boot configuration file not found"
fi

echo
echo "Hardware Information:"
echo "--------------------"
echo "GPIO Hardware: $(cat /proc/device-tree/soc/gpio*/compatible 2>/dev/null | head -1 || echo 'Unknown')"
echo "GPIO Memory: $(ls -la /dev/gpio* 2>/dev/null || echo 'No GPIO devices found')"

echo
echo "Kernel Modules:"
echo "--------------"
echo "GPIO modules loaded:"
lsmod | grep gpio || echo "No GPIO modules found"

echo
echo "Recommendations:"
echo "---------------"

# Check for common issues
ISSUES=0

if ! groups | grep -q gpio; then
    echo "1. Add user to gpio group: sudo usermod -a -G gpio $(whoami)"
    ((ISSUES++))
fi

if [ ! -c "/dev/gpiomem" ]; then
    echo "2. GPIO memory device not found - may need kernel update"
    ((ISSUES++))
fi

if [ -z "$(lsmod | grep gpio)" ]; then
    echo "3. No GPIO kernel modules loaded - may need device tree update"
    ((ISSUES++))
fi

if [ $ISSUES -eq 0 ]; then
    echo "✓ GPIO configuration appears correct"
    echo "  You should be able to control LEDs from the UPS monitor"
else
    echo "Found $ISSUES potential issues that may affect GPIO functionality"
fi

echo
echo "GPIO check completed."