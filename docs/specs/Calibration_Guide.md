# Technical Calibration Specifications

This document provides the technical specifications and implementation details for the UPS Monitor calibration system.

## Calibration System Architecture

### Components
1. **Calibration Engine**: Core calibration logic and algorithms
2. **Data Collection**: Sensor reading collection and validation
3. **Curve Fitting**: Mathematical curve fitting algorithms
4. **Profile Management**: Battery profile creation and updates
5. **Validation System**: Calibration quality assessment

### Data Flow
```
Sensor Readings → Data Validation → Curve Fitting → Profile Generation → Validation → Storage
```

## Calibration Algorithms

### Voltage Curve Fitting

#### Linear Interpolation Method
```python
def linear_interpolation_curve(data_points):
    """
    Create voltage curve using linear interpolation between measured points.
    
    Args:
        data_points: List of (percentage, voltage) tuples
    
    Returns:
        Dictionary mapping percentage to voltage
    """
    sorted_points = sorted(data_points, key=lambda x: x[0], reverse=True)
    curve = {}
    
    for i in range(101):  # 0-100%
        percentage = 100 - i
        
        # Find surrounding points
        for j, (p, v) in enumerate(sorted_points[:-1]):
            if sorted_points[j+1][0] <= percentage <= p:
                # Linear interpolation
                p1, v1 = sorted_points[j+1]
                p2, v2 = p, v
                
                voltage = v1 + (v2 - v1) * (percentage - p1) / (p2 - p1)
                curve[percentage] = round(voltage, 3)
                break
        else:
            # Outside measured range
            if percentage > sorted_points[0][0]:
                curve[percentage] = sorted_points[0][1]
            else:
                curve[percentage] = sorted_points[-1][1]
    
    return curve
```

#### Polynomial Curve Fitting
```python
import numpy as np

def polynomial_curve_fitting(data_points, degree=3):
    """
    Fit polynomial curve to calibration data points.
    
    Args:
        data_points: List of (percentage, voltage) tuples
        degree: Polynomial degree (default: 3)
    
    Returns:
        Polynomial coefficients and fitted curve
    """
    percentages = np.array([p[0] for p in data_points])
    voltages = np.array([p[1] for p in data_points])
    
    # Fit polynomial
    coefficients = np.polyfit(percentages, voltages, degree)
    poly_func = np.poly1d(coefficients)
    
    # Generate smooth curve
    curve = {}
    for i in range(101):
        percentage = 100 - i
        voltage = float(poly_func(percentage))
        curve[percentage] = round(max(0, voltage), 3)  # Ensure non-negative
    
    return coefficients, curve
```

#### Exponential Decay Model
```python
import numpy as np
from scipy.optimize import curve_fit

def exponential_decay_model(percentage, a, b, c, d):
    """
    Exponential decay model for lithium battery discharge curve.
    
    V(p) = a * exp(-b * (100-p)) + c * (100-p) + d
    
    Where:
        p = percentage (0-100)
        a, b, c, d = fitting parameters
    """
    return a * np.exp(-b * (100 - percentage)) + c * (100 - percentage) + d

def fit_exponential_curve(data_points):
    """Fit exponential decay model to calibration data."""
    percentages = np.array([p[0] for p in data_points])
    voltages = np.array([p[1] for p in data_points])
    
    # Initial parameter guess
    initial_guess = [0.5, 0.01, -0.01, 3.5]
    
    try:
        # Fit curve
        popt, pcov = curve_fit(
            exponential_decay_model, 
            percentages, 
            voltages, 
            p0=initial_guess,
            maxfev=5000
        )
        
        # Generate curve
        curve = {}
        for i in range(101):
            percentage = 100 - i
            voltage = exponential_decay_model(percentage, *popt)
            curve[percentage] = round(max(0, voltage), 3)
        
        # Calculate R-squared
        y_pred = exponential_decay_model(percentages, *popt)
        ss_res = np.sum((voltages - y_pred) ** 2)
        ss_tot = np.sum((voltages - np.mean(voltages)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        return popt, curve, r_squared
        
    except Exception as e:
        print(f"Curve fitting failed: {e}")
        return None, {}, 0.0
```

## Calibration Data Collection

### Sampling Strategy

#### Time-Based Sampling
```python
import time
from datetime import datetime, timedelta

class CalibrationDataCollector:
    def __init__(self, sampling_interval=60):  # 1 minute default
        self.sampling_interval = sampling_interval
        self.data_points = []
        self.start_time = None
        self.last_sample_time = 0
        
    def start_collection(self):
        """Start calibration data collection."""
        self.start_time = datetime.now()
        self.data_points = []
        print(f"Calibration started at {self.start_time}")
        
    def collect_sample(self, sensor_data):
        """Collect a calibration sample."""
        current_time = time.time()
        
        if current_time - self.last_sample_time >= self.sampling_interval:
            sample = {
                'timestamp': datetime.now(),
                'voltage': sensor_data['battery_voltage'],
                'current': sensor_data['battery_current'],
                'temperature': sensor_data['temperature'],
                'elapsed_time': current_time - time.mktime(self.start_time.timetuple())
            }
            
            self.data_points.append(sample)
            self.last_sample_time = current_time
            
            return sample
        
        return None
```

#### Percentage-Based Sampling
```python
def percentage_based_sampling(collector, target_percentages):
    """
    Collect samples at specific percentage points.
    
    Args:
        collector: CalibrationDataCollector instance
        target_percentages: List of percentages to sample at
    """
    collected_percentages = set()
    
    while len(collected_percentages) < len(target_percentages):
        sample = collector.collect_sample()
        if sample:
            # Estimate current percentage (rough estimate)
            estimated_percentage = estimate_percentage_from_voltage(
                sample['voltage']
            )
            
            # Find closest target percentage
            closest_target = min(
                target_percentages,
                key=lambda x: abs(x - estimated_percentage)
            )
            
            # If close enough and not already collected
            if (abs(closest_target - estimated_percentage) < 2.5 and 
                closest_target not in collected_percentages):
                
                sample['target_percentage'] = closest_target
                sample['estimated_percentage'] = estimated_percentage
                collected_percentages.add(closest_target)
                
                print(f"Collected sample at {closest_target}%: {sample['voltage']:.3f}V")
        
        time.sleep(30)  # Wait 30 seconds between checks
```

### Data Validation

#### Outlier Detection
```python
import numpy as np

def detect_outliers(data_points, method='iqr'):
    """
    Detect and remove outliers from calibration data.
    
    Args:
        data_points: List of voltage measurements
        method: 'iqr' or 'zscore'
    
    Returns:
        Filtered data points
    """
    voltages = np.array([p['voltage'] for p in data_points])
    
    if method == 'iqr':
        Q1 = np.percentile(voltages, 25)
        Q3 = np.percentile(voltages, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        mask = (voltages >= lower_bound) & (voltages <= upper_bound)
        
    elif method == 'zscore':
        z_scores = np.abs((voltages - np.mean(voltages)) / np.std(voltages))
        mask = z_scores < 3  # 3 standard deviations
    
    return [dp for i, dp in enumerate(data_points) if mask[i]]
```

#### Monotonicity Check
```python
def validate_monotonicity(voltage_curve, tolerance=0.005):
    """
    Validate that voltage curve is monotonically decreasing.
    
    Args:
        voltage_curve: Dictionary mapping percentage to voltage
        tolerance: Allowed tolerance for monotonicity violations
    
    Returns:
        (is_valid, violations)
    """
    percentages = sorted(voltage_curve.keys(), reverse=True)
    violations = []
    
    for i in range(len(percentages) - 1):
        p1, p2 = percentages[i], percentages[i + 1]
        v1, v2 = voltage_curve[p1], voltage_curve[p2]
        
        # Voltage should decrease as percentage decreases
        if v1 < v2 - tolerance:
            violations.append({
                'percentage_high': p1,
                'percentage_low': p2,
                'voltage_high': v1,
                'voltage_low': v2,
                'violation': v2 - v1
            })
    
    return len(violations) == 0, violations
```

## Quality Metrics

### Calibration Quality Assessment
```python
def assess_calibration_quality(data_points, fitted_curve):
    """
    Assess the quality of calibration based on multiple metrics.
    
    Returns:
        Dictionary with quality metrics and overall grade
    """
    # Calculate R-squared
    actual_voltages = [dp['voltage'] for dp in data_points]
    predicted_voltages = [
        fitted_curve.get(dp['estimated_percentage'], 0) 
        for dp in data_points
    ]
    
    r_squared = calculate_r_squared(actual_voltages, predicted_voltages)
    
    # Calculate RMSE
    rmse = np.sqrt(np.mean([
        (actual - predicted) ** 2 
        for actual, predicted in zip(actual_voltages, predicted_voltages)
    ]))
    
    # Data point coverage
    percentages_covered = len(set(dp['estimated_percentage'] for dp in data_points))
    coverage_score = min(percentages_covered / 10.0, 1.0)  # Target 10+ points
    
    # Temperature stability
    temperatures = [dp['temperature'] for dp in data_points]
    temp_stability = 1.0 - (max(temperatures) - min(temperatures)) / 20.0
    temp_stability = max(0.0, temp_stability)
    
    # Overall quality score
    quality_score = (
        r_squared * 0.4 +           # R-squared weight: 40%
        (1 - rmse / 0.5) * 0.3 +    # RMSE weight: 30% (target < 0.5V)
        coverage_score * 0.2 +       # Coverage weight: 20%
        temp_stability * 0.1         # Temperature weight: 10%
    )
    
    # Quality grade
    if quality_score >= 0.9:
        grade = "EXCELLENT"
    elif quality_score >= 0.8:
        grade = "GOOD"
    elif quality_score >= 0.7:
        grade = "ACCEPTABLE"
    else:
        grade = "POOR"
    
    return {
        'r_squared': r_squared,
        'rmse': rmse,
        'coverage_score': coverage_score,
        'temperature_stability': temp_stability,
        'quality_score': quality_score,
        'grade': grade,
        'data_points': len(data_points),
        'temperature_range': max(temperatures) - min(temperatures)
    }
```

## Temperature Compensation

### Temperature Coefficient Calculation
```python
def calculate_temperature_coefficient(calibration_data):
    """
    Calculate temperature coefficient from calibration data.
    
    Returns:
        Temperature coefficient in V/°C
    """
    # Group data by similar percentages
    percentage_groups = {}
    
    for dp in calibration_data:
        percentage = round(dp['estimated_percentage'] / 5) * 5  # Group by 5%
        if percentage not in percentage_groups:
            percentage_groups[percentage] = []
        percentage_groups[percentage].append(dp)
    
    coefficients = []
    
    for percentage, group in percentage_groups.items():
        if len(group) < 3:  # Need at least 3 points
            continue
            
        temperatures = [dp['temperature'] for dp in group]
        voltages = [dp['voltage'] for dp in group]
        
        # Linear regression: voltage vs temperature
        coeff = np.polyfit(temperatures, voltages, 1)[0]  # Slope
        coefficients.append(coeff)
    
    # Average coefficient across all percentages
    if coefficients:
        avg_coefficient = np.mean(coefficients)
        return avg_coefficient
    
    return -0.003  # Default Li-ion coefficient
```

### Temperature Compensation Application
```python
def apply_temperature_compensation(voltage, temperature, profile):
    """
    Apply temperature compensation to voltage reading.
    
    Args:
        voltage: Raw voltage reading
        temperature: Current temperature in °C
        profile: Battery profile with temperature coefficients
    
    Returns:
        Temperature-compensated voltage
    """
    temp_coeff = profile.get('temperature_coefficients', {})
    coefficient = temp_coeff.get('coefficient', -0.003)
    reference_temp = temp_coeff.get('reference_temp', 25.0)
    
    # Compensation = coefficient * (temperature - reference)
    compensation = coefficient * (temperature - reference_temp)
    compensated_voltage = voltage - compensation
    
    return compensated_voltage
```

## Calibration Persistence

### Data Storage Format
```python
import json
from datetime import datetime

class CalibrationStorage:
    def save_calibration(self, profile_name, calibration_data, quality_metrics):
        """Save calibration results to persistent storage."""
        calibration_record = {
            'profile_name': profile_name,
            'calibration_date': datetime.now().isoformat(),
            'data_points': len(calibration_data['samples']),
            'quality_metrics': quality_metrics,
            'voltage_curve': calibration_data['fitted_curve'],
            'temperature_coefficient': calibration_data.get('temp_coefficient'),
            'battery_info': {
                'chemistry': calibration_data.get('chemistry', 'Li-ion'),
                'capacity_mah': calibration_data.get('capacity_mah'),
                'series_cells': calibration_data.get('series_cells', 1),
                'parallel_groups': calibration_data.get('parallel_groups', 1)
            },
            'calibration_parameters': {
                'method': calibration_data.get('method', 'polynomial'),
                'sampling_interval': calibration_data.get('sampling_interval', 60),
                'total_duration': calibration_data.get('duration_hours')
            }
        }
        
        filename = f"calibration_{profile_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"data/calibrations/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(calibration_record, f, indent=2)
        
        return filepath
```

### Profile Generation
```python
def generate_battery_profile(calibration_data, quality_metrics):
    """
    Generate battery profile from calibration data.
    
    Returns:
        Complete battery profile dictionary
    """
    profile = {
        'chemistry': calibration_data.get('chemistry', 'Li-ion'),
        'nominal_voltage': calibration_data.get('nominal_voltage', 3.7),
        'full_voltage': max(calibration_data['fitted_curve'].values()),
        'empty_voltage': min(calibration_data['fitted_curve'].values()),
        'capacity_mah': calibration_data.get('capacity_mah', 2500),
        'series_cells': calibration_data.get('series_cells', 1),
        'parallel_groups': calibration_data.get('parallel_groups', 1),
        
        'voltage_curve': calibration_data['fitted_curve'],
        
        'temperature_coefficients': {
            'coefficient': calibration_data.get('temp_coefficient', -0.003),
            'reference_temp': 25.0
        },
        
        'calibration_metadata': {
            'calibration_date': datetime.now().isoformat(),
            'quality_grade': quality_metrics['grade'],
            'r_squared': quality_metrics['r_squared'],
            'rmse': quality_metrics['rmse'],
            'data_points': quality_metrics['data_points']
        },
        
        'safety_limits': {
            'max_voltage': calibration_data['fitted_curve'][100] + 0.05,
            'min_voltage': calibration_data['fitted_curve'][0] - 0.2,
            'max_current': calibration_data.get('max_current', 10000),
            'max_temperature': 60.0
        }
    }
    
    return profile
```

This technical specification provides the foundation for implementing accurate and reliable battery calibration in the UPS Monitor system.