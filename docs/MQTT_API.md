# MQTT API Reference

Complete MQTT topic and message reference for Battery Charger Controller.

## Base Topic

Default: `battery-charger`

Configurable in `config/charging_config.yaml`:
```yaml
mqtt:
  base_topic: "battery-charger"
```

## Topic Structure

```
battery-charger/
├── status/          # Published by charger (read-only)
│   ├── online
│   ├── voltage
│   ├── current
│   ├── mode
│   ├── state
│   ├── stage
│   ├── elapsed
│   ├── progress
│   └── json
└── cmd/             # Commands to charger (write)
    ├── start
    ├── stop
    ├── mode
    └── current
```

---

## Status Topics (Published)

These topics are published by the charger. Subscribe to monitor status.

### `battery-charger/status/online`

Charger online/offline status (Last Will and Testament).

**Type:** Boolean string
**Retain:** Yes
**QoS:** 1
**Update:** On connect/disconnect

**Values:**
- `"true"` - Charger online and running
- `"false"` - Charger offline or disconnected

**Example:**
```bash
mosquitto_sub -h localhost -t "battery-charger/status/online"
```

---

### `battery-charger/status/voltage`

Current battery voltage measurement.

**Type:** Float string
**Unit:** Volts (V)
**Retain:** Yes
**QoS:** 1
**Update:** Every 5 seconds (configurable)

**Range:** 0.0 - 62.0 (depends on PSU model)

**Example:**
```
13.45
14.12
12.98
```

---

### `battery-charger/status/current`

Current charging current measurement.

**Type:** Float string
**Unit:** Amperes (A)
**Retain:** Yes
**QoS:** 1
**Update:** Every 5 seconds

**Range:** 0.0 - 5.0 (SPE6205 limit)

**Example:**
```
4.23
2.15
0.87
```

---

### `battery-charger/status/mode`

Active charging mode.

**Type:** String
**Retain:** Yes
**QoS:** 1
**Update:** On mode change

**Values:**
- `"IUoU"` - 3-stage charging (Bulk/Absorption/Float)
- `"CV"` - Constant Voltage
- `"Pulse"` - Pulse charging (desulfation)
- `"Trickle"` - Trickle maintenance

**Example:**
```
IUoU
```

---

### `battery-charger/status/state`

Current charging state.

**Type:** String
**Retain:** Yes
**QoS:** 1
**Update:** On state change

**Values:**
- `"idle"` - Not charging
- `"charging"` - Actively charging
- `"completed"` - Charging complete
- `"error"` - Error occurred
- `"stopped"` - Manually stopped

**Example:**
```
charging
```

---

### `battery-charger/status/stage`

Current stage within charging mode (IUoU only).

**Type:** String
**Retain:** Yes
**QoS:** 1
**Update:** On stage change

**Values (IUoU mode):**
- `"bulk"` - Constant current phase
- `"absorption"` - Constant voltage phase
- `"float"` - Maintenance phase

**Values (Pulse mode):**
- `"pulse"` - High voltage pulse
- `"rest"` - Rest period

**Other modes:** Empty string

**Example:**
```
absorption
```

---

### `battery-charger/status/elapsed`

Elapsed charging time since start.

**Type:** Integer string
**Unit:** Seconds
**Retain:** Yes
**QoS:** 1
**Update:** Every 5 seconds

**Range:** 0 - 43200 (max 12 hours by default)

**Example:**
```
3600
7234
```

**Convert to time:**
```python
hours = elapsed // 3600
minutes = (elapsed % 3600) // 60
```

---

### `battery-charger/status/progress`

Estimated charging progress.

**Type:** Integer string
**Unit:** Percent (%)
**Retain:** Yes
**QoS:** 1
**Update:** Every 5 seconds

**Range:** 0 - 100

**Progress estimation:**
- **IUoU:** Bulk 0-60%, Absorption 60-90%, Float 90-100%
- **CV:** Based on current taper
- **Pulse:** Based on cycle count
- **Trickle:** Fixed at 50% (maintenance)

**Example:**
```
75
```

---

### `battery-charger/status/json`

Complete status as JSON object.

**Type:** JSON string
**Retain:** No
**QoS:** 1
**Update:** Every 5 seconds

**Fields:**
```json
{
  "voltage": 13.45,
  "current": 4.23,
  "mode": "IUoU",
  "state": "charging",
  "stage": "bulk",
  "elapsed": 3600,
  "progress": 45,
  "bulk_current": 4.75,
  "absorption_voltage": 14.4,
  "float_voltage": 13.6
}
```

**Example usage:**
```bash
mosquitto_sub -h localhost -t "battery-charger/status/json" | jq
```

---

## Command Topics (Subscribed)

These topics accept commands. Publish to control the charger.

### `battery-charger/cmd/start`

Start charging with current mode.

**Payload:** Empty string (any payload accepted)
**QoS:** 1
**Response:** Updates `status/state` to `"charging"`

**Example:**
```bash
mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m ""
```

**Result:**
- PSU output enabled
- Charging begins with configured mode
- Status updates start publishing

---

### `battery-charger/cmd/stop`

Stop charging immediately.

**Payload:** Empty string (any payload accepted)
**QoS:** 1
**Response:** Updates `status/state` to `"stopped"`

**Example:**
```bash
mosquitto_pub -h localhost -t "battery-charger/cmd/stop" -m ""
```

**Result:**
- PSU output disabled
- Charging stops
- Safety monitoring stops

---

### `battery-charger/cmd/mode`

Change charging mode.

**Payload:** Mode name string
**QoS:** 1
**Response:** Updates `status/mode`

**Valid values:**
- `"IUoU"` - Switch to 3-stage charging
- `"CV"` - Switch to constant voltage
- `"Pulse"` - Switch to pulse charging
- `"Trickle"` - Switch to trickle maintenance

**Example:**
```bash
mosquitto_pub -h localhost -t "battery-charger/cmd/mode" -m "CV"
```

**Behavior:**
- Stops current charging if active
- Creates new mode instance with config
- Does NOT auto-start charging
- Send `cmd/start` to begin with new mode

---

### `battery-charger/cmd/current`

Adjust charging current limit.

**Payload:** Current value as float string
**Unit:** Amperes (A)
**QoS:** 1
**Response:** Updates `status/current` (if charging)

**Range:** 0.5 - 5.0 (SPE6205 limit)

**Example:**
```bash
mosquitto_pub -h localhost -t "battery-charger/cmd/current" -m "3.5"
```

**Behavior:**
- If charging: Updates PSU current limit immediately
- If idle: No effect (will use config on next start)
- Safety limits still apply

---

## QoS Levels

**QoS 0 (At most once):** Not used
**QoS 1 (At least once):** Used for all topics (default)
**QoS 2 (Exactly once):** Supported, configurable

Configure in `charging_config.yaml`:
```yaml
mqtt:
  qos: 1  # 0, 1, or 2
```

---

## Retain Flag

**Status topics:** Retained (last value available immediately on subscribe)
**Command topics:** Not retained
**Online status (LWT):** Retained

Configure in `charging_config.yaml`:
```yaml
mqtt:
  retain: true
```

---

## Update Intervals

**Status updates:** 5 seconds (default)
**CSV logging:** 60 seconds (default)

Configure in `charging_config.yaml`:
```yaml
mqtt:
  update_interval: 5.0  # seconds

safety:
  measurement_interval: 5.0  # seconds
  log_interval: 60.0  # seconds
```

---

## Example Workflows

### Monitor All Topics

```bash
mosquitto_sub -h localhost -t "battery-charger/#" -v
```

### Start IUoU Charging

```bash
# Set mode
mosquitto_pub -h localhost -t "battery-charger/cmd/mode" -m "IUoU"

# Start charging
mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m ""
```

### Quick Status Check

```bash
mosquitto_sub -h localhost -t "battery-charger/status/json" -C 1 | jq
```

### Monitor Voltage and Current

```bash
mosquitto_sub -h localhost -t "battery-charger/status/voltage" -t "battery-charger/status/current" -v
```

### Emergency Stop

```bash
mosquitto_pub -h localhost -t "battery-charger/cmd/stop" -m ""
```

### Change Current During Charging

```bash
# Reduce current to 2A
mosquitto_pub -h localhost -t "battery-charger/cmd/current" -m "2.0"
```

---

## Python Example

```python
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to all status topics
    client.subscribe("battery-charger/status/#")

def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

    # Parse JSON status
    if msg.topic == "battery-charger/status/json":
        status = json.loads(msg.payload.decode())
        print(f"Voltage: {status['voltage']}V")
        print(f"Current: {status['current']}A")
        print(f"Progress: {status['progress']}%")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# Start charging
client.publish("battery-charger/cmd/start", "")

# Run loop
client.loop_forever()
```

---

## Node-RED Flow

```json
[
    {
        "id": "mqtt_in",
        "type": "mqtt in",
        "topic": "battery-charger/status/json",
        "qos": "1",
        "broker": "mqtt_broker",
        "outputs": 1
    },
    {
        "id": "json_parse",
        "type": "json"
    },
    {
        "id": "debug",
        "type": "debug",
        "name": "Battery Status"
    }
]
```

---

## Security

### Authentication

Configure username/password in `charging_config.yaml`:

```yaml
mqtt:
  username: "charger"
  password: "secure_password_here"
```

### TLS/SSL

For secure connections, update broker settings:

```yaml
mqtt:
  broker: "mqtt.example.com"
  port: 8883  # TLS port
  # Add certificate paths if needed
```

### Access Control (Mosquitto)

Create ACL file `/etc/mosquitto/acl`:

```
# Battery charger access
user charger
topic write battery-charger/cmd/#
topic read battery-charger/status/#

# Home Assistant access
user homeassistant
topic read battery-charger/#
topic write battery-charger/cmd/#
```

---

## Troubleshooting

### No Messages Received

```bash
# Check broker running
sudo systemctl status mosquitto

# Test broker
mosquitto_pub -h localhost -t "test" -m "hello"
mosquitto_sub -h localhost -t "test"

# Check charger running
sudo systemctl status battery-charger

# Check charger logs
sudo journalctl -u battery-charger -f
```

### Messages Not Retained

Check `retain` setting in config and verify with:

```bash
# Subscribe to see retained messages immediately
mosquitto_sub -h localhost -t "battery-charger/status/voltage"
```

Should show last voltage immediately, not wait for update.

### Commands Not Working

```bash
# Test command manually
mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m "" -d

# Check charger logs for command received
sudo journalctl -u battery-charger | grep "MQTT command"
```

---

## See Also

- [README.md](../README.md) - Main documentation
- [HOME_ASSISTANT.md](HOME_ASSISTANT.md) - Home Assistant integration
- [CHARGING_MODES.md](CHARGING_MODES.md) - Charging algorithms (if exists)
