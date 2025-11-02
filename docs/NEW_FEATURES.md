# New Features Guide

**English | [Deutsch](NEW_FEATURES.de.md)**

This document describes the new features added to the battery charger system.

## Feature Summary

1. ✅ **Improved Progress Calculation** - Smoother, more accurate charging progress
2. ✅ **Battery Profile Switching** - Switch between batteries via MQTT
3. ✅ **Charge Scheduling** - Schedule charging sessions
4. ✅ **Error Recovery** - Auto-reconnect PSU/MQTT
5. ✅ **Battery History & Health** - Track charge cycles and battery health

---

## 1. Improved Progress Calculation

**What changed:**
- Progress now goes 0→70% (bulk) → 70→95% (absorption) → 100% (float)
- Was: 0→60% → 60→84% → 100% (with jumps)
- Better current taper calculation (threshold × 10 instead of × 3)

**No action needed** - automatically applies to all charging sessions.

---

## 2. Battery Profile Switching via MQTT

**Available profiles:**
- `4max_100ah` - 4MAX 100Ah battery
- `lucas_44ah` - Lucas Premium LP063 44Ah
- `banner_44ah` - Banner 544 09 44Ah
- `default` - Generic lead-calcium 95Ah
- `lead_antimony` - Legacy lead-antimony chemistry
- `lead_calcium` - Modern lead-calcium chemistry
- `conditioning` - Tom's conditioning mode

**Usage via MQTT:**
```bash
# Switch to Lucas 44Ah battery
mosquitto_pub -h localhost -t 'battery-charger/cmd/profile' -m 'lucas_44ah'

# Switch to 4MAX 100Ah battery
mosquitto_pub -h localhost -t 'battery-charger/cmd/profile' -m '4max_100ah'
```

**Rules:**
- ✅ Can switch when idle (not charging)
- ❌ Cannot switch while charging (safety)
- Automatically loads battery-specific settings (capacity, voltage, current)

---

## 3. Charge Scheduling

**Module:** `src/charge_scheduler.py`

**Features:**
- Start charging at specific time
- Set duration limit
- Auto-switch battery profile
- One-time or recurring schedules

**Example Usage (Python):**
```python
from charge_scheduler import ChargeScheduler

scheduler = ChargeScheduler()

# Schedule for 2AM tonight, 3 hours duration
scheduler.schedule_charge(
    start_time=scheduler.parse_start_time("02:00"),
    duration=scheduler.parse_duration("3h"),
    profile="lucas_44ah"
)

# In main loop:
scheduler.update()  # Call periodically
```

**Time formats:**
- `"now"` - Start immediately
- `"14:30"` - Today at 14:30 (or tomorrow if passed)
- `"2025-11-02 14:30"` - Specific date/time

**Duration formats:**
- `"1h"` - 1 hour
- `"30m"` - 30 minutes
- `"3600"` - 3600 seconds

**Integration TODO:**
- Add to `charger_main.py`
- Add MQTT commands: `battery-charger/cmd/schedule`

---

## 4. Error Recovery

**Module:** `src/error_recovery.py`

**Features:**
- Auto-reconnect PSU on USB disconnect
- Auto-reconnect MQTT broker on network issues
- Tracks disconnect counts
- Configurable check intervals

**Example Usage:**
```python
from error_recovery import ErrorRecoveryManager

recovery = ErrorRecoveryManager()

# In main loop (every 10 seconds):
psu_ok = recovery.check_psu_connection(psu, check_interval=10.0)
mqtt_ok = recovery.check_mqtt_connection(mqtt_client, check_interval=10.0)

# Get stats
stats = recovery.get_stats()
print(f"PSU disconnects: {stats['psu_disconnects']}")
print(f"MQTT disconnects: {stats['mqtt_disconnects']}")
```

**Integration TODO:**
- Add to `charger_main.py` main loop
- Set up reconnect callbacks

---

## 5. Battery History & Health Tracking

**Module:** `src/battery_history.py`

**Features:**
- Track all charge sessions per battery
- Calculate battery health (capacity degradation)
- Statistics: total Ah/Wh, average per session
- Export to CSV
- JSON storage format

**Example Usage:**
```python
from battery_history import BatteryHistoryTracker

tracker = BatteryHistoryTracker("battery_history.json")

# Record a charge session
tracker.record_charge_session(
    battery_model="lucas_44ah",
    start_voltage=12.44,
    end_voltage=13.5,
    ah_delivered=1.865,
    wh_delivered=28.0,
    duration=7742,  # seconds
    mode="IUoU",
    success=True
)

# Get battery statistics
stats = tracker.get_battery_stats("lucas_44ah")
print(f"Total sessions: {stats['total_sessions']}")
print(f"Battery health: {stats['estimated_health']}%")
print(f"Average Ah: {stats['avg_ah_per_session']}Ah")

# Export to CSV
tracker.export_csv("lucas_44ah", "lucas_history.csv")
```

**Battery Health Calculation:**
- Compares recent average Ah to historical average
- 100% = battery accepting same charge as before
- <90% = capacity degradation detected
- Helps predict battery replacement needs

**Integration TODO:**
- Add to `charger_main.py`
- Record session on charge completion
- Publish stats via MQTT

---

## Integration Checklist

To fully integrate these features into `charger_main.py`:

### Charge Scheduler
- [ ] Import `ChargeScheduler`
- [ ] Initialize in `__init__`
- [ ] Add `scheduler.update()` to main loop
- [ ] Add MQTT commands:
  - `battery-charger/cmd/schedule/start` (time)
  - `battery-charger/cmd/schedule/duration` (duration)
  - `battery-charger/cmd/schedule/cancel`
- [ ] Publish schedule status to MQTT

### Error Recovery
- [ ] Import `ErrorRecoveryManager`
- [ ] Initialize in `__init__`
- [ ] Add connection checks to main loop
- [ ] Set up reconnect callbacks
- [ ] Publish recovery stats to MQTT

### Battery History
- [ ] Import `BatteryHistoryTracker`
- [ ] Initialize in `__init__`
- [ ] Record session in `stop_charging()`
- [ ] Add MQTT topic: `battery-charger/status/battery_health`
- [ ] Publish stats periodically

---

## Quick Test

**Test battery profile switching:**
```bash
# Stop current charging
ssh mrnice@chargeberry.wlan36.heim.purg.at "cd ~/battery-charger/scripts && ./stop_charging.sh"

# Deploy new code
rsync -avz src/*.py mrnice@chargeberry.wlan36.heim.purg.at:~/battery-charger/src/

# Switch profile via MQTT
mosquitto_pub -h chargeberry.wlan36.heim.purg.at -t 'battery-charger/cmd/profile' -m 'lucas_44ah'

# Verify in logs
ssh mrnice@chargeberry.wlan36.heim.purg.at "screen -r charging"
```

---

## Benefits

1. **Progress Calculation:** More accurate progress display, no jumps
2. **Profile Switching:** Quick battery changes without config editing
3. **Scheduling:** Charge during off-peak hours, set time limits
4. **Error Recovery:** Reliable operation despite USB/network issues
5. **History Tracking:** Monitor battery health, predict replacement

All features are modular and can be enabled/disabled independently.
