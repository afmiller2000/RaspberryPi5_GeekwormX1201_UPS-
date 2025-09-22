# Raspberry Pi Geekworm X1201 UPS Monitor

A comprehensive monitoring and management system for the Geekworm X1201 UPS on Raspberry Pi 5 and other Linux distributions.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4%2B-red.svg)](https://www.raspberrypi.org/)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/afmiller2000/RaspberryPi5_GeekwormX1201_UPS-.git
cd RaspberryPi5_GeekwormX1201_UPS-

# Install dependencies
pip install -r requirements.txt

# Run the monitor
python src/cli.py --monitor
```

## 📁 Repository Structure

```
RaspberryPi5_GeekwormX1201_UPS-/
├── README.md                    # This file
├── CONTRIBUTING.md              # Contribution guidelines
├── CODE_OF_CONDUCT.md          # Community standards
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── .gitignore                  # Git ignore patterns
│
├── .github/                    # GitHub configuration
│   ├── ISSUE_TEMPLATE/         # Bug reports & feature requests
│   ├── PULL_REQUEST_TEMPLATE.md # PR checklist
│   ├── workflows/ci.yml        # GitHub Actions CI/CD
│   └── labels.yml              # Issue/PR labels
│
├── docs/                       # Documentation
│   ├── getting_started.md      # Setup and installation guide
│   ├── calibration_guide.md    # Battery calibration procedures
│   ├── troubleshooting.md      # Common issues and solutions
│   ├── roadmap.md              # Project roadmap
│   ├── screenshots/            # UI screenshots
│   └── specs/                  # Technical specifications
│       ├── ANSI_Colors.md      # Color coding reference
│       ├── Battery_Profiles.md # Battery configuration specs
│       ├── Calibration_Guide.md # Technical calibration details
│       ├── Display_Policy.md   # LED display rules
│       └── Event_Counters.md   # Event tracking specifications
│
├── config/                     # Configuration files
│   ├── led_mapping.yaml        # LED display configuration
│   ├── battery_profiles.yaml   # Battery type profiles
│   └── hardware_calibration.yaml # Hardware calibration data
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── cli.py                  # Command-line interface
│   └── monitor/                # Core monitoring modules
│       ├── __init__.py
│       ├── sensors.py          # Sensor data collection
│       ├── analytics.py        # Data analysis and calculations
│       ├── led.py              # LED display management
│       ├── runtime.py          # Runtime estimation
│       ├── logger.py           # Event logging system
│       └── safeops.py          # Safety operations
│
├── scripts/                    # Utility scripts
│   ├── i2c_scan.sh            # I2C device detection
│   ├── gpio_check.sh          # GPIO pin testing
│   ├── quickref.md            # Quick reference guide
│   └── ups1.sh                # UPS control script
│
├── tests/                      # Test suite
│   ├── test_sensors.py        # Sensor module tests
│   └── test_led.py            # LED module tests
│
├── service/                    # System service files
│   ├── ups-monitor.service    # systemd service configuration
│   └── docker-compose.yml     # Docker deployment
│
├── deploy/                     # Deployment configurations
│   ├── Dockerfile             # Container image definition
│   └── systemd/               # systemd service files
│       └── upsmonitor.service
│
└── data/                      # Runtime data
    ├── logs/                  # Application logs
    └── snapshots/             # Diagnostic snapshots
```

## ✨ Features

### I. Comprehensive Power Monitoring
- **AC Input Monitoring**: Voltage, current, power, and state detection
- **DC Output Monitoring**: Output voltage, current, power with undervoltage alerts
- **Battery Monitoring**: Pack voltage, charge/discharge current, remaining capacity
- **Multi-Bank Support**: Automatic detection of single or dual battery configurations

### II. LED Battery Visualization
- **Always-Visible LED Chart**: 4-row display showing battery status
- **Capacity Mapping**: 76–100% (4 LEDs), 51–75% (3 LEDs), 26–50% (2 LEDs), 5–25% (1 LED), <5% (Critical)
- **Status Indicators**: GOOD, CHARGING, DISCHARGING, CRITICAL, UNKNOWN states

### III. Advanced Analytics
- **Runtime Estimation**: Load-based operational time calculations
- **Power Smoothing**: Exponential moving averages for stable readings
- **Calibration Profiles**: Voltage-to-percentage mapping by battery chemistry

### IV. Event Logging & Diagnostics
- **System Log Integration**: journalctl, dmesg, syslog capture
- **UPS Event Tracking**: AC/DC transitions, battery warnings, fault detection
- **Diagnostic Snapshots**: JSON export for issue reporting

### V. Safety & Reliability
- **Secure Operations**: Sudo requirements for hardware commands
- **Data Protection**: Dry-run enforcement for critical operations
- **System Integrity**: Automatic system updates and documentation sync

### VI. Integration & Extensibility
- **Cross-Platform**: Raspberry Pi OS, Ubuntu, MX Linux support
- **Service Integration**: systemd service for 24/7 monitoring
- **Scalability**: Ready for GUI extensions and containerization

## 🔧 Hardware Requirements

- Raspberry Pi 4B or 5 (recommended)
- Geekworm X1201 UPS HAT v1.1 or newer
- MicroSD card (32GB+ recommended)
- I2C enabled on Raspberry Pi

## 📖 Documentation

- **[Getting Started](docs/getting_started.md)** - Setup and installation
- **[Calibration Guide](docs/calibration_guide.md)** - Battery calibration procedures
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Project Roadmap](docs/roadmap.md)** - Future development plans

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Geekworm for the X1201 UPS hardware design
- Raspberry Pi Foundation for the excellent platform
- The open-source community for inspiration and support
