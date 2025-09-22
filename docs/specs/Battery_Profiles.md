# Battery Profiles Specification

This document defines the battery profile system used by the UPS Monitor to accurately track battery charge levels and estimate runtime for different battery types and configurations.

## Overview

Battery profiles provide voltage-to-percentage mapping curves that account for the non-linear discharge characteristics of different battery chemistries. Each profile includes discharge curves, safety parameters, and chemistry-specific properties.

## Profile Structure

### Basic Profile Format
```yaml
profile_name:
  chemistry: "string"           # Battery chemistry type
  nominal_voltage: float        # Nominal voltage per cell
  full_voltage: float          # Full charge voltage per cell
  empty_voltage: float         # Empty/cutoff voltage per cell
  capacity_mah: int            # Typical capacity in mAh
  series_cells: int            # Number of cells in series
  parallel_groups: int         # Number of parallel groups
  voltage_curve:               # Voltage curve mapping
    percentage: voltage        # % charge to voltage mapping
  discharge_curve:             # Discharge rate characteristics
    current_ma: capacity_factor # Current to capacity factor
  temperature_coefficients:    # Temperature compensation
    coefficient: float         # Voltage coefficient per °C
    reference_temp: float      # Reference temperature
  safety_limits:              # Safety parameters
    max_voltage: float         # Maximum safe voltage
    min_voltage: float         # Minimum safe voltage
    max_current: float         # Maximum discharge current
    max_temperature: float     # Maximum operating temperature
```

## Standard Battery Profiles

### 18650 Lithium-Ion (Most Common)
```yaml
18650_standard:
  chemistry: "Li-ion"
  nominal_voltage: 3.7
  full_voltage: 4.2
  empty_voltage: 2.5
  capacity_mah: 2500
  series_cells: 1
  parallel_groups: 1
  
  voltage_curve:
    100: 4.20    # Full charge
    95:  4.15    # Near full
    90:  4.10    # High charge
    85:  4.05
    80:  4.00
    75:  3.95
    70:  3.90
    65:  3.85
    60:  3.80
    55:  3.78
    50:  3.75    # Nominal voltage region
    45:  3.73
    40:  3.70
    35:  3.68
    30:  3.65
    25:  3.62
    20:  3.60
    15:  3.58
    10:  3.55
    5:   3.50    # Low battery warning
    0:   2.50    # Protection circuit cutoff
    
  discharge_curve:
    # Current (mA) to capacity factor
    250:  1.00   # C/10 discharge rate
    500:  0.98   # C/5 discharge rate
    1000: 0.95   # C/2.5 discharge rate
    2000: 0.90   # C/1.25 discharge rate
    2500: 0.85   # 1C discharge rate
    
  temperature_coefficients:
    coefficient: -0.003  # -3mV per °C
    reference_temp: 25.0 # 25°C reference
    
  safety_limits:
    max_voltage: 4.25
    min_voltage: 2.0
    max_current: 10000   # 10A maximum
    max_temperature: 60.0
```

### 18650 High Capacity
```yaml
18650_high_capacity:
  chemistry: "Li-ion"
  nominal_voltage: 3.7
  full_voltage: 4.2
  empty_voltage: 2.5
  capacity_mah: 3500
  series_cells: 1
  parallel_groups: 1
  
  # Similar voltage curve but optimized for high capacity cells
  voltage_curve:
    100: 4.20
    90:  4.08    # Slightly different curve
    80:  3.98
    70:  3.88
    60:  3.78
    50:  3.73    # More stable voltage plateau
    40:  3.68
    30:  3.63
    20:  3.58
    10:  3.53
    5:   3.48
    0:   2.50
    
  discharge_curve:
    350:  1.00   # Lower optimal discharge rate
    700:  0.98
    1400: 0.95
    2800: 0.88
    3500: 0.82   # 1C rate
    
  temperature_coefficients:
    coefficient: -0.003
    reference_temp: 25.0
    
  safety_limits:
    max_voltage: 4.25
    min_voltage: 2.0
    max_current: 15000   # Higher current capability
    max_temperature: 60.0
```

### 21700 Lithium-Ion
```yaml
21700_standard:
  chemistry: "Li-ion"
  nominal_voltage: 3.7
  full_voltage: 4.2
  empty_voltage: 2.5
  capacity_mah: 4000
  series_cells: 1
  parallel_groups: 1
  
  voltage_curve:
    100: 4.20
    90:  4.10
    80:  3.98
    70:  3.86
    60:  3.76
    50:  3.71    # Extended voltage plateau
    40:  3.66
    30:  3.61
    20:  3.56
    10:  3.51
    5:   3.46
    0:   2.50
    
  discharge_curve:
    400:  1.00   # C/10
    800:  0.98   # C/5
    1600: 0.96   # C/2.5
    3200: 0.91   # C/1.25
    4000: 0.86   # 1C
    
  temperature_coefficients:
    coefficient: -0.003
    reference_temp: 25.0
    
  safety_limits:
    max_voltage: 4.25
    min_voltage: 2.0
    max_current: 20000   # 20A maximum
    max_temperature: 60.0
```

## Multi-Cell Configurations

### Dual 18650 Parallel
```yaml
dual_18650_parallel:
  chemistry: "Li-ion"
  nominal_voltage: 3.7
  full_voltage: 4.2
  empty_voltage: 2.5
  capacity_mah: 5000      # 2x 2500mAh
  series_cells: 1
  parallel_groups: 2
  
  # Same voltage curve as single cell
  voltage_curve:
    # ... same as 18650_standard
    
  discharge_curve:
    500:  1.00   # Higher current capability
    1000: 0.99
    2000: 0.97
    4000: 0.93
    5000: 0.88   # 1C total rate
    
  temperature_coefficients:
    coefficient: -0.003
    reference_temp: 25.0
    
  safety_limits:
    max_voltage: 4.25
    min_voltage: 2.0
    max_current: 20000   # Higher total current
    max_temperature: 60.0
```

### Dual 18650 Series (7.4V System)
```yaml
dual_18650_series:
  chemistry: "Li-ion"
  nominal_voltage: 7.4     # 2x 3.7V
  full_voltage: 8.4        # 2x 4.2V
  empty_voltage: 5.0       # 2x 2.5V
  capacity_mah: 2500
  series_cells: 2
  parallel_groups: 1
  
  voltage_curve:
    100: 8.40    # 2x 4.20V
    90:  8.20    # 2x 4.10V
    80:  8.00    # 2x 4.00V
    70:  7.80    # 2x 3.90V
    60:  7.60    # 2x 3.80V
    50:  7.50    # 2x 3.75V
    40:  7.40    # 2x 3.70V
    30:  7.30    # 2x 3.65V
    20:  7.20    # 2x 3.60V
    10:  7.10    # 2x 3.55V
    5:   7.00    # 2x 3.50V
    0:   5.00    # 2x 2.50V
    
  discharge_curve:
    250:  1.00
    500:  0.98
    1000: 0.95
    2000: 0.90
    2500: 0.85
    
  temperature_coefficients:
    coefficient: -0.006  # 2x single cell coefficient
    reference_temp: 25.0
    
  safety_limits:
    max_voltage: 8.50    # 2x 4.25V
    min_voltage: 4.0     # 2x 2.0V
    max_current: 10000
    max_temperature: 60.0
```

## Advanced Profile Features

### Aging Compensation
```yaml
aging_factors:
  cycle_count_threshold: 100   # Cycles before applying aging
  capacity_fade_per_100_cycles: 0.02  # 2% capacity loss per 100 cycles
  voltage_sag_compensation: 0.01      # Additional voltage sag compensation
  max_aging_cycles: 1000              # Maximum tracked cycles
```

### Load-Dependent Curves
```yaml
load_dependent_curves:
  low_load:    # < 0.5A
    efficiency_factor: 1.05
    voltage_boost: 0.02
  medium_load: # 0.5-1.5A
    efficiency_factor: 1.00
    voltage_boost: 0.00
  high_load:   # > 1.5A
    efficiency_factor: 0.95
    voltage_boost: -0.03
```

### Runtime Estimation Parameters
```yaml
runtime_parameters:
  peukert_exponent: 1.1        # Peukert's law exponent
  efficiency_factor: 0.95      # System efficiency
  cutoff_margin: 0.1          # Safety margin (10% before cutoff)
  temperature_derating:        # Capacity derating by temperature
    0:   0.80   # 80% capacity at 0°C
    10:  0.90   # 90% capacity at 10°C
    25:  1.00   # 100% capacity at 25°C
    40:  0.95   # 95% capacity at 40°C
    60:  0.85   # 85% capacity at 60°C
```

## Profile Selection Logic

### Automatic Detection
```python
def detect_battery_profile(voltage_reading, current_reading):
    """Automatically detect battery profile based on readings."""
    # Check voltage range to determine cell count
    if 3.0 <= voltage_reading <= 4.3:
        cell_count = 1
    elif 6.0 <= voltage_reading <= 8.6:
        cell_count = 2
    else:
        return None
        
    # Estimate capacity based on discharge characteristics
    # ... additional logic
    
    return suggested_profile
```

### Manual Selection
```yaml
# config/hardware_calibration.yaml
battery_configuration:
  profile: "18650_standard"
  override_capacity: 2800      # Override if known capacity differs
  custom_name: "Panasonic NCR18650B"
  calibration_date: "2025-01-15"
```

## Calibration Integration

### Profile Customization
Profiles can be customized through calibration:

```yaml
custom_calibrated_profile:
  base_profile: "18650_standard"
  calibration_adjustments:
    voltage_offset: 0.05       # Add 50mV to all readings
    capacity_factor: 0.92      # 92% of rated capacity measured
    custom_points:             # Override specific points
      50: 3.78                 # 50% = 3.78V (measured)
      25: 3.64                 # 25% = 3.64V (measured)
```

### Validation
```python
def validate_profile(profile_data):
    """Validate battery profile data."""
    required_fields = [
        'chemistry', 'nominal_voltage', 'full_voltage', 
        'empty_voltage', 'capacity_mah', 'voltage_curve'
    ]
    
    for field in required_fields:
        if field not in profile_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate voltage curve is monotonic
    voltages = list(profile_data['voltage_curve'].values())
    if not all(v1 >= v2 for v1, v2 in zip(voltages, voltages[1:])):
        raise ValueError("Voltage curve must be monotonically decreasing")
    
    return True
```

## Usage Examples

### Loading Profiles
```python
import yaml

def load_battery_profiles():
    """Load all battery profiles from configuration."""
    with open('config/battery_profiles.yaml', 'r') as f:
        profiles = yaml.safe_load(f)
    
    # Validate each profile
    for name, profile in profiles.items():
        validate_profile(profile)
    
    return profiles

def get_voltage_for_percentage(profile, percentage):
    """Get voltage for a given percentage using profile curve."""
    curve = profile['voltage_curve']
    
    # Find closest percentage points
    percentages = sorted(curve.keys(), reverse=True)
    
    if percentage in curve:
        return curve[percentage]
    
    # Interpolate between points
    for i, p in enumerate(percentages[:-1]):
        if percentages[i+1] <= percentage <= p:
            # Linear interpolation
            x1, y1 = percentages[i+1], curve[percentages[i+1]]
            x2, y2 = p, curve[p]
            
            return y1 + (y2 - y1) * (percentage - x1) / (x2 - x1)
    
    return profile['empty_voltage']  # Fallback
```

This battery profiles specification provides the foundation for accurate battery monitoring across different battery types and configurations in the UPS Monitor system.