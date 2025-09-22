# 📚 Example Repository Structure for Geekworm X1201 UPS Monitor

RaspberryPi5_GeekwormX1201_UPS-
├── 0-START_HERE.md
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE
├── .github/
│   ├── workflows/ci.yml
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── DOCS/
│   ├── 0-INDEX.md
│   ├── DESIGN_OVERVIEW.md
│   ├── LED_MAPPING.md
│   ├── BATTERY_GUIDE.md
│   ├── CALIBRATION_GUIDE.md
│   ├── FAQ.md
│   ├── SCREENSHOTS/
│   ├── ROADMAP.md
│   ├── TROUBLESHOOTING.md
│   ├── GLOSSARY.md
│   └── SCRUB.md
├── CONFIG/
│   ├── led_mapping.yaml
│   ├── battery_profiles.yaml
│   ├── hardware_calibration.yaml
│   └── example_config.yaml
├── SRC/
│   ├── __init__.py
│   ├── monitor/
│   │   ├── __init__.py
│   │   ├── sensors.py
│   │   ├── analytics.py
│   │   ├── led.py
│   │   ├── runtime.py
│   │   ├── logger.py
│   │   └── safeops.py
│   ├── cli.py
│   └── gui.py
├── SCRIPTS/
│   ├── i2c_scan.sh
│   ├── quickref.md
│   ├── ups1.sh
│   └── template_script.sh
├── TEMPLATES/
│   ├── config_template.yaml
│   └── eventlog_template.json
├── TESTS/
│   ├── test_sensors.py
│   ├── test_led.py
│   └── test_integration.py
├── DEPLOY/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── systemd/
│       └── ups-monitor.service
├── SERVICE/
│   └── ups-monitor.service
├── DATA/
│   ├── logs/
│   └── snapshots/
├── SCRUB/
│   ├── data_scrubber.py
│   ├── README.md
│   └── examples/
│       └── sample_scrub.yaml
└── REQUIREMENTS.TXT