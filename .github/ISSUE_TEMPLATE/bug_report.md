---
name: Bug report
about: Create a report to help us improve
title: ''
labels: 'bug'
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**System Information (please complete the following information):**
- Raspberry Pi Model: [e.g., Pi 4B, Pi 5]
- OS: [e.g., Raspberry Pi OS, Ubuntu 22.04]
- Python Version: [e.g., 3.9.2]
- UPS Firmware Version: [e.g., v1.1]
- Project Version: [e.g., commit hash or release tag]

**Hardware Information:**
- UPS Model: [e.g., Geekworm X1201 v1.1]
- Battery Configuration: [e.g., single 18650, dual 18650]
- External Power Supply: [e.g., official Pi PSU, 3rd party]

**Logs**
Please include relevant log files or diagnostic information:
- Error messages from console
- Contents of `data/logs/` directory
- Output from `python src/cli.py --diagnostics`
- I2C scan results: `sudo i2cdetect -y 1`

**Additional context**
Add any other context about the problem here.