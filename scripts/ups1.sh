#!/bin/bash
# UPS Control Script for Geekworm X1201
# Provides basic UPS control and status functions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_CMD="python3"

# Check if virtual environment exists
if [ -d "$PROJECT_DIR/venv" ]; then
    PYTHON_CMD="$PROJECT_DIR/venv/bin/python"
fi

# Function to display usage
show_usage() {
    echo "UPS Control Script for Geekworm X1201"
    echo "====================================="
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  status          Show current UPS status"
    echo "  monitor         Start monitoring (foreground)"
    echo "  test            Test UPS connectivity"
    echo "  snapshot        Generate diagnostic snapshot"
    echo "  calibrate       Run battery calibration"
    echo "  led-test        Test LED functionality"
    echo "  start-service   Start systemd service"
    echo "  stop-service    Stop systemd service"
    echo "  install-service Install systemd service"
    echo
    echo "Options:"
    echo "  -h, --help      Show this help message"
    echo "  -d, --debug     Enable debug output"
    echo "  -q, --quiet     Quiet mode"
    echo "  -i, --interval  Monitor interval in seconds (default: 5)"
    echo
    echo "Examples:"
    echo "  $0 status                    # Show current status"
    echo "  $0 monitor -i 10            # Monitor with 10s interval"
    echo "  $0 test                     # Test hardware"
    echo "  $0 install-service          # Install as system service"
}

# Function to check if UPS monitor is available
check_ups_monitor() {
    if [ ! -f "$PROJECT_DIR/src/cli.py" ]; then
        echo "ERROR: UPS monitor not found at $PROJECT_DIR/src/cli.py"
        echo "Make sure you're running this script from the correct directory"
        exit 1
    fi
}

# Function to show UPS status
show_status() {
    echo "Checking UPS Status..."
    echo "====================="
    $PYTHON_CMD "$PROJECT_DIR/src/cli.py" --status "$@"
}

# Function to start monitoring
start_monitor() {
    echo "Starting UPS Monitor..."
    echo "======================"
    $PYTHON_CMD "$PROJECT_DIR/src/cli.py" --monitor "$@"
}

# Function to test UPS
test_ups() {
    echo "Testing UPS Hardware..."
    echo "======================"
    $PYTHON_CMD "$PROJECT_DIR/src/cli.py" --test-hardware "$@"
}

# Function to generate snapshot
generate_snapshot() {
    echo "Generating Diagnostic Snapshot..."
    echo "================================"
    $PYTHON_CMD "$PROJECT_DIR/src/cli.py" --snapshot "$@"
}

# Function to run calibration
run_calibration() {
    echo "Starting Battery Calibration..."
    echo "=============================="
    $PYTHON_CMD "$PROJECT_DIR/src/cli.py" --calibrate "$@"
}

# Function to test LEDs
test_leds() {
    echo "Testing LED Functionality..."
    echo "==========================="
    
    # Run GPIO check script
    if [ -x "$SCRIPT_DIR/gpio_check.sh" ]; then
        "$SCRIPT_DIR/gpio_check.sh"
    else
        echo "GPIO check script not found or not executable"
    fi
    
    # Run hardware test
    $PYTHON_CMD "$PROJECT_DIR/src/cli.py" --test-hardware
}

# Function to start systemd service
start_service() {
    echo "Starting UPS Monitor Service..."
    if systemctl is-active --quiet ups-monitor.service; then
        echo "Service is already running"
        systemctl status ups-monitor.service
    else
        sudo systemctl start ups-monitor.service
        echo "Service started"
        systemctl status ups-monitor.service
    fi
}

# Function to stop systemd service
stop_service() {
    echo "Stopping UPS Monitor Service..."
    if systemctl is-active --quiet ups-monitor.service; then
        sudo systemctl stop ups-monitor.service
        echo "Service stopped"
    else
        echo "Service is not running"
    fi
}

# Function to install systemd service
install_service() {
    echo "Installing UPS Monitor Service..."
    echo "================================"
    
    SERVICE_FILE="$PROJECT_DIR/service/ups-monitor.service"
    TARGET_FILE="/etc/systemd/system/ups-monitor.service"
    
    if [ ! -f "$SERVICE_FILE" ]; then
        echo "ERROR: Service file not found at $SERVICE_FILE"
        exit 1
    fi
    
    # Copy service file
    sudo cp "$SERVICE_FILE" "$TARGET_FILE"
    
    # Update paths in service file for current installation
    sudo sed -i "s|/home/pi/RaspberryPi5_GeekwormX1201_UPS-|$PROJECT_DIR|g" "$TARGET_FILE"
    
    # Set correct user
    CURRENT_USER=$(whoami)
    sudo sed -i "s|User=pi|User=$CURRENT_USER|g" "$TARGET_FILE"
    sudo sed -i "s|Group=pi|Group=$CURRENT_USER|g" "$TARGET_FILE"
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable service
    sudo systemctl enable ups-monitor.service
    
    echo "Service installed and enabled"
    echo "Use '$0 start-service' to start the service"
    echo "Use 'sudo journalctl -u ups-monitor.service -f' to view logs"
}

# Main script logic
main() {
    # Check for UPS monitor
    check_ups_monitor
    
    # Parse command
    case "${1:-}" in
        status)
            shift
            show_status "$@"
            ;;
        monitor)
            shift
            start_monitor "$@"
            ;;
        test)
            shift
            test_ups "$@"
            ;;
        snapshot)
            shift
            generate_snapshot "$@"
            ;;
        calibrate)
            shift
            run_calibration "$@"
            ;;
        led-test)
            shift
            test_leds "$@"
            ;;
        start-service)
            start_service
            ;;
        stop-service)
            stop_service
            ;;
        install-service)
            install_service
            ;;
        -h|--help|help)
            show_usage
            ;;
        "")
            echo "ERROR: No command specified"
            echo
            show_usage
            exit 1
            ;;
        *)
            echo "ERROR: Unknown command '$1'"
            echo
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"