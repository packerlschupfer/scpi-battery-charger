# Home Assistant Integration Guide

**English | [Deutsch](HOME_ASSISTANT.de.md)**

Complete guide to integrate the Battery Charger with Home Assistant via MQTT.

## Prerequisites

- Battery charger running and connected to MQTT broker
- Home Assistant with MQTT integration configured
- MQTT broker accessible from Home Assistant

## MQTT Integration Setup

### 1. Configure MQTT in Home Assistant

If not already configured, add MQTT integration:

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **MQTT**
4. Enter your MQTT broker details (usually `localhost` or `192.168.x.x`)

### 2. Add Battery Charger Entities

Edit your `configuration.yaml` and add:

```yaml
mqtt:
  sensor:
    # Voltage sensor
    - name: "Battery Voltage"
      state_topic: "battery-charger/status/voltage"
      unit_of_measurement: "V"
      device_class: voltage
      state_class: measurement
      value_template: "{{ value | float | round(2) }}"

    # Current sensor
    - name: "Battery Current"
      state_topic: "battery-charger/status/current"
      unit_of_measurement: "A"
      device_class: current
      state_class: measurement
      value_template: "{{ value | float | round(2) }}"

    # Charging state
    - name: "Battery Charging State"
      state_topic: "battery-charger/status/state"
      icon: mdi:battery-charging

    # Charging mode
    - name: "Battery Charging Mode"
      state_topic: "battery-charger/status/mode"
      icon: mdi:cog

    # Charging stage (IUoU mode)
    - name: "Battery Charging Stage"
      state_topic: "battery-charger/status/stage"
      icon: mdi:stairs

    # Elapsed time
    - name: "Battery Charging Elapsed"
      state_topic: "battery-charger/status/elapsed"
      unit_of_measurement: "s"
      device_class: duration
      state_class: measurement
      icon: mdi:timer

    # Progress
    - name: "Battery Charging Progress"
      state_topic: "battery-charger/status/progress"
      unit_of_measurement: "%"
      icon: mdi:percent

    # Online status
    - name: "Battery Charger Online"
      state_topic: "battery-charger/status/online"
      payload_on: "true"
      payload_off: "false"
      device_class: connectivity

  # Power calculation (V × A = W)
  - name: "Battery Charging Power"
    state_topic: "battery-charger/status/json"
    unit_of_measurement: "W"
    device_class: power
    state_class: measurement
    value_template: >
      {% set data = value_json %}
      {{ (data.voltage | float * data.current | float) | round(1) }}

  switch:
    # Start/Stop switch
    - name: "Battery Charger"
      command_topic: "battery-charger/cmd/start"
      state_topic: "battery-charger/status/state"
      payload_on: ""
      payload_off: ""
      state_on: "charging"
      state_off: "idle"
      optimistic: false
      icon: mdi:battery-charging

  select:
    # Charging mode selector
    - name: "Battery Charging Mode Select"
      command_topic: "battery-charger/cmd/mode"
      state_topic: "battery-charger/status/mode"
      options:
        - "IUoU"
        - "CV"
        - "Pulse"
        - "Trickle"
      icon: mdi:cog

  number:
    # Current adjustment (adjust max based on your PSU model)
    - name: "Battery Charging Current"
      command_topic: "battery-charger/cmd/current"
      state_topic: "battery-charger/status/current"
      min: 0.5
      max: 20.0  # SPE6205: 20A, SPE3102/3103/6103: 10A
      step: 0.1
      unit_of_measurement: "A"
      device_class: current
      icon: mdi:current-dc
```

### 3. Restart Home Assistant

After adding configuration:
1. Go to **Developer Tools** → **YAML**
2. Click **Check Configuration**
3. If valid, click **Restart**

## Dashboard Cards

### Entities Card - Status Overview

```yaml
type: entities
title: Battery Charger Status
entities:
  - entity: sensor.battery_charger_online
    name: Online
  - entity: sensor.battery_charging_state
    name: State
  - entity: sensor.battery_charging_mode
    name: Mode
  - entity: sensor.battery_charging_stage
    name: Stage
  - entity: sensor.battery_charging_progress
    name: Progress
  - type: divider
  - entity: sensor.battery_voltage
    name: Voltage
  - entity: sensor.battery_current
    name: Current
  - entity: sensor.battery_charging_power
    name: Power
  - type: divider
  - entity: sensor.battery_charging_elapsed
    name: Elapsed Time
```

### Gauge Cards - Voltage and Current

```yaml
type: horizontal-stack
cards:
  - type: gauge
    entity: sensor.battery_voltage
    name: Voltage
    min: 10
    max: 16
    needle: true
    severity:
      green: 12
      yellow: 14
      red: 15

  - type: gauge
    entity: sensor.battery_current
    name: Current
    min: 0
    max: 20  # Adjust based on your PSU (SPE6205: 20A, others: 10A)
    needle: true
    severity:
      green: 0
      yellow: 10
      red: 18
```

### Progress Bar

```yaml
type: custom:bar-card
entity: sensor.battery_charging_progress
name: Charging Progress
unit_of_measurement: "%"
min: 0
max: 100
severity:
  - color: '#f44336'
    from: 0
    to: 33
  - color: '#ff9800'
    from: 33
    to: 66
  - color: '#4caf50'
    from: 66
    to: 100
```

### Control Card

```yaml
type: entities
title: Battery Charger Control
entities:
  - entity: switch.battery_charger
    name: Charging
  - entity: select.battery_charging_mode_select
    name: Mode
  - entity: number.battery_charging_current
    name: Current Limit
```

### History Graph

```yaml
type: history-graph
title: Charging History
hours_to_show: 12
entities:
  - entity: sensor.battery_voltage
    name: Voltage
  - entity: sensor.battery_current
    name: Current
  - entity: sensor.battery_charging_power
    name: Power
```

### Complete Dashboard Example

```yaml
type: vertical-stack
cards:
  # Status
  - type: entities
    title: Battery Charger
    entities:
      - entity: sensor.battery_charger_online
      - entity: sensor.battery_charging_state
      - entity: sensor.battery_charging_mode
      - entity: sensor.battery_charging_stage

  # Gauges
  - type: horizontal-stack
    cards:
      - type: gauge
        entity: sensor.battery_voltage
        name: Voltage
        min: 10
        max: 16
        needle: true

      - type: gauge
        entity: sensor.battery_current
        name: Current
        min: 0
        max: 20  # Adjust for your PSU model
        needle: true

  # Progress
  - type: entities
    entities:
      - entity: sensor.battery_charging_progress
      - entity: sensor.battery_charging_elapsed

  # Controls
  - type: entities
    title: Control
    entities:
      - entity: switch.battery_charger
      - entity: select.battery_charging_mode_select
      - entity: number.battery_charging_current

  # History
  - type: history-graph
    hours_to_show: 6
    entities:
      - entity: sensor.battery_voltage
      - entity: sensor.battery_current
```

## Automations

### Auto-Start Charging on Low Voltage

```yaml
automation:
  - alias: "Battery Charger - Auto Start"
    trigger:
      - platform: numeric_state
        entity_id: sensor.battery_voltage
        below: 12.5
    condition:
      - condition: state
        entity_id: sensor.battery_charging_state
        state: "idle"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.battery_charger
      - service: notify.mobile_app
        data:
          message: "Battery voltage low ({{ states('sensor.battery_voltage') }}V), starting charger"
```

### Stop Charging When Complete

```yaml
automation:
  - alias: "Battery Charger - Notify Complete"
    trigger:
      - platform: state
        entity_id: sensor.battery_charging_state
        to: "completed"
    action:
      - service: notify.mobile_app
        data:
          message: "Battery charging complete"
      - service: switch.turn_off
        target:
          entity_id: switch.battery_charger
```

### Alert on Safety Issues

```yaml
automation:
  - alias: "Battery Charger - Safety Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.battery_voltage
        above: 16.5  # Adjust based on battery type (sealed: 16.5V, flooded: 17.0V, legacy: 15.5V)
    action:
      - service: notify.mobile_app
        data:
          message: "ALERT: Battery voltage high ({{ states('sensor.battery_voltage') }}V)"
          title: "Battery Charger Safety"
      - service: switch.turn_off
        target:
          entity_id: switch.battery_charger
```

### Scheduled Maintenance Charging

```yaml
automation:
  - alias: "Battery Charger - Weekly Maintenance"
    trigger:
      - platform: time
        at: "02:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: select.select_option
        target:
          entity_id: select.battery_charging_mode_select
        data:
          option: "Trickle"
      - service: switch.turn_on
        target:
          entity_id: switch.battery_charger
```

## Node-RED Integration

If using Node-RED, you can create flows to control the charger:

### Start Charging Flow

```json
[
    {
        "id": "start_charge",
        "type": "mqtt out",
        "topic": "battery-charger/cmd/start",
        "payload": "",
        "broker": "mqtt_broker"
    }
]
```

### Monitor Status Flow

```json
[
    {
        "id": "monitor",
        "type": "mqtt in",
        "topic": "battery-charger/status/#",
        "broker": "mqtt_broker"
    }
]
```

## Mobile App Notifications

### Critical Alerts

Set up critical notifications for:
- Charging complete
- Safety violations
- Charger offline
- High temperature (if sensor available)

Example iOS critical notification:

```yaml
service: notify.mobile_app_iphone
data:
  message: "Battery charger safety violation!"
  title: "Critical Alert"
  data:
    push:
      sound:
        name: default
        critical: 1
        volume: 1.0
```

## Energy Dashboard Integration

To add battery charging to Energy Dashboard:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Under **Individual Devices**, click **Add Device**
3. Select `sensor.battery_charging_power`
4. Set device type to **Battery Charging**

Note: You may need to create a Riemann sum integral helper to track energy (Wh) from power (W).

## Lovelace Button Card (Advanced)

For custom button card (requires `button-card` custom component):

```yaml
type: custom:button-card
entity: switch.battery_charger
name: Battery Charger
icon: mdi:battery-charging
show_state: true
state:
  - value: "on"
    color: green
    icon: mdi:battery-charging
  - value: "off"
    color: grey
    icon: mdi:battery
tap_action:
  action: toggle
hold_action:
  action: more-info
custom_fields:
  voltage: |
    [[[ return `${states['sensor.battery_voltage'].state}V` ]]]
  current: |
    [[[ return `${states['sensor.battery_current'].state}A` ]]]
  mode: |
    [[[ return states['sensor.battery_charging_mode'].state ]]]
styles:
  card:
    - height: 120px
  custom_fields:
    voltage:
      - position: absolute
      - left: 10px
      - top: 10px
      - font-size: 14px
    current:
      - position: absolute
      - left: 10px
      - top: 30px
      - font-size: 14px
    mode:
      - position: absolute
      - left: 10px
      - top: 50px
      - font-size: 12px
      - opacity: 0.6
```

## Troubleshooting

### Entities Not Appearing

1. Check MQTT connection: **Settings** → **Devices & Services** → **MQTT**
2. Verify topics with MQTT explorer or command line:
   ```bash
   mosquitto_sub -h localhost -t "battery-charger/#" -v
   ```
3. Check `configuration.yaml` syntax
4. Restart Home Assistant

### Switch Not Working

- Verify charger is online: `sensor.battery_charger_online` should be `true`
- Check MQTT broker logs
- Test manually:
  ```bash
  mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m ""
  ```

### Values Not Updating

- Check `update_interval` in charger configuration
- Verify charger is running: `sudo systemctl status battery-charger`
- Check charger logs: `sudo journalctl -u battery-charger -f`

## Advanced Features

### Template Sensors

Create derived sensors:

```yaml
template:
  - sensor:
      # Energy consumed (approximate)
      - name: "Battery Energy Charged"
        unit_of_measurement: "Wh"
        state: >
          {% set power = states('sensor.battery_charging_power') | float %}
          {% set time = states('sensor.battery_charging_elapsed') | float / 3600 %}
          {{ (power * time) | round(1) }}

      # Estimated time remaining (very approximate)
      - name: "Battery Charging Time Remaining"
        unit_of_measurement: "min"
        state: >
          {% set progress = states('sensor.battery_charging_progress') | float %}
          {% set elapsed = states('sensor.battery_charging_elapsed') | float / 60 %}
          {% if progress > 5 %}
            {{ ((elapsed / progress * 100) - elapsed) | round(0) }}
          {% else %}
            unknown
          {% endif %}
```

### Conditional Cards

Show different cards based on state:

```yaml
type: conditional
conditions:
  - entity: sensor.battery_charging_state
    state: "charging"
card:
  type: entities
  title: Charging Active
  entities:
    - sensor.battery_voltage
    - sensor.battery_current
    - sensor.battery_charging_progress
```

## Support

For issues with Home Assistant integration:
1. Check MQTT connection
2. Verify topic names match configuration
3. Check Home Assistant logs
4. Test MQTT manually with mosquitto_sub/pub

For charger issues, see main README.md troubleshooting section.
