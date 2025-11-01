# SCPI Battery Charger - Raspberry Pi + OWON SPE Series

Professional intelligent battery charger controller for **OWON SPE series** programmable power supplies running on Raspberry Pi.

**Supported models**: SPE3102, SPE3103, SPE6103, SPE6205 (and likely other SCPI-compatible PSUs)

**Headless operation - fully controlled via MQTT and monitored remotely.**

## Features

### Core Functionality
✅ **OWON SPE Series Support** - Full SCPI control (SPE3102/3103/6103/6205)
✅ **Multiple Charging Modes** - IUoU (3-stage), CV, Pulse, Trickle
✅ **MQTT Integration** - Complete monitoring and control
✅ **Energy Accounting** - Ah/Wh delivered and stored (Coulomb counting)
✅ **Safety Monitoring** - Multi-layer protection with automatic shutdown
✅ **Data Logging** - CSV logs with complete charging history

### Advanced Features
✅ **Voltage Plateau Detection** - Auto-stop for high-voltage flooded battery charging
✅ **Power Monitoring** - Real-time V/A/W measurements
✅ **Temperature Sensor** - Optional DS18B20 support for battery temperature
✅ **Charging Efficiency Tracking** - Accounts for 17% losses (heat/gas)
✅ **12.5V Warning Threshold** - Critical SOC monitoring
✅ **Systemd Service** - Auto-start, watchdog, automatic restart

### Integration
✅ **Home Assistant** - Full integration with sensors and switches
✅ **Remote Control** - MQTT control from any client
✅ **Web Dashboards** - Compatible with Node-RED, Grafana, etc.
✅ **SSH Access** - Full Linux debugging and monitoring

## ⚠️ CRITICAL: Battery Type Configuration

**Modern batteries need DIFFERENT voltages than old batteries!**

This project includes **TWO configurations**:

1. **Lead-Calcium (Ca/Ca)** - Modern batteries (2010+)
   - Uses **15.2V** for charging
   - Default configuration
   - Most automotive batteries since 2010

2. **Lead-Antimony (Sb)** - Legacy batteries (pre-2010)
   - Uses **14.4V** for charging
   - Separate configuration file
   - Older serviceable batteries

### How to Check Your Battery

**Quick check:** When was your battery manufactured?
- **2010 or later** → Use default config (lead-calcium)
- **Before 2010** → Use `charging_config_lead_antimony.yaml`

**Label check:** Look for these markings:
- "Calcium", "Ca/Ca", "Maintenance Free" → Lead-calcium (15.2V)
- "Sb", "Antimony", removable caps → Lead-antimony (14.4V)

**📖 Full guide:** See [docs/BATTERY_TYPES.md](docs/BATTERY_TYPES.md) for detailed identification

### Why This Matters

Using wrong voltages:
- ❌ **14.4V on lead-calcium** → Battery never fully charges → premature failure
- ⚠️ **15.2V on lead-antimony** → Excessive gassing → water loss

**Most "dead" batteries just need the correct charging voltage!**

### Configuration Files

```bash
# Modern lead-calcium battery (DEFAULT)
config/charging_config.yaml                    # 15.2V charging

# Legacy lead-antimony battery
config/charging_config_lead_antimony.yaml      # 14.4V charging

# To use legacy config:
python3 src/charger_main.py --config config/charging_config_lead_antimony.yaml
```

**📖 Technical References:**
- [German Battery Technical Wiki](https://wiki.w311.info/index.php?title=Batterie_Heute) - Complete technical specifications
- [Microcharge Forum: High-Voltage Charging](https://www.microcharge.de/forum/forum/thread/847-hochspannungsladung-von-bleiakkus) - Expert charging methods
- [OWON SPE/SP/SPS Programming Manual](https://files.owon.com.cn/software/Application/SP_and_SPE_SPS_programming_manual.pdf) - Official SCPI command reference

These resources explain:
- Lead-calcium vs lead-antimony chemistry differences
- Correct charging voltages (Ladeschlussspannung: 17-17.5V for flooded)
- Traditional constant current method (150 years proven)
- State-of-charge voltage tables
- 12.5V critical threshold (80% SOC - must recharge immediately)
- Charging efficiency and losses

---

## Hardware Setup

```
OWON SPE Series USB → Raspberry Pi USB Port (/dev/ttyUSB0)
                        ↓
                   Ethernet/WiFi
                        ↓
                    MQTT Broker
                        ↓
              Home Assistant / Dashboard
```

### Choosing the Right PSU

| Model | Voltage | Current | Power | Best For |
|-------|---------|---------|-------|----------|
| **SPE3102** | 30V | 10A | 200W | Batteries up to 70-80Ah (12V only) |
| **SPE3103** | 30V | 10A | 300W | Batteries up to 70-80Ah (12V only) |
| **SPE6103** | 60V | 10A | 300W | Batteries up to 70-80Ah (12V, 24V, 48V) |
| **SPE6205** | 60V | 20A | 500W | Batteries up to 200Ah+ (12V, 24V, 48V) |

**Configuration templates** are provided in `config/psu_templates/` for each model.

See `config/psu_templates/README.md` for detailed PSU selection guide.

## Quick Start

**New to Raspberry Pi or Linux?** → See **[Complete Installation Guide](docs/INSTALLATION_GUIDE.md)** for step-by-step instructions!

**Experienced users:**

```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv git mosquitto mosquitto-clients

# 2. Clone project
cd ~
git clone https://github.com/packerlschupfer/scpi-battery-charger.git battery-charger
cd battery-charger

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install pyserial paho-mqtt pyyaml

# 4. Add user to dialout group (for USB access)
sudo usermod -a -G dialout $USER
# Log out and back in for this to take effect

# 5. Choose PSU template and configure for your battery
cp config/psu_templates/SPE6205_config.yaml config/charging_config.yaml
nano config/charging_config.yaml  # Edit battery capacity and current

# 6. Test manually first
python3 src/charger_main.py --auto-start

# 7. Install as systemd service (after testing!)
sudo cp battery-charger.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable battery-charger
sudo systemctl start battery-charger
```

## Configuration

Edit `config/charging_config.yaml`:

```yaml
# Power Supply
power_supply:
  model: "OWON SPE6205"
  port: "/dev/ttyUSB0"
  baudrate: 115200
  max_voltage: 60.0  # SPE6205: 60V max (0.01-60V range)
  max_current: 20.0  # SPE6205: 20A max (0.001-20A range)

# Battery
battery:
  type: "lead_calcium_flooded"  # Modern battery (2010+)
  nominal_voltage: 12.0
  capacity: 95.0  # Ah

# Charging Mode - Lead-Calcium Configuration
charging:
  default_mode: "IUoU"
  IUoU:
    bulk_current: 9.5         # 9.5A = C/10 rate for 95Ah
    absorption_voltage: 15.2  # Lead-calcium needs 15-15.4V!
    float_voltage: 13.8
    absorption_current_threshold: 1.0
    enable_float: true

# Safety Limits
safety:
  absolute_max_voltage: 16.5  # Safe for lead-calcium
  absolute_max_current: 20.0  # Hardware limit
  max_charging_duration: 43200  # 12 hours

# MQTT
mqtt:
  enabled: true
  broker: "localhost"
  port: 1883
  base_topic: "battery-charger"
  update_interval: 5.0  # seconds
```

## MQTT Topics

### Status (Published every 5 seconds)

```
battery-charger/status/online         # "true" / "false"
battery-charger/status/voltage        # 13.45 (V)
battery-charger/status/current        # 4.23 (A)
battery-charger/status/power          # 56.79 (W)
battery-charger/status/mode           # "IUoU"
battery-charger/status/state          # "charging" / "idle" / "completed"
battery-charger/status/stage          # "bulk" / "absorption" / "float" (IUoU mode)
battery-charger/status/elapsed        # 3600 (seconds)
battery-charger/status/progress       # 75 (%)

# Energy Accounting (Coulomb Counting)
battery-charger/status/ah_delivered   # 12.345 (Ah from PSU)
battery-charger/status/wh_delivered   # 175.23 (Wh energy consumed)
battery-charger/status/ah_stored      # 10.246 (Ah stored in battery, 83% efficiency)

# Complete JSON status
battery-charger/status/json           # Complete status as JSON
```

### Commands (Subscribed)

```
battery-charger/cmd/start             # Payload: "" (start charging)
battery-charger/cmd/stop              # Payload: "" (stop charging)
battery-charger/cmd/mode              # Payload: "IUoU" / "CV" / "Pulse" / "Trickle"
battery-charger/cmd/current           # Payload: "5.0" (set current in A)
```

## Home Assistant Integration

Add to `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "Battery Voltage"
      state_topic: "battery-charger/status/voltage"
      unit_of_measurement: "V"
      device_class: voltage

    - name: "Battery Current"
      state_topic: "battery-charger/status/current"
      unit_of_measurement: "A"
      device_class: current

    - name: "Charging State"
      state_topic: "battery-charger/status/state"

    - name: "Charging Progress"
      state_topic: "battery-charger/status/progress"
      unit_of_measurement: "%"

  switch:
    - name: "Battery Charger"
      command_topic: "battery-charger/cmd/start"
      state_topic: "battery-charger/status/state"
      payload_on: ""
      payload_off: ""
      state_on: "charging"
      state_off: "idle"
```

## Monitoring

### Via MQTT Command Line

```bash
# Subscribe to all topics
mosquitto_sub -h localhost -t "battery-charger/#" -v

# Start charging
mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m ""

# Stop charging
mosquitto_pub -h localhost -t "battery-charger/cmd/stop" -m ""

# Change mode
mosquitto_pub -h localhost -t "battery-charger/cmd/mode" -m "CV"
```

### Via Logs

```bash
# Real-time logs
sudo journalctl -u battery-charger -f

# CSV data logs
tail -f ~/battery-charger/logs/charge_*.csv
```

## Safety Features

### Multi-Layer Protection
- **Voltage Limits** - Absolute max (18V), operational max (17.2V), warning (12.5V)
- **Current Limits** - Hardware enforced (20A max from SPE6205)
- **Power Monitoring** - Real-time V×A calculation
- **Timeout Protection** - Configurable max charging duration (default 12 hours)
- **Temperature Monitoring** - Optional DS18B20 sensor with high/low limits
- **Voltage Plateau Detection** - Auto-stop for flooded batteries above 16V
- **12.5V Warning Threshold** - Critical SOC alert (80% - recharge immediately)

### Reliability Features
- **Automatic Shutdown** - On safety violations, completion, or errors
- **Systemd Watchdog** - Auto-restart on crash
- **MQTT Status** - Real-time health monitoring
- **Last Will Testament** - Offline detection
- **Complete Logging** - All sessions logged to CSV with full history
- **Energy Accounting** - Track Ah/Wh delivered and stored

## Charging Modes

### IUoU (3-Stage) - Recommended for Most Cases
- Bulk: Constant current (C/10) until absorption voltage
- Absorption: Hold absorption voltage until current tapers
- Float: Maintain 13.5V (reduced from 13.8V to prevent grid corrosion)
- Automatic transitions between stages

### CC (Constant Current) - Traditional 150-Year Method
- Pure constant current charging (C/10 rate)
- Best for open flooded batteries
- Uses voltage plateau detection for auto-stop
- Battery naturally reaches 17-17.5V when full

### Conditioning (Tom's Method) - Advanced Maintenance
- Extended high-voltage (15.4-15.6V) for 24-48 hours
- For batteries that won't hold charge properly
- Improves resting voltage and charge retention
- Includes electrolysis detection
- Better than continuous float for storage batteries

### CV (Constant Voltage)
- Hold target voltage, current tapers naturally
- Good for maintenance charging

### Pulse
- Desulfation mode for neglected batteries
- Voltage pulses with rest periods
- For recovery of sulfated batteries

### Trickle
- Low current maintenance
- Now uses 13.5V (reduced from 13.8V)
- For long-term storage

## Troubleshooting

### Service won't start

```bash
# Check status
sudo systemctl status battery-charger

# Check logs
sudo journalctl -u battery-charger -n 50

# Run manually to see errors
cd ~/battery-charger
source venv/bin/activate
python3 src/charger_main.py
```

### OWON not found

```bash
# Check USB device
ls -l /dev/ttyUSB0

# Check permissions
sudo usermod -a -G dialout pi
# Log out and back in

# Test SCPI
python3 /tmp/test_owon.py
```

### MQTT not working

```bash
# Check mosquitto running
sudo systemctl status mosquitto

# Test manually
mosquitto_pub -h localhost -t "test" -m "hello"
mosquitto_sub -h localhost -t "test"
```

## File Structure

```
scpi-battery-charger/
├── README.md
├── battery-charger.service   # Systemd service file
├── requirements.txt           # Python dependencies
│
├── src/
│   ├── charger_main.py       # Main entry point
│   ├── owon_psu.py           # OWON SCPI driver
│   ├── charging_modes.py     # Charging algorithms
│   ├── safety_monitor.py     # Safety checks
│   └── mqtt_client.py        # MQTT integration
│
├── config/
│   └── charging_config.yaml  # Main configuration
│
├── logs/                     # Data logs (auto-created)
│   └── charge_*.csv
│
└── docs/
    ├── CHARGING_MODES.md     # Mode details
    └── MQTT_API.md           # MQTT topic reference
```

## Production Deployment

1. ✅ Test manually first
2. ✅ Configure MQTT broker
3. ✅ Install systemd service
4. ✅ Add to Home Assistant
5. ✅ Test remote start/stop
6. ✅ Monitor first charging cycle
7. ✅ Set up alerts/notifications

## Advantages vs ESP32 Version

✅ **Simpler** - No display/button hardware
✅ **More Reliable** - Linux stability
✅ **Easier Debugging** - SSH access, logs
✅ **Better Integration** - MQTT, Home Assistant
✅ **More Power** - Can add web dashboard
✅ **Flexible** - Easy to extend with Python

## Documentation

- **[Installation Guide](docs/INSTALLATION_GUIDE.md)** - Complete beginner-friendly setup guide
- **[PSU Selection Guide](config/psu_templates/README.md)** - Choose the right OWON model
- **[Battery Types Guide](CONFIGURATION_SUMMARY.md)** - Lead-calcium vs lead-antimony
- **[Systemd Service Setup](docs/SYSTEMD_SERVICE.md)** - Auto-start configuration

## Support & Community

- **GitHub Issues**: https://github.com/packerlschupfer/scpi-battery-charger/issues
- **Configuration Help**: See `config/psu_templates/README.md`
- **Logs**: `~/battery-charger/logs/` and `journalctl -u battery-charger -f`
- **MQTT Testing**: `mosquitto_sub -h localhost -t 'battery-charger/#' -v`

## License

MIT License - See LICENSE file for details
