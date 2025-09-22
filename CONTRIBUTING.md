# Contributing to Raspberry Pi Geekworm X1201 UPS Monitor

Thank you for your interest in contributing to the Raspberry Pi Geekworm X1201 UPS Monitor project! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)
- [Code Style](#code-style)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/RaspberryPi5_GeekwormX1201_UPS-.git
   cd RaspberryPi5_GeekwormX1201_UPS-
   ```

3. **Set up the development environment**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Verify your setup**:
   ```bash
   # Run tests to ensure everything works
   python -m pytest tests/
   
   # Check basic functionality
   python src/cli.py --help
   ```

## Development Workflow

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the project structure:
   - Core logic goes in `src/monitor/`
   - Configuration files in `config/`
   - Documentation in `docs/`
   - Tests in `tests/`

3. **Test your changes**:
   ```bash
   # Run all tests
   python -m pytest tests/
   
   # Run specific tests
   python -m pytest tests/test_sensors.py -v
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

## Testing

We use pytest for testing. Please ensure all tests pass before submitting a PR.

### Running Tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src tests/

# Run specific test file
python -m pytest tests/test_sensors.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Place test files in the `tests/` directory
- Name test files with the `test_` prefix
- Use descriptive test function names
- Include both unit tests and integration tests where appropriate

## Submitting Changes

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub with:
   - Clear title and description
   - Reference any related issues
   - Include screenshots for UI changes
   - List any breaking changes

3. **Respond to feedback** and make necessary changes

4. **Ensure CI passes** - all automated checks must pass

## Issue Reporting

When reporting bugs or requesting features:

1. **Use the appropriate issue template**
2. **Include system information**:
   - Raspberry Pi model
   - Operating system version
   - Python version
   - UPS firmware version

3. **Provide reproduction steps** for bugs
4. **Include logs** when relevant (see `data/logs/` directory)
5. **Use diagnostic snapshots** when reporting sensor issues

## Code Style

### Python Style Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where appropriate
- Write descriptive docstrings for functions and classes
- Keep line length under 88 characters
- Use meaningful variable names

### Project Structure Guidelines

- **Core logic**: Place in `src/monitor/` modules
- **Configuration**: Use YAML files in `config/`
- **Scripts**: Shell scripts go in `scripts/`
- **Documentation**: Markdown files in `docs/`

### Hardware Integration

When working with hardware:

- Always include safety checks
- Use proper error handling for I2C communication
- Test on actual hardware when possible
- Document hardware-specific requirements

### Commit Message Format

Use clear, descriptive commit messages:

```
Add feature: brief description

Longer description if needed, explaining:
- What was changed
- Why it was changed
- Any breaking changes
```

## Development Setup for Hardware

If you have access to the actual Geekworm X1201 UPS:

1. **Enable I2C** on your Raspberry Pi:
   ```bash
   sudo raspi-config
   # Interface Options -> I2C -> Enable
   ```

2. **Install hardware dependencies**:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-smbus i2c-tools
   ```

3. **Verify I2C connection**:
   ```bash
   sudo i2cdetect -y 1
   ```

4. **Run hardware tests**:
   ```bash
   ./scripts/i2c_scan.sh
   python src/cli.py --test-hardware
   ```

## Documentation

- Update relevant documentation when making changes
- Include code examples in docstrings
- Update the README.md if adding new features
- Add screenshots for UI changes

## Getting Help

- Open an issue for questions
- Check existing issues and documentation
- Join our community discussions

## Recognition

Contributors will be recognized in our README.md and release notes. Thank you for helping make this project better!