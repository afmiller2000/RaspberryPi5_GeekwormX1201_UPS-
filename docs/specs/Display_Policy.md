# LED Display Policy Specification

This document defines the rules and policies governing LED display behavior in the UPS Monitor system.

## Overview

The LED display system provides visual feedback about battery status, power conditions, and system health through a combination of hardware LEDs on the UPS HAT and software-rendered LED indicators in the terminal interface.

## LED Hardware Configuration

### Standard 4-LED Configuration
Most Geekworm X1201 UPS HATs include 4 LEDs for battery level indication:

- **LED4**: Highest level indicator (76-100%)
- **LED3**: High level indicator (51-75%)
- **LED2**: Medium level indicator (26-50%)
- **LED1**: Low level indicator (5-25%)

### LED States
Each LED can be in one of the following states:
- **OFF**: LED is not illuminated
- **ON**: LED is continuously illuminated
- **BLINK_SLOW**: LED blinks slowly (1 Hz)
- **BLINK_FAST**: LED blinks rapidly (4 Hz)
- **PULSE**: LED pulses smoothly (breathing effect)

## Display Policies

### Battery Level Display Policy

#### Standard Display Mode
```python
def get_battery_led_pattern(battery_percentage):
    """
    Determine LED pattern based on battery percentage.
    
    Returns:
        Dictionary with LED states for each LED
    """
    if battery_percentage >= 76:
        return {
            'LED4': 'ON',     # Green - Full
            'LED3': 'ON',     # Green - High
            'LED2': 'ON',     # Green - Medium
            'LED1': 'ON'      # Green - Low
        }
    elif battery_percentage >= 51:
        return {
            'LED4': 'OFF',    # Off
            'LED3': 'ON',     # Green - High
            'LED2': 'ON',     # Green - Medium
            'LED1': 'ON'      # Green - Low
        }
    elif battery_percentage >= 26:
        return {
            'LED4': 'OFF',    # Off
            'LED3': 'OFF',    # Off
            'LED2': 'ON',     # Yellow - Medium
            'LED1': 'ON'      # Yellow - Low
        }
    elif battery_percentage >= 5:
        return {
            'LED4': 'OFF',    # Off
            'LED3': 'OFF',    # Off
            'LED2': 'OFF',    # Off
            'LED1': 'ON'      # Red - Critical warning
        }
    else:  # < 5%
        return {
            'LED4': 'OFF',    # Off
            'LED3': 'OFF',    # Off
            'LED2': 'OFF',    # Off
            'LED1': 'BLINK_FAST'  # Red blinking - Emergency
        }
```

#### Enhanced Display Mode (with charging indication)
```python
def get_enhanced_led_pattern(battery_percentage, power_status, charging_status):
    """
    Enhanced LED pattern including power and charging status.
    """
    base_pattern = get_battery_led_pattern(battery_percentage)
    
    # Modify pattern based on charging status
    if charging_status == 'CHARGING':
        # Add pulsing effect to active LEDs
        for led, state in base_pattern.items():
            if state == 'ON':
                base_pattern[led] = 'PULSE'
    
    elif power_status == 'AC_POWER' and charging_status == 'FULL':
        # All LEDs on solid when on AC power and battery full
        base_pattern = {led: 'ON' for led in base_pattern.keys()}
    
    elif power_status == 'BATTERY_POWER':
        # Indicate running on battery power
        # Keep base pattern but add slow blink to highest active LED
        active_leds = [led for led, state in base_pattern.items() if state == 'ON']
        if active_leds:
            highest_led = max(active_leds, key=lambda x: int(x.replace('LED', '')))
            base_pattern[highest_led] = 'BLINK_SLOW'
    
    return base_pattern
```

### Color Policies

#### LED Color Mapping
```python
LED_COLORS = {
    'battery_level': {
        76: 'GREEN',      # Excellent battery level
        51: 'GREEN',      # Good battery level
        26: 'YELLOW',     # Moderate battery level
        5:  'RED',        # Low battery warning
        0:  'RED'         # Critical battery warning
    },
    'power_status': {
        'AC_POWER': 'BLUE',         # On external power
        'BATTERY_POWER': 'ORANGE',  # Running on battery
        'CHARGING': 'CYAN',         # Battery charging
        'FAULT': 'RED'              # System fault
    },
    'system_status': {
        'NORMAL': 'GREEN',
        'WARNING': 'YELLOW',
        'ERROR': 'RED',
        'MAINTENANCE': 'PURPLE'
    }
}
```

### Terminal Display Policies

#### Software LED Representation
```python
def render_terminal_leds(led_pattern, color_mapping):
    """
    Render LED pattern in terminal using ANSI colors and symbols.
    """
    led_symbols = {
        'ON': '●',           # Filled circle
        'OFF': '○',          # Empty circle
        'BLINK_SLOW': '◐',   # Half-filled circle
        'BLINK_FAST': '◑',   # Quarter-filled circle
        'PULSE': '◒'         # Three-quarter circle
    }
    
    output_lines = []
    
    # Display LEDs in reverse order (LED4 at top)
    for led_num in range(4, 0, -1):
        led_key = f'LED{led_num}'
        state = led_pattern.get(led_key, 'OFF')
        symbol = led_symbols[state]
        
        # Get color based on LED position and state
        color = get_led_color(led_num, state, color_mapping)
        colored_symbol = apply_color(symbol, color)
        
        output_lines.append(f"{led_key}: {colored_symbol}")
    
    return '\n'.join(output_lines)
```

#### Percentage Bar Display
```python
def render_percentage_bar(percentage, width=20):
    """
    Render horizontal percentage bar with LED-like segments.
    """
    filled_width = int((percentage / 100) * width)
    
    # Create segments with different colors
    segments = []
    for i in range(width):
        if i < filled_width:
            if percentage >= 75:
                segments.append(apply_color('█', 'GREEN'))
            elif percentage >= 50:
                segments.append(apply_color('█', 'YELLOW'))
            elif percentage >= 25:
                segments.append(apply_color('█', 'ORANGE'))
            else:
                segments.append(apply_color('█', 'RED'))
        else:
            segments.append(apply_color('░', 'DIM'))
    
    return f"[{''.join(segments)}] {percentage}%"
```

## Display Timing Policies

### Blink Timing
```python
BLINK_TIMINGS = {
    'BLINK_SLOW': {
        'on_duration': 1.0,   # 1 second on
        'off_duration': 1.0,  # 1 second off
        'frequency': 0.5      # 0.5 Hz
    },
    'BLINK_FAST': {
        'on_duration': 0.125, # 125ms on
        'off_duration': 0.125, # 125ms off
        'frequency': 4.0      # 4 Hz
    },
    'PULSE': {
        'period': 2.0,        # 2 second period
        'duty_cycle': 0.5,    # 50% duty cycle
        'smoothing': True     # Smooth transitions
    }
}
```

### Update Frequency
```python
DISPLAY_UPDATE_RATES = {
    'battery_monitoring': 5.0,    # Update every 5 seconds
    'charging_status': 2.0,       # Update every 2 seconds
    'critical_alerts': 0.5,       # Update every 500ms
    'system_status': 10.0,        # Update every 10 seconds
    'led_refresh': 0.1            # LED refresh rate (100ms)
}
```

## Priority Policies

### Display Priority Hierarchy
1. **CRITICAL ALERTS** (Highest priority)
   - Battery critically low (<5%)
   - System fault conditions
   - Hardware failures

2. **WARNING STATES** (High priority)
   - Low battery (5-15%)
   - High temperature
   - Charging errors

3. **NORMAL OPERATION** (Medium priority)
   - Battery level indication
   - Charging status
   - Power source indication

4. **INFORMATIONAL** (Low priority)
   - System health indicators
   - Runtime estimates
   - Statistics display

### Override Policies
```python
def apply_priority_override(current_pattern, alerts):
    """
    Apply priority-based overrides to LED pattern.
    """
    # Critical battery override
    if any(alert['level'] == 'CRITICAL' and alert['type'] == 'BATTERY' 
           for alert in alerts):
        return {
            'LED4': 'BLINK_FAST',
            'LED3': 'BLINK_FAST', 
            'LED2': 'BLINK_FAST',
            'LED1': 'BLINK_FAST'
        }
    
    # System fault override
    if any(alert['level'] == 'CRITICAL' and alert['type'] == 'SYSTEM' 
           for alert in alerts):
        return {
            'LED4': 'ON',
            'LED3': 'OFF',
            'LED2': 'ON', 
            'LED1': 'OFF'
        }  # Alternating pattern for system fault
    
    # High temperature warning
    if any(alert['level'] == 'WARNING' and alert['type'] == 'TEMPERATURE' 
           for alert in alerts):
        # Add slow blink to all active LEDs
        for led, state in current_pattern.items():
            if state == 'ON':
                current_pattern[led] = 'BLINK_SLOW'
    
    return current_pattern
```

## Accessibility Policies

### Color-Blind Support
```python
def apply_colorblind_friendly_display(led_pattern, colorblind_type):
    """
    Modify display for colorblind accessibility.
    """
    if colorblind_type == 'red_green':
        # Use symbols instead of just colors
        symbol_mapping = {
            'CRITICAL': '⚠',    # Warning symbol
            'LOW': '▼',         # Down arrow
            'NORMAL': '●',      # Circle
            'GOOD': '✓'         # Check mark
        }
        
        # Add symbols to display
        for led, state in led_pattern.items():
            # Add appropriate symbol based on battery level
            pass  # Implementation details
    
    elif colorblind_type == 'blue_yellow':
        # Use high contrast colors
        pass  # Implementation details
    
    return led_pattern
```

### High Contrast Mode
```python
def apply_high_contrast_mode(display_elements):
    """
    Apply high contrast colors for better visibility.
    """
    high_contrast_colors = {
        'background': 'BLACK',
        'critical': 'BRIGHT_WHITE_ON_RED',
        'warning': 'BLACK_ON_YELLOW',
        'normal': 'WHITE_ON_BLACK',
        'good': 'BLACK_ON_GREEN'
    }
    
    # Apply high contrast colors
    for element in display_elements:
        element['color'] = high_contrast_colors.get(
            element['level'], 
            high_contrast_colors['normal']
        )
    
    return display_elements
```

## Configuration Policies

### User Customization
```yaml
# config/display_policy.yaml
led_display:
  mode: "enhanced"          # standard, enhanced, minimal
  brightness: 80            # 0-100%
  color_theme: "default"    # default, high_contrast, colorblind_friendly
  blink_speed: "normal"     # slow, normal, fast
  
battery_display:
  thresholds:
    critical: 5             # Critical threshold (%)
    low: 25                 # Low threshold (%)
    medium: 50              # Medium threshold (%)
    high: 75                # High threshold (%)
  
  colors:
    critical: "red"
    low: "orange" 
    medium: "yellow"
    high: "green"
    
power_display:
  show_charging_animation: true
  show_ac_indicator: true
  show_runtime_estimate: true
  
accessibility:
  colorblind_support: false
  high_contrast: false
  use_symbols: true
  audio_alerts: false
```

### Runtime Configuration
```python
class DisplayPolicyManager:
    def __init__(self, config_file='config/display_policy.yaml'):
        self.config = self.load_config(config_file)
        self.current_mode = self.config['led_display']['mode']
        
    def update_policy(self, policy_changes):
        """Update display policy at runtime."""
        self.config.update(policy_changes)
        self.apply_policy_changes()
        
    def get_led_pattern(self, battery_data, system_status):
        """Get LED pattern based on current policy."""
        if self.current_mode == 'standard':
            return self.get_standard_pattern(battery_data)
        elif self.current_mode == 'enhanced':
            return self.get_enhanced_pattern(battery_data, system_status)
        elif self.current_mode == 'minimal':
            return self.get_minimal_pattern(battery_data)
```

## Error Handling Policies

### Display Fallback
```python
def get_fallback_display():
    """
    Provide fallback display when normal display fails.
    """
    return {
        'LED4': 'BLINK_SLOW',
        'LED3': 'OFF',
        'LED2': 'BLINK_SLOW', 
        'LED1': 'OFF'
    }  # Alternating blink pattern indicates error state

def handle_display_error(error_type, error_details):
    """
    Handle display system errors with appropriate fallback.
    """
    if error_type == 'i2c_communication':
        # Use software-only display
        return get_software_display_only()
    
    elif error_type == 'led_hardware_failure':
        # Use terminal display with error indication
        return get_terminal_display_with_error()
    
    else:
        # Generic fallback
        return get_fallback_display()
```

This display policy specification ensures consistent, accessible, and informative visual feedback across all components of the UPS Monitor system.