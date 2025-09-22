# Event Counters Specification

This document defines the event tracking and counting system for the UPS Monitor, including event types, counter mechanisms, persistence, and reporting.

## Overview

The Event Counters system provides comprehensive tracking of all significant events in the UPS Monitor system, enabling trend analysis, maintenance scheduling, and system health assessment.

## Event Categories

### Power Events
```python
POWER_EVENTS = {
    'AC_POWER_LOSS': {
        'description': 'AC power input lost',
        'severity': 'WARNING',
        'counter_type': 'increment',
        'triggers': ['backup_power_activation', 'battery_discharge_start']
    },
    'AC_POWER_RESTORED': {
        'description': 'AC power input restored',
        'severity': 'INFO',
        'counter_type': 'increment',
        'triggers': ['backup_power_deactivation', 'battery_charge_start']
    },
    'DC_OUTPUT_LOSS': {
        'description': 'DC output to load lost',
        'severity': 'CRITICAL',
        'counter_type': 'increment',
        'triggers': ['system_shutdown', 'load_disconnect']
    },
    'DC_OUTPUT_RESTORED': {
        'description': 'DC output to load restored',
        'severity': 'INFO',
        'counter_type': 'increment',
        'triggers': ['system_startup', 'load_reconnect']
    }
}
```

### Battery Events
```python
BATTERY_EVENTS = {
    'BATTERY_LOW': {
        'description': 'Battery voltage below low threshold',
        'severity': 'WARNING',
        'counter_type': 'increment',
        'threshold': '3.6V per cell',
        'triggers': ['low_battery_alert', 'shutdown_warning']
    },
    'BATTERY_CRITICAL': {
        'description': 'Battery voltage critically low',
        'severity': 'CRITICAL', 
        'counter_type': 'increment',
        'threshold': '3.4V per cell',
        'triggers': ['critical_battery_alert', 'imminent_shutdown']
    },
    'BATTERY_RECOVERED': {
        'description': 'Battery voltage recovered to normal',
        'severity': 'INFO',
        'counter_type': 'increment',
        'triggers': ['cancel_alerts', 'normal_operation']
    },
    'CHARGING_STARTED': {
        'description': 'Battery charging initiated',
        'severity': 'INFO',
        'counter_type': 'increment',
        'triggers': ['charge_cycle_start']
    },
    'CHARGING_COMPLETED': {
        'description': 'Battery charging completed',
        'severity': 'INFO',
        'counter_type': 'increment',
        'triggers': ['charge_cycle_end', 'battery_full']
    },
    'CHARGE_CYCLE_COUNT': {
        'description': 'Complete charge-discharge cycles',
        'severity': 'INFO',
        'counter_type': 'increment',
        'triggers': ['battery_health_update', 'maintenance_check']
    }
}
```

### System Events
```python
SYSTEM_EVENTS = {
    'SYSTEM_STARTUP': {
        'description': 'UPS Monitor system started',
        'severity': 'INFO',
        'counter_type': 'increment',
        'triggers': ['initialization_complete']
    },
    'SYSTEM_SHUTDOWN': {
        'description': 'UPS Monitor system shutdown',
        'severity': 'INFO',
        'counter_type': 'increment',
        'triggers': ['cleanup_procedures']
    },
    'I2C_ERROR': {
        'description': 'I2C communication error',
        'severity': 'ERROR',
        'counter_type': 'increment',
        'triggers': ['communication_retry', 'error_logging']
    },
    'CALIBRATION_PERFORMED': {
        'description': 'Battery calibration completed',
        'severity': 'INFO',
        'counter_type': 'increment',
        'triggers': ['profile_update', 'accuracy_improvement']
    },
    'TEMPERATURE_HIGH': {
        'description': 'System temperature above threshold',
        'severity': 'WARNING',
        'counter_type': 'increment',
        'threshold': '60°C',
        'triggers': ['thermal_protection', 'cooling_alert']
    }
}
```

### Safety Events
```python
SAFETY_EVENTS = {
    'OVERVOLTAGE_DETECTED': {
        'description': 'Voltage above safe limits',
        'severity': 'CRITICAL',
        'counter_type': 'increment',
        'triggers': ['protection_circuit_activation', 'safety_shutdown']
    },
    'UNDERVOLTAGE_DETECTED': {
        'description': 'Voltage below safe limits',
        'severity': 'CRITICAL',
        'counter_type': 'increment',
        'triggers': ['protection_circuit_activation', 'load_disconnect']
    },
    'OVERCURRENT_DETECTED': {
        'description': 'Current above safe limits',
        'severity': 'CRITICAL',
        'counter_type': 'increment',
        'triggers': ['current_limiting', 'protection_activation']
    },
    'THERMAL_SHUTDOWN': {
        'description': 'System shutdown due to high temperature',
        'severity': 'CRITICAL',
        'counter_type': 'increment',
        'triggers': ['emergency_shutdown', 'thermal_protection']
    }
}
```

## Counter Implementation

### Event Counter Class
```python
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque

class EventCounter:
    def __init__(self, storage_file='data/event_counters.json'):
        self.storage_file = storage_file
        self.counters = defaultdict(int)
        self.event_history = defaultdict(list)
        self.rate_windows = defaultdict(lambda: deque(maxlen=100))
        self.load_counters()
        
    def increment_counter(self, event_type, metadata=None):
        """Increment counter for specific event type."""
        timestamp = datetime.now()
        
        # Increment main counter
        self.counters[event_type] += 1
        
        # Add to history with timestamp
        event_record = {
            'timestamp': timestamp.isoformat(),
            'counter_value': self.counters[event_type],
            'metadata': metadata or {}
        }
        self.event_history[event_type].append(event_record)
        
        # Add to rate calculation window
        self.rate_windows[event_type].append(timestamp)
        
        # Trigger any associated actions
        self._trigger_event_actions(event_type, event_record)
        
        # Auto-save periodically
        if self.counters[event_type] % 10 == 0:
            self.save_counters()
    
    def get_counter(self, event_type):
        """Get current counter value."""
        return self.counters.get(event_type, 0)
    
    def get_event_rate(self, event_type, window_minutes=60):
        """Calculate event rate over specified time window."""
        if event_type not in self.rate_windows:
            return 0.0
            
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=window_minutes)
        
        # Count events within window
        recent_events = [
            ts for ts in self.rate_windows[event_type] 
            if ts >= cutoff_time
        ]
        
        return len(recent_events) / (window_minutes / 60.0)  # Events per hour
```

### Persistent Storage
```python
def save_counters(self):
    """Save counters to persistent storage."""
    data = {
        'counters': dict(self.counters),
        'last_updated': datetime.now().isoformat(),
        'event_history': {
            event_type: history[-1000:]  # Keep last 1000 events per type
            for event_type, history in self.event_history.items()
        }
    }
    
    with open(self.storage_file, 'w') as f:
        json.dump(data, f, indent=2)

def load_counters(self):
    """Load counters from persistent storage."""
    try:
        with open(self.storage_file, 'r') as f:
            data = json.load(f)
            
        self.counters.update(data.get('counters', {}))
        
        # Restore event history
        for event_type, history in data.get('event_history', {}).items():
            self.event_history[event_type] = history
            
            # Rebuild rate windows from recent history
            for event in history[-100:]:  # Last 100 events
                timestamp = datetime.fromisoformat(event['timestamp'])
                self.rate_windows[event_type].append(timestamp)
                
    except FileNotFoundError:
        # Initialize with empty counters
        pass
```

## Statistics and Analytics

### Counter Analytics
```python
def get_counter_statistics(self, event_type, days=30):
    """Generate statistics for specific event type."""
    if event_type not in self.event_history:
        return None
        
    history = self.event_history[event_type]
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Filter recent events
    recent_events = [
        event for event in history
        if datetime.fromisoformat(event['timestamp']) >= cutoff_date
    ]
    
    if not recent_events:
        return {
            'total_count': self.counters[event_type],
            'recent_count': 0,
            'daily_average': 0.0,
            'trend': 'stable'
        }
    
    # Calculate statistics
    recent_count = len(recent_events)
    daily_average = recent_count / days
    
    # Calculate trend (compare first and second half)
    mid_point = len(recent_events) // 2
    first_half = recent_events[:mid_point]
    second_half = recent_events[mid_point:]
    
    if len(first_half) > 0 and len(second_half) > 0:
        first_rate = len(first_half) / (days / 2)
        second_rate = len(second_half) / (days / 2)
        
        if second_rate > first_rate * 1.2:
            trend = 'increasing'
        elif second_rate < first_rate * 0.8:
            trend = 'decreasing'
        else:
            trend = 'stable'
    else:
        trend = 'insufficient_data'
    
    return {
        'total_count': self.counters[event_type],
        'recent_count': recent_count,
        'daily_average': round(daily_average, 2),
        'trend': trend,
        'first_occurrence': recent_events[0]['timestamp'] if recent_events else None,
        'last_occurrence': recent_events[-1]['timestamp'] if recent_events else None
    }
```

### System Health Metrics
```python
def calculate_system_health_score(self):
    """Calculate overall system health based on event counters."""
    
    # Weight factors for different event types
    weight_factors = {
        'CRITICAL': -10,    # Critical events heavily impact score
        'ERROR': -5,        # Error events moderately impact score
        'WARNING': -2,      # Warning events slightly impact score
        'INFO': 0           # Info events don't impact score
    }
    
    base_score = 100
    recent_days = 7
    
    for event_type in self.counters:
        stats = self.get_counter_statistics(event_type, recent_days)
        if not stats:
            continue
            
        # Get event severity
        severity = self._get_event_severity(event_type)
        weight = weight_factors.get(severity, 0)
        
        # Apply weight based on recent occurrences
        score_impact = stats['recent_count'] * weight
        base_score += score_impact
    
    # Normalize to 0-100 range
    health_score = max(0, min(100, base_score))
    
    # Determine health grade
    if health_score >= 90:
        grade = 'EXCELLENT'
    elif health_score >= 80:
        grade = 'GOOD'
    elif health_score >= 70:
        grade = 'FAIR'
    elif health_score >= 60:
        grade = 'POOR'
    else:
        grade = 'CRITICAL'
    
    return {
        'score': health_score,
        'grade': grade,
        'factors': self._get_health_factors()
    }
```

## Reporting and Visualization

### Counter Reports
```python
def generate_event_report(self, report_type='summary', days=30):
    """Generate comprehensive event report."""
    
    if report_type == 'summary':
        return self._generate_summary_report(days)
    elif report_type == 'detailed':
        return self._generate_detailed_report(days)
    elif report_type == 'trends':
        return self._generate_trends_report(days)

def _generate_summary_report(self, days):
    """Generate summary report of all events."""
    report = {
        'report_type': 'summary',
        'period_days': days,
        'generated_at': datetime.now().isoformat(),
        'total_events': sum(self.counters.values()),
        'event_categories': {}
    }
    
    # Group by categories
    categories = ['POWER_EVENTS', 'BATTERY_EVENTS', 'SYSTEM_EVENTS', 'SAFETY_EVENTS']
    
    for category in categories:
        category_events = [
            event for event in self.counters 
            if event in globals().get(category, {})
        ]
        
        category_count = sum(self.counters[event] for event in category_events)
        
        report['event_categories'][category] = {
            'total_count': category_count,
            'event_types': len(category_events),
            'top_events': sorted(
                [(event, self.counters[event]) for event in category_events],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    return report
```

### Data Export
```python
def export_event_data(self, format='json', output_file=None):
    """Export event data in various formats."""
    
    export_data = {
        'export_timestamp': datetime.now().isoformat(),
        'counters': dict(self.counters),
        'event_history': dict(self.event_history),
        'statistics': {
            event_type: self.get_counter_statistics(event_type)
            for event_type in self.counters
        }
    }
    
    if format == 'json':
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
        return json.dumps(export_data, indent=2)
    
    elif format == 'csv':
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Event_Type', 'Count', 'Last_Occurrence', 'Daily_Average'])
        
        # Write data rows
        for event_type, count in self.counters.items():
            stats = self.get_counter_statistics(event_type)
            writer.writerow([
                event_type,
                count,
                stats['last_occurrence'] if stats else '',
                stats['daily_average'] if stats else 0
            ])
        
        csv_data = output.getvalue()
        output.close()
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(csv_data)
        
        return csv_data
```

## Alerting Integration

### Threshold-Based Alerts
```python
def check_alert_thresholds(self):
    """Check if any event counters exceed alert thresholds."""
    
    alert_thresholds = {
        'I2C_ERROR': {'daily': 10, 'hourly': 5},
        'BATTERY_LOW': {'daily': 5, 'hourly': 2},
        'AC_POWER_LOSS': {'daily': 3, 'hourly': 1},
        'TEMPERATURE_HIGH': {'daily': 2, 'hourly': 1}
    }
    
    alerts = []
    
    for event_type, thresholds in alert_thresholds.items():
        # Check daily threshold
        daily_rate = self.get_event_rate(event_type, window_minutes=1440)  # 24 hours
        if daily_rate > thresholds.get('daily', float('inf')):
            alerts.append({
                'event_type': event_type,
                'threshold_type': 'daily',
                'current_rate': daily_rate,
                'threshold': thresholds['daily'],
                'severity': 'WARNING'
            })
        
        # Check hourly threshold
        hourly_rate = self.get_event_rate(event_type, window_minutes=60)
        if hourly_rate > thresholds.get('hourly', float('inf')):
            alerts.append({
                'event_type': event_type,
                'threshold_type': 'hourly',
                'current_rate': hourly_rate,
                'threshold': thresholds['hourly'],
                'severity': 'CRITICAL'
            })
    
    return alerts
```

## Configuration

### Event Counter Configuration
```yaml
# config/event_counters.yaml
event_counters:
  storage_file: "data/event_counters.json"
  auto_save_interval: 300  # 5 minutes
  history_retention_days: 365
  max_history_per_event: 10000
  
alert_thresholds:
  I2C_ERROR:
    daily: 10
    hourly: 5
    severity: "WARNING"
  
  BATTERY_CRITICAL:
    daily: 2
    hourly: 1
    severity: "CRITICAL"
    
  AC_POWER_LOSS:
    daily: 3
    hourly: 1
    severity: "WARNING"

reporting:
  auto_generate_daily_report: true
  auto_generate_weekly_report: true
  report_output_directory: "data/reports/"
  export_formats: ["json", "csv"]
  
health_scoring:
  enabled: true
  calculation_interval: 3600  # 1 hour
  min_events_for_trend: 5
  trend_analysis_days: 30
```

This Event Counters specification provides comprehensive event tracking capabilities that enable proactive maintenance, trend analysis, and system health monitoring for the UPS Monitor system.