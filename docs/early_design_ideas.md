# Early Design Ideas and Planning Log

This document contains the initial design and planning conversation for the Raspberry Pi Geekworm X1201/X120X UPS monitoring project, including all technical discussion from the point where “Power/Battery/AC/DC-Related Interrupts” and metrics were first discussed.  
Spelling has been corrected and formatting adapted for readability and professionalism.

---

## Conversation Transcript

---

**User:**  
Power/Battery/AC/DC-Related Interrupts (early draft of things to capture):  
- AC power loss  
- AC power restored  
- DC out loss  
- DC out restored  
- Battery voltage low  
- Battery voltage critical  
- Battery voltage recovered  
- Charging started  
- Charging stopped  
- Battery full  
- UPS fault  
- Temperature high  
- Temperature normal  
- Overcurrent detected  
- Overcurrent cleared

How would you structure these events in code and logs, and what is the best way to manage them for both software (dashboard) and hardware (LEDs, relays, etc.)?

---

**Copilot:**  
Great list! Here’s how I’d suggest structuring these events for robust monitoring, code clarity, and easy integration with both software dashboards and hardware feedback (LEDs, relays, etc.):

### 1. **Event Enumeration**

Define an enumeration for all interrupt/event types.  
For example, in Python:

```python
from enum import Enum, auto

class UPSEvent(Enum):
    AC_POWER_LOSS = auto()
    AC_POWER_RESTORED = auto()
    DC_OUT_LOSS = auto()
    DC_OUT_RESTORED = auto()
    BATTERY_VOLTAGE_LOW = auto()
    BATTERY_VOLTAGE_CRITICAL = auto()
    BATTERY_VOLTAGE_RECOVERED = auto()
    CHARGING_STARTED = auto()
    CHARGING_STOPPED = auto()
    BATTERY_FULL = auto()
    UPS_FAULT = auto()
    TEMPERATURE_HIGH = auto()
    TEMPERATURE_NORMAL = auto()
    OVERCURRENT_DETECTED = auto()
    OVERCURRENT_CLEARED = auto()
```

### 2. **Event Data Structure**

Each log entry or event should contain:
- Timestamp
- Event type (from Enum)
- Optional: value/threshold (e.g., voltage, temperature)
- Optional: descriptive message

```python
from dataclasses import dataclass
from datetime import datetime

dataclass
class UPSEventLogEntry:
    timestamp: datetime
    event: UPSEvent
    value: float = None
    message: str = ""
```

### 3. **Logging**

- Log events in a rotating file (`data/logs/ups_events.log`) in structured format (CSV, JSON, or structured text).
- Optionally, also log to system journal or syslog for advanced users.

### 4. **Hardware Handling**

- **LEDs:** Map certain events to LED states/patterns (e.g., blinking for “charging,” red for “fault,” etc.).
- **Relays:** Trigger relays on events like “AC power loss” or “overcurrent detected.”
- **Buzzer/Alert:** Sound an alarm on “battery voltage critical” or “UPS fault.”

### 5. **Software Dashboard**

- Poll or subscribe to new log events for live updates.
- Display current state, recent events, and allow user to view event history.
- Optionally, allow filtering by event type or time range.

### 6. **Extensibility**

- Make event definitions and hardware mappings user-configurable (YAML/JSON).
- Support for custom scripts/hooks per event (for integration with Home Assistant, MQTT, etc.).

---

**Summary Table:**

| Event Type             | Log Entry | LED/Relay | Dashboard      | Extensible Mapping? |
|------------------------|-----------|-----------|---------------|---------------------|
| AC power loss          | Yes       | Yes       | Yes           | Yes                 |
| Battery voltage low    | Yes       | Yes       | Yes           | Yes                 |
| UPS fault              | Yes       | Yes       | Yes           | Yes                 |
| ... (etc.)             | ...       | ...       | ...           | ...                 |

---

**Let me know if you want full code samples, a sample YAML mapping, or a concrete logging example!**

---

**User:**  
That looks great. Can you show an example YAML mapping for event-to-hardware and event-to-dashboard actions, including things like Kasa EP25 AC monitoring integration?

---

**Copilot:**  
Absolutely! Here’s a sample YAML configuration that maps UPS events to hardware actions (LEDs, relays), dashboard notifications, and even integration with an AC smart plug like the Kasa EP25.

```yaml
# config/event_mappings.yaml

events:
  AC_POWER_LOSS:
    leds: [red, blink]
    relay: off
    dashboard_notify: true
    integrations:
      kasa_ep25:
        action: "capture_power_state"
  AC_POWER_RESTORED:
    leds: [green, solid]
    relay: on
    dashboard_notify: true
    integrations:
      kasa_ep25:
        action: "capture_power_state"
  BATTERY_VOLTAGE_LOW:
    leds: [yellow, blink]
    buzzer: short_beep
    dashboard_notify: true
  BATTERY_VOLTAGE_CRITICAL:
    leds: [red, fast_blink]
    buzzer: alarm
    dashboard_notify: true
    relay: off
  CHARGING_STARTED:
    leds: [blue, pulse]
    dashboard_notify: false
  BATTERY_FULL:
    leds: [green, solid]
    dashboard_notify: true
  UPS_FAULT:
    leds: [red, solid]
    buzzer: alarm
    dashboard_notify: true
    relay: off
    integrations:
      kasa_ep25:
        action: "turn_off"

integrations:
  kasa_ep25:
    ip: "192.168.1.20"
    alias: "rack_ac"
    monitor_interval: 60  # seconds
    actions:
      capture_power_state:
        description: "Log current AC state from Kasa"
      turn_off:
        description: "Turn off AC outlet for safety"
```

**Key Points:**
- Each event can map to one or more hardware actions and dashboard notifications.
- Kasa EP25 integration supports capturing AC state/logging or turning off the outlet if needed.
- This YAML is extensible—add more events, hardware, or integrations as needed.

---

**User:**  
Perfect. How would I implement the Kasa EP25 action in Python?

---

**Copilot:**  
You can use the `python-kasa` library to control and monitor Kasa devices like the EP25. Here’s a basic example for two actions: capturing power state and turning off the smart plug.

**Install the library:**
```sh
pip install python-kasa
```

**Python code:**
```python
from kasa import SmartPlug
import asyncio

async def capture_power_state(ip):
    plug = SmartPlug(ip)
    await plug.update()
    print(f"AC Power State: {plug.is_on}, Current: {plug.current}, Power: {plug.power}, Voltage: {plug.voltage}")

async def turn_off_kasa(ip):
    plug = SmartPlug(ip)
    await plug.turn_off()
    print("Kasa plug turned off for safety.")

# Example usage:
ip = '192.168.1.20'
asyncio.run(capture_power_state(ip))
asyncio.run(turn_off_kasa(ip))
```

- Use `capture_power_state()` to log AC metrics.
- Use `turn_off_kasa()` to power off the AC outlet if a fault is detected.

This logic can be triggered based on your event mappings and config.

---

**User:**  
How would I generalize this for other smart plugs and sensors (e.g., for Zigbee/Z-Wave or Shelly devices)?

---

**Copilot:**  
To generalize AC device integration, you could:

1. **Define a base interface** (abstract class) for smart plugs/sensors.
2. **Implement adapters** for each device type (Kasa, Shelly, Zigbee, etc.).
3. **Configure devices in YAML** and instantiate them dynamically by type.

**Example Python structure:**
```python
from abc import ABC, abstractmethod

class SmartACDevice(ABC):
    @abstractmethod
    async def capture_power_state(self):
        pass

    @abstractmethod
    async def turn_off(self):
        pass

class KasaPlug(SmartACDevice):
    # ...implementation as above...

class ShellyPlug(SmartACDevice):
    # ...implement Shelly-specific logic...

class ZigbeePlug(SmartACDevice):
    # ...implement Zigbee-specific logic...

def get_device(device_type, config):
    if device_type == 'kasa':
        return KasaPlug(config['ip'])
    elif device_type == 'shelly':
        return ShellyPlug(config['ip'])
    elif device_type == 'zigbee':
        return ZigbeePlug(config['id'])
    else:
        raise ValueError("Unknown device type")
```

**YAML Example:**
```yaml
integrations:
  ac_devices:
    - type: kasa
      name: rack_outlet
      ip: 192.168.1.20
    - type: shelly
      name: backup_outlet
      ip: 192.168.1.30
    - type: zigbee
      name: lab_outlet
      id: 00158d0001a2b3c4
```

Now your event handling code can read the config, instantiate the right device adapter, and call `capture_power_state()` or `turn_off()` as needed.

---

**User:**  
That’s exactly what I need. Please save this full conversation (starting from "Power/Battery/AC/DC-Related Interrupts") as a markdown file, spell checked and formatted, for my repo.

---

**Copilot:**  
[This is the current document you are reading.]

---

## Key Design Decisions & Next Steps

- Use enums and dataclasses for robust event management.
- YAML-based configuration for event-to-action mapping.
- Extensible integration layer for smart plugs and sensors (Kasa, Shelly, Zigbee, etc.).
- Consistent logging and dashboard notification strategy.
- All code, configuration, and documentation should be modular and user-friendly.

---

## Why Save This?

- Keeps your early design rationale and technical Q&A in one place.
- Onboards collaborators and documents your architectural vision.
- Provides a professional, user-friendly reference for future expansion.

---

*End of transcript (add more as you go!)
