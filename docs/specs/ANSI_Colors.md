# ANSI Color Codes Reference

This document defines the ANSI color codes used throughout the UPS Monitor for consistent terminal output and user interface elements.

## Standard Colors

### Basic Colors
```
BLACK   = '\033[30m'    # Black text
RED     = '\033[31m'    # Red text  
GREEN   = '\033[32m'    # Green text
YELLOW  = '\033[33m'    # Yellow text
BLUE    = '\033[34m'    # Blue text
MAGENTA = '\033[35m'    # Magenta text
CYAN    = '\033[36m'    # Cyan text
WHITE   = '\033[37m'    # White text
```

### Bright Colors
```
BRIGHT_BLACK   = '\033[90m'    # Bright black (gray)
BRIGHT_RED     = '\033[91m'    # Bright red
BRIGHT_GREEN   = '\033[92m'    # Bright green
BRIGHT_YELLOW  = '\033[93m'    # Bright yellow
BRIGHT_BLUE    = '\033[94m'    # Bright blue
BRIGHT_MAGENTA = '\033[95m'    # Bright magenta
BRIGHT_CYAN    = '\033[96m'    # Bright cyan
BRIGHT_WHITE   = '\033[97m'    # Bright white
```

### Background Colors
```
BG_BLACK   = '\033[40m'    # Black background
BG_RED     = '\033[41m'    # Red background
BG_GREEN   = '\033[42m'    # Green background
BG_YELLOW  = '\033[43m'    # Yellow background
BG_BLUE    = '\033[44m'    # Blue background
BG_MAGENTA = '\033[45m'    # Magenta background
BG_CYAN    = '\033[46m'    # Cyan background
BG_WHITE   = '\033[47m'    # White background
```

### Text Formatting
```
RESET     = '\033[0m'     # Reset all formatting
BOLD      = '\033[1m'     # Bold text
DIM       = '\033[2m'     # Dim/faint text
ITALIC    = '\033[3m'     # Italic text
UNDERLINE = '\033[4m'     # Underlined text
BLINK     = '\033[5m'     # Blinking text
REVERSE   = '\033[7m'     # Reverse colors
STRIKETHROUGH = '\033[9m' # Strikethrough text
```

## UPS Monitor Color Scheme

### Battery Status Colors
- **CRITICAL (0-5%)**: `BRIGHT_RED + BLINK` - Immediate attention required
- **LOW (6-25%)**: `RED` - Warning state
- **NORMAL (26-75%)**: `YELLOW` - Normal operation
- **GOOD (76-100%)**: `GREEN` - Optimal state

### Power Status Colors
- **AC POWER**: `BRIGHT_GREEN` - External power available
- **BATTERY POWER**: `YELLOW` - Running on battery
- **CHARGING**: `CYAN` - Battery charging
- **FAULT**: `BRIGHT_RED + BOLD` - System fault detected

### LED Representation Colors
- **LED ON**: `BRIGHT_GREEN + BOLD` - Active LED
- **LED OFF**: `DIM + WHITE` - Inactive LED
- **LED BLINKING**: `YELLOW + BLINK` - Blinking LED

### System Status Colors
- **ONLINE**: `GREEN` - System operational
- **OFFLINE**: `RED` - System not responding
- **MAINTENANCE**: `YELLOW` - Maintenance mode
- **ERROR**: `BRIGHT_RED` - Error condition

### Data Value Colors
- **VOLTAGE**: `CYAN` - Voltage readings
- **CURRENT**: `MAGENTA` - Current readings
- **TEMPERATURE**: `YELLOW` - Temperature readings
- **PERCENTAGE**: `GREEN` - Percentage values
- **TIME**: `BLUE` - Time/duration values

## Usage Examples

### Python Implementation
```python
class Colors:
    # Basic colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    
    # Formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    BLINK = '\033[5m'
    RESET = '\033[0m'

def color_text(text, color):
    """Apply color to text with automatic reset."""
    return f"{color}{text}{Colors.RESET}"

def battery_status_color(percentage):
    """Return appropriate color for battery percentage."""
    if percentage <= 5:
        return Colors.BRIGHT_RED + Colors.BLINK
    elif percentage <= 25:
        return Colors.RED
    elif percentage <= 75:
        return Colors.YELLOW
    else:
        return Colors.GREEN
```

### Display Examples
```python
# Battery status display
battery_percent = 23
color = battery_status_color(battery_percent)
print(f"Battery: {color}{battery_percent}%{Colors.RESET}")

# LED status display
led_active = True
led_color = Colors.BRIGHT_GREEN + Colors.BOLD if led_active else Colors.DIM + Colors.WHITE
print(f"LED1: {led_color}●{Colors.RESET}")

# Power status
ac_power = False
power_status = "BATTERY" if not ac_power else "AC"
power_color = Colors.YELLOW if not ac_power else Colors.BRIGHT_GREEN
print(f"Power: {power_color}{power_status}{Colors.RESET}")
```

## Terminal Compatibility

### Supported Terminals
- **Linux Terminal**: Full support
- **macOS Terminal**: Full support
- **Windows Command Prompt**: Limited support (Windows 10+)
- **Windows PowerShell**: Full support (PowerShell 5.1+)
- **SSH Clients**: Depends on client capabilities

### Fallback Behavior
When ANSI colors are not supported:
```python
import sys
import os

def supports_color():
    """Check if terminal supports ANSI color codes."""
    return (
        hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and
        os.environ.get("TERM") != "dumb" and
        os.name != "nt"  # Windows check
    )

def safe_color_text(text, color):
    """Apply color only if terminal supports it."""
    if supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text
```

## Color Accessibility

### Colorblind Considerations
- **Red-Green Colorblind**: Use symbols in addition to colors
- **High Contrast**: Provide high contrast mode option
- **Text Alternatives**: Always include text descriptions

### Alternative Indicators
```python
def battery_indicator(percentage):
    """Provide both color and symbol indicators."""
    if percentage <= 5:
        return f"{Colors.BRIGHT_RED}⚠ CRITICAL{Colors.RESET}"
    elif percentage <= 25:
        return f"{Colors.RED}⚡ LOW{Colors.RESET}"
    elif percentage <= 75:
        return f"{Colors.YELLOW}● NORMAL{Colors.RESET}"
    else:
        return f"{Colors.GREEN}✓ GOOD{Colors.RESET}"
```

## Configuration Options

### Color Themes
Users can select from predefined color themes:

```yaml
# config/colors.yaml
theme: "default"  # default, high_contrast, monochrome, custom

themes:
  default:
    critical: "\033[91m\033[5m"  # bright_red + blink
    warning: "\033[31m"          # red
    normal: "\033[33m"           # yellow
    good: "\033[32m"             # green
    
  high_contrast:
    critical: "\033[97m\033[41m\033[1m"  # white on red, bold
    warning: "\033[30m\033[43m\033[1m"   # black on yellow, bold
    normal: "\033[30m\033[47m"           # black on white
    good: "\033[30m\033[42m\033[1m"      # black on green, bold
    
  monochrome:
    critical: "\033[1m\033[5m"   # bold + blink
    warning: "\033[1m"           # bold
    normal: "\033[0m"            # normal
    good: "\033[2m"              # dim
```

### Custom Colors
```python
def load_color_config():
    """Load color configuration from file."""
    try:
        with open('config/colors.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config['themes'][config['theme']]
    except FileNotFoundError:
        return default_colors()
```

## Best Practices

### Consistent Usage
1. **Always reset**: Use `Colors.RESET` after colored text
2. **Meaningful colors**: Colors should convey information, not just decoration
3. **Accessibility**: Provide alternative indicators for color information
4. **Performance**: Cache color strings for frequently used colors

### Testing Colors
```bash
# Test color output
python src/cli.py --test-colors

# Test in different terminals
python src/cli.py --monitor --no-color  # Disable colors
python src/cli.py --monitor --high-contrast  # High contrast mode
```

### Color Validation
```python
def validate_color_output():
    """Test color output in current terminal."""
    test_colors = [
        (Colors.RED, "Red text"),
        (Colors.GREEN, "Green text"),
        (Colors.YELLOW, "Yellow text"),
        (Colors.BLUE, "Blue text"),
        (Colors.BRIGHT_RED + Colors.BOLD, "Bright red bold"),
        (Colors.CYAN + Colors.UNDERLINE, "Cyan underlined")
    ]
    
    print("Color test:")
    for color, text in test_colors:
        print(f"{color}{text}{Colors.RESET}")
```

This color specification ensures consistent, accessible, and informative visual output across all components of the UPS Monitor system.