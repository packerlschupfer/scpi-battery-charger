# Battery Charger - TODO List

## Hardware Enhancements

### AC Power Relay Safety (CRITICAL - Recommended!)
- [x] Create relay_control.py module with Shelly/Tasmota/GPIO support
- [x] Implement keepalive watchdog thread
- [x] Add configuration examples and testing commands
- [ ] Purchase smart relay/plug (Shelly Plug S recommended ~20€)
- [ ] Connect PSU AC power through relay
- [ ] Integrate relay control into charger_main.py
- [ ] Add relay configuration to charging_config.yaml
- [ ] Add relay state to MQTT status topics
- [ ] Test relay failsafe (simulate Pi crash)
- [ ] Document wiring diagram with photos

**Why This Is Critical:**
- If Raspberry Pi crashes, PSU continues outputting last voltage/current
- If USB connection fails, no way to turn off PSU
- Relay provides hardware failsafe: Pi crash = AC power OFF = PSU OFF
- Professional safety requirement for unattended charging

**Supported Relay Types:**
- **Shelly Plug S** - WiFi, HTTP API, local control (recommended)
- **Tasmota** - Open source firmware, MQTT native
- **GPIO Relay** - Direct Raspberry Pi control (cheaper but less safe)
- **Shelly Plus Plug** - Newer model with better API

**Implementation:**
```python
# In charger_main.py
1. Before charging: Turn relay ON (power PSU)
2. During charging: Keep relay ON
3. On completion: Turn relay OFF
4. On error/crash: Relay loses keepalive → AUTO OFF
```

**Failsafe Behavior:**
- Raspberry Pi sends keepalive every 30 seconds
- If keepalive stops (crash/freeze) → Relay turns OFF
- PSU loses AC power → Safe state

**Sample Code Created:**
See `src/relay_control.py` for complete implementation with:
- Shelly Plug support (Gen1 and Gen2/Plus)
- Tasmota support (HTTP API)
- GPIO relay support (with warnings)
- Automatic keepalive thread
- Factory pattern for easy integration

**Configuration Example (add to charging_config.yaml):**
```yaml
# AC Relay Safety Configuration
relay:
  enabled: true                    # Enable relay control
  type: "shelly"                   # shelly, tasmota, or gpio

  # Shelly Plug Configuration
  host: "192.168.1.100"            # IP address or hostname
  generation: 1                    # 1 for Shelly Plug S, 2 for Plus/Pro

  # Safety Settings
  keepalive_interval: 30           # Seconds - send ON command every 30s
  timeout: 5                       # HTTP request timeout

  # Turn relay OFF when charging completes
  turn_off_on_complete: true
  # Turn relay OFF on any error
  turn_off_on_error: true
```

**Usage in charger_main.py:**
```python
from relay_control import create_relay_controller

# Initialize relay
relay_config = config.get('relay', {})
relay = create_relay_controller(relay_config)

# Before charging starts
relay.turn_on()                    # Power on PSU
relay.start_keepalive()            # Start watchdog

# During charging
# ... normal charging loop ...

# After charging completes or on error
relay.stop_keepalive()             # Stop watchdog
relay.turn_off()                   # Power off PSU (SAFE)
```

**Testing:**
```bash
# Test Shelly Plug manually
curl "http://192.168.1.100/relay/0?turn=on"
curl "http://192.168.1.100/relay/0?turn=off"
curl "http://192.168.1.100/relay/0"  # Check status

# For Shelly Plus/Pro (Gen2)
curl "http://192.168.1.100/rpc/Switch.Set?id=0&on=true"
curl "http://192.168.1.100/rpc/Switch.Set?id=0&on=false"
curl "http://192.168.1.100/rpc/Switch.GetStatus?id=0"
```

---

### Temperature Sensor (Optional)
- [ ] Purchase DS18B20 temperature sensor ($2-5)
- [ ] Install sensor on battery case
- [ ] Enable 1-Wire interface on Raspberry Pi
- [ ] Test temperature reading
- [ ] Integrate with charger_main.py
- [ ] Add temperature to MQTT topics
- [ ] Add temperature to CSV logs

**Files created (ready to use):**
- `src/temperature_sensor.py` - DS18B20 driver
- Documentation for setup

**Benefits:**
- Monitor battery temperature during charging
- Auto-stop if overheating (>45°C)
- Better safety monitoring

---

### Electronic Load for Battery Testing (Recommended!)
- [ ] Purchase OWON OEL1530 (300W electronic load)
- [ ] Connect to Raspberry Pi via USB
- [ ] Create electronic load driver (similar to owon_psu.py)
- [ ] Implement capacity testing mode
- [ ] Implement internal resistance testing
- [ ] Add automated charge/discharge cycling
- [ ] Create diagnostic test suite

**Capabilities with OEL1530:**
- Full capacity testing (actual Ah measurement)
- Battery health assessment
- Internal resistance measurement
- Cycle life testing
- Load response testing

**Why OEL1530 is perfect:**
- 300W capacity (more than enough for 95Ah battery)
- USB/RS232/RS485 control (SCPI compatible)
- Pairs perfectly with SPE6205 charger
- Professional battery analyzer setup

---

## Software Enhancements

### Diagnostic Mode
- [x] Create diagnostic_mode.py (basic tests)
- [ ] Add internal resistance test (requires load or specific method)
- [ ] Add voltage recovery test improvements
- [ ] Create web UI for diagnostics
- [ ] Add automated health scoring system

**Already implemented:**
- Resting voltage test
- State of charge estimation
- Voltage recovery test
- Comprehensive test report

---

### Configuration Improvements
- [ ] Add 12.5V warning threshold (per German diagram)
- [ ] Create battery profile presets (different sizes/types)
- [ ] Add temperature compensation (−18mV/°C for 12V)
- [ ] Create wizard for first-time setup
- [ ] Add configuration validation

---

### Monitoring & Logging
- [ ] Create web dashboard (Flask/FastAPI)
- [ ] Add Grafana integration
- [ ] Implement InfluxDB for time-series data
- [ ] Add charging history graphs
- [ ] Email/SMS notifications for events
- [ ] Add capacity tracking over time

---

### Advanced Charging Modes
- [ ] Implement equalization charging (for flooded batteries)
- [ ] Add temperature-compensated charging
- [ ] Create custom charging profiles
- [ ] Add battery break-in mode (new batteries)
- [ ] Implement rapid charging mode (higher current)

---

## Documentation
- [ ] Create video tutorial for setup
- [ ] Add wiring diagrams with photos
- [ ] Create troubleshooting guide with common issues
- [ ] Document SCPI commands for both PSU and Load
- [ ] Add battery chemistry comparison guide
- [ ] Create safety checklist with photos

---

## Testing & Quality
- [ ] Add unit tests for all modules
- [ ] Create integration tests
- [ ] Add MQTT message validation
- [ ] Test with different battery types (AGM, Gel, etc.)
- [ ] Long-term stability testing
- [ ] Add logging of all safety events

---

## Future Ideas

### Multi-Battery Support
- [ ] Support charging multiple batteries
- [ ] Add relay switching for bank selection
- [ ] Create queue system for sequential charging
- [ ] Add battery management dashboard

### Advanced Features
- [ ] AI-based battery health prediction
- [ ] Automatic battery type detection
- [ ] Solar panel integration (MPPT)
- [ ] Grid tie-in for energy management
- [ ] Battery matching for parallel banks

### Professional Features
- [ ] Create commercial-grade UI
- [ ] Add user accounts and permissions
- [ ] Generate PDF reports
- [ ] Compliance logging (ISO standards)
- [ ] Remote access via VPN/cloud

---

## Completed ✓

- [x] OWON SPE6205 driver (owon_psu.py)
- [x] All charging modes (IUoU, CV, Pulse, Trickle, CC, Conditioning)
- [x] Safety monitoring system
- [x] Voltage plateau detection for CC mode
- [x] MQTT integration
- [x] Lead-calcium configuration (15.2V)
- [x] Lead-antimony configuration (14.4V)
- [x] Battery type identification guide
- [x] Home Assistant integration
- [x] Systemd service for auto-start
- [x] Complete documentation
- [x] CSV data logging
- [x] Migration from SPE6103 to SPE6205
- [x] Fix owon_psu.py connection bug
- [x] Deploy to Raspberry Pi (chargeberry)
- [x] Basic diagnostic mode
- [x] Multi-PSU support (SPE3102/3103/6103/6205)
- [x] PSU configuration templates for all models
- [x] Repository rename (battery-charger-raspi → scpi-battery-charger)
- [x] Beginner-friendly installation guide (docs/INSTALLATION_GUIDE.md)
- [x] Automation scripts (scripts/auto_conditioning.sh)
- [x] MQTT value rounding for clean output
- [x] Plateau detection debugging and validation

---

## Priority: Next Steps

**High Priority:**
1. ⚠️ **AC Relay Safety** - Add smart plug for PSU power control (failsafe!)
2. ⚠️ Add 12.5V warning threshold (safety per German diagram)
3. Test display messages after current charging cycle
4. Fix display bug (_command → _send_command in owon_psu.py)

**Medium Priority:**
1. Purchase OWON OEL1530 for capacity testing
2. Add temperature sensor (DS18B20)
3. Create simple web dashboard
4. Add email notifications

**Low Priority:**
1. Advanced diagnostic features
2. Multi-battery support
3. Grafana integration

---

## Notes

- System is production-ready for basic charging
- Temperature monitoring optional but recommended
- Electronic load (OEL1530) highly recommended for professional testing
- All configurations validated against German technical documentation
- MQTT working, Home Assistant ready

**Current Status:**
- ✅ Installed on chargeberry.wlan36.heim.purg.at
- ✅ OWON SPE6205 connected and operational
- ✅ MQTT broker running with Home Assistant integration
- ✅ Repository renamed to scpi-battery-charger
- ✅ Multi-PSU support added (all SPE models)
- 🔋 **Currently running**: Conditioning mode on Banner 544 09 (44Ah)
- 🔋 **In progress**: 24h conditioning cycle (started 2025-11-01 ~08:53)
- 📝 **Next**: Deploy bug fixes and test display messages after conditioning completes
