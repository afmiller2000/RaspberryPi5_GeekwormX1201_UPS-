# Battery Calibration Guide

Accurate battery monitoring requires proper calibration for your specific battery type and configuration. This guide walks you through the calibration process.

## Overview

The UPS monitor uses voltage-to-percentage mapping to estimate battery charge levels. Different battery chemistries and capacities have different voltage curves, so calibration is essential for accurate readings.

## When to Calibrate

- **First installation** - Always calibrate new setups
- **Battery replacement** - When changing battery type or capacity
- **Inaccurate readings** - If percentage doesn't match actual runtime
- **Periodic maintenance** - Every 6 months for optimal accuracy

## Battery Types Supported

### 18650 Lithium-Ion (Most Common)
- **Nominal Voltage:** 3.7V
- **Full Charge:** 4.2V
- **Empty:** 2.5V (protection circuit cutoff)
- **Capacity:** 2500-3500mAh typical

### 21700 Lithium-Ion (High Capacity)
- **Nominal Voltage:** 3.7V
- **Full Charge:** 4.2V
- **Empty:** 2.5V
- **Capacity:** 4000-5000mAh typical

## Calibration Methods

### Method 1: Guided Calibration (Recommended)

This method uses the built-in calibration routine:

```bash
# Start guided calibration
python src/cli.py --calibrate

# Follow the interactive prompts:
# 1. Ensure battery is fully charged (4.2V per cell)
# 2. Begin discharge monitoring
# 3. System will track voltage curve during use
# 4. Complete when battery reaches low voltage cutoff
```

The guided calibration will:
- Record voltage at 100%, 75%, 50%, 25%, and 10% discharge points
- Generate a custom voltage curve for your battery
- Save results to `config/hardware_calibration.yaml`

### Method 2: Manual Configuration

For advanced users who understand their battery specifications:

1. **Edit battery profile:**
```bash
nano config/battery_profiles.yaml
```

2. **Add custom profile:**
```yaml
custom_18650:
  chemistry: "Li-ion"
  nominal_voltage: 3.7
  full_voltage: 4.2
  empty_voltage: 2.5
  capacity_mah: 3000
  voltage_curve:
    100: 4.20
    90:  4.10
    80:  4.00
    70:  3.90
    60:  3.80
    50:  3.75
    40:  3.70
    30:  3.65
    20:  3.60
    10:  3.55
    5:   3.50
    0:   2.50
```

3. **Update configuration:**
```bash
nano config/hardware_calibration.yaml
```

```yaml
battery:
  profile: "custom_18650"
  bank_count: 1  # or 2 for dual battery setup
  calibration_date: "2025-01-15"
  calibrated_by: "user"
```

## Calibration Process

### Preparation

1. **Full Charge:** Ensure batteries are fully charged (4.2V per cell)
2. **Stable Environment:** Perform calibration at room temperature
3. **Normal Load:** Use typical system load during calibration
4. **Time Allocation:** Allow 4-8 hours for complete discharge cycle

### Step-by-Step Process

#### Step 1: Start Calibration Mode
```bash
python src/cli.py --calibrate --profile new_battery
```

#### Step 2: Record Full Charge Point
```
Battery Status: CHARGING → FULL
Voltage: 4.20V (per cell)
Percentage: 100%
Action: Press Enter to confirm full charge point
```

#### Step 3: Monitor Discharge
The calibration will automatically:
- Record voltage readings every minute
- Track time-based discharge rates
- Identify key percentage points (75%, 50%, 25%, 10%)
- Calculate average load consumption

#### Step 4: Low Battery Cutoff
```
Battery Status: LOW BATTERY WARNING
Voltage: 3.20V (per cell)
Percentage: 10%
Action: System will safely shutdown when reaching cutoff
```

#### Step 5: Calibration Complete
```
Calibration Complete!
Data points collected: 240
Discharge time: 6.2 hours
Average load: 0.85A
Calibration saved to: config/hardware_calibration.yaml
```

## Dual Battery Configuration

For systems with two 18650 batteries:

### Parallel Configuration (Most Common)
- **Voltage:** Same as single battery (3.7V nominal)
- **Capacity:** Double (2x capacity)
- **Calibration:** Use single battery profile, adjust capacity

```yaml
battery:
  profile: "18650_parallel"
  bank_count: 2
  configuration: "parallel"
  total_capacity_mah: 6000  # 2x 3000mAh batteries
```

### Series Configuration (Rare)
- **Voltage:** Double (7.4V nominal)
- **Capacity:** Same as single battery
- **Calibration:** Requires special series profile

## Verification

After calibration, verify accuracy:

### Runtime Test
```bash
# Monitor during known discharge time
python src/cli.py --monitor --log-runtime

# Compare estimated vs actual runtime
# Should be within 10% accuracy
```

### Voltage Verification
```bash
# Check voltage readings against multimeter
python src/cli.py --voltage-test

# Readings should be within 0.05V of actual
```

## Troubleshooting Calibration

### Common Issues

1. **Calibration Won't Start**
   - Battery not fully charged
   - I2C communication error
   - Previous calibration file locked

2. **Inaccurate Results**
   - Battery degraded/old
   - Temperature effects
   - Inconsistent load during calibration

3. **Calibration Interrupted**
   - Power loss during process
   - I2C errors
   - System reboot

### Solutions

```bash
# Reset calibration data
python src/cli.py --reset-calibration

# Force recalibration
python src/cli.py --calibrate --force

# Manual voltage curve entry
python src/cli.py --manual-curve
```

## Advanced Topics

### Temperature Compensation

Battery voltage varies with temperature:
- **Cold:** Higher voltage readings
- **Hot:** Lower voltage readings
- **Compensation:** ±0.003V per °C from 25°C reference

```yaml
temperature_compensation:
  enabled: true
  reference_temp: 25.0  # Celsius
  coefficient: -0.003   # V/°C
```

### Battery Aging

Batteries lose capacity over time:
- **Cycle count tracking**
- **Capacity fade modeling**
- **Automatic recalibration suggestions**

### Load-Based Estimation

More accurate estimation using load patterns:
- **Peukert effect correction**
- **Load history analysis**
- **Dynamic runtime calculation**

## Maintenance Schedule

### Weekly
- Check battery voltage trends
- Review capacity estimates

### Monthly
- Verify percentage accuracy
- Check temperature readings

### Quarterly
- Full discharge/recharge cycle
- Update calibration if needed

### Annually
- Complete recalibration
- Battery health assessment
- Consider battery replacement

## Safety Considerations

⚠️ **Warning:** Always follow safety protocols:

- Never calibrate damaged batteries
- Monitor temperature during discharge
- Use protection circuits
- Maintain ventilation during calibration
- Stop calibration if voltage drops too quickly

## Example Calibration Data

Successful calibration output:
```
Calibration Results for 18650 Li-ion Battery
===========================================
Total Discharge Time: 6.2 hours
Average Load: 0.85A
Capacity: 2850mAh (measured)

Voltage Curve Points:
100%: 4.20V  |  50%: 3.75V
 90%: 4.10V  |  40%: 3.70V
 80%: 4.00V  |  30%: 3.65V
 70%: 3.90V  |  20%: 3.60V
 60%: 3.80V  |  10%: 3.55V

Calibration Quality: EXCELLENT
Estimated Accuracy: ±5%
Next Calibration Due: 2025-07-15
```