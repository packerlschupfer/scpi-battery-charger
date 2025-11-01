# Configuration Summary

## Updated Configuration Files

All configurations have been updated with:
- **Correct OWON SPE6205 specifications:** 60V 20A (was incorrectly 62V 5A)
- **Optimized charging currents:** 9.5A (C/10 rate) for faster charging
- **Battery-type specific voltages:** Lead-calcium vs Lead-antimony

---

## Quick Reference

### OWON SPE6205 Specifications

| Parameter | Specification |
|-----------|--------------|
| Voltage Range | 0.01 - 60V |
| Current Range | 0.001 - 20A |
| Power | 1200W max |
| Protocol | SCPI over USB (115200 baud) |

---

## Battery Type Comparison

### Lead-Calcium (Modern, 2010+)

**Configuration File:** `config/charging_config.yaml` (default)

**Typical Battery:**
- Manufactured 2010 or later
- Label: "Calcium", "Ca/Ca", "Maintenance Free"
- Sealed construction (no removable caps)
- 1 year standby time
- 6-10+ year lifespan

**Charging Voltages:**
| Stage | Voltage | Why |
|-------|---------|-----|
| Bulk/Absorption | **15.2V** | Proper full charge for lead-calcium |
| Float | **13.8V** | Maintenance voltage |
| Gassing starts | 15.8V | Higher than lead-antimony |
| Maximum safe | 16.5V | Can handle higher voltages |

**Charging Current:**
- **9.5A** (C/10 rate for 95Ah battery)
- Faster charging with the 20A capable PSU
- Can use 4.75A for gentler charge

**Typical Charging Time (50% discharged, 95Ah battery):**
- At 9.5A: **~5 hours** (bulk + absorption)
- At 4.75A: ~10 hours

---

### Lead-Antimony (Legacy, Pre-2010)

**Configuration File:** `config/charging_config_lead_antimony.yaml`

**Typical Battery:**
- Manufactured before 2010
- Label: "Sb", "Antimony", "Conventional"
- Removable caps (serviceable)
- 3 month standby time
- 3-5 year lifespan

**Charging Voltages:**
| Stage | Voltage | Why |
|-------|---------|-----|
| Bulk/Absorption | **14.4V** | Proper voltage for lead-antimony |
| Float | **13.6V** | Maintenance voltage |
| Gassing starts | 14.8V | LOWER than lead-calcium! |
| Maximum safe | 16.0V | More sensitive to overcharge |

**Charging Current:**
- **9.5A** (C/10 rate for 95Ah battery)
- Same as lead-calcium for speed
- Can use 4.75A for gentler charge

**Typical Charging Time (50% discharged, 95Ah battery):**
- At 9.5A: **~5 hours** (bulk + absorption)
- At 4.75A: ~10 hours

---

## Critical Voltage Difference

### The Problem

**Using 14.4V (lead-antimony) on lead-calcium battery:**
- ❌ Battery never reaches full charge
- ❌ Only charges to ~80-90% capacity
- ❌ Sulfation builds up over time
- ❌ Premature failure (1-2 years instead of 6-10)
- ❌ **This is the #1 reason "dead" batteries fail prematurely!**

**Using 15.2V (lead-calcium) on lead-antimony battery:**
- ⚠️ Excessive gassing (hydrogen production)
- ⚠️ Water loss (needs frequent refilling)
- ⚠️ Shorter lifespan
- Not immediately dangerous but reduces battery life

### Why Car Batteries Often Aren't Fully Charged

Modern vehicle alternators run at **14.0-14.4V**, which is:
- ✓ Perfect for lead-antimony batteries (older vehicles)
- ❌ **Too low** for lead-calcium batteries (modern vehicles)

Lead-calcium batteries in vehicles rely on:
- Low self-discharge (1 year standby)
- Maintenance-free operation
- The **1.4V gap** below gassing voltage (15.8V)

**Result:** Modern car batteries rarely reach 100% charge from alternator alone!

**Solution:** Periodic bench charging at proper voltage (15.2V) extends battery life significantly.

---

## How to Select Configuration

### Decision Tree

```
Is your battery from 2010 or later?
├─ YES → Use default config (lead-calcium, 15.2V)
└─ NO → Use lead_antimony config (14.4V)

Or check battery label:
├─ "Calcium", "Ca/Ca", "Maintenance Free" → Lead-calcium (15.2V)
└─ "Sb", "Antimony", removable caps → Lead-antimony (14.4V)
```

### Running with Specific Configuration

```bash
# Default (lead-calcium, most common)
python3 src/charger_main.py

# Legacy lead-antimony
python3 src/charger_main.py --config config/charging_config_lead_antimony.yaml

# Systemd service (edit battery-charger.service to change config)
sudo nano /etc/systemd/system/battery-charger.service
# Change: --config /home/pi/battery-charger/config/charging_config_lead_antimony.yaml
```

---

## Charging Modes

All modes available in both configurations:

### IUoU (3-Stage) - Recommended

**Lead-Calcium:**
- Bulk: 9.5A constant current → 15.2V
- Absorption: 15.2V constant voltage → current drops to 1.0A
- Float: 13.8V constant voltage

**Lead-Antimony:**
- Bulk: 9.5A constant current → 14.4V
- Absorption: 14.4V constant voltage → current drops to 1.0A
- Float: 13.6V constant voltage

### CV (Constant Voltage)

**Lead-Calcium:** 15.0V with 9.5A limit
**Lead-Antimony:** 13.8V with 9.5A limit

### Pulse (Desulfation)

**Lead-Calcium:** 16.0V pulses (can handle higher voltage)
**Lead-Antimony:** 15.5V pulses (lower gassing voltage)

### Trickle (Maintenance)

**Lead-Calcium:** 13.8V @ 0.5A
**Lead-Antimony:** 13.5V @ 0.5A

---

## Configuration Files

### Primary Files

```
scpi-battery-charger/
├── config/
│   ├── charging_config.yaml                   # Lead-calcium (DEFAULT)
│   ├── charging_config_lead_calcium.yaml      # Lead-calcium (explicit)
│   └── charging_config_lead_antimony.yaml     # Lead-antimony (legacy)
```

### Which to Use

| Battery Type | Configuration File | Voltage |
|--------------|-------------------|---------|
| Modern (2010+) | `charging_config.yaml` (default) | 15.2V |
| Legacy (pre-2010) | `charging_config_lead_antimony.yaml` | 14.4V |

---

## Safety Limits

### Lead-Calcium

```yaml
safety:
  absolute_max_voltage: 16.5   # Can handle higher voltages
  absolute_max_current: 20.0   # Hardware limit
  max_charging_duration: 43200  # 12 hours
```

### Lead-Antimony

```yaml
safety:
  absolute_max_voltage: 16.0   # More sensitive to overcharge
  absolute_max_current: 20.0   # Hardware limit
  max_charging_duration: 43200  # 12 hours
```

---

## Performance Comparison

### Charging Time (95Ah battery, 50% discharged)

| Current | Lead-Calcium (15.2V) | Lead-Antimony (14.4V) |
|---------|---------------------|----------------------|
| 9.5A (C/10) | ~5 hours | ~5 hours |
| 4.75A (C/20) | ~10 hours | ~10 hours |

**Note:** Lead-calcium needs higher voltage (15.2V) but charging time is similar.

### Battery Lifespan

| Battery Type | Typical Lifespan | Self-Discharge |
|--------------|------------------|----------------|
| Lead-Calcium | 6-10+ years | 1 year standby |
| Lead-Antimony | 3-5 years | 3 months standby |

**When properly charged at correct voltages!**

---

## References

- [Battery Types Guide](docs/BATTERY_TYPES.md) - Detailed identification guide
- [Charging Modes](docs/CHARGING_MODES.md) - Algorithm explanations
- [MQTT API](docs/MQTT_API.md) - Control reference
- [German Battery Wiki](https://wiki.w311.info/index.php?title=Batterie_Heute) - Technical source

---

## Changes from Initial Configuration

### Hardware Specifications

| Parameter | Initial (Incorrect) | Corrected |
|-----------|-------------------|-----------|
| Max Voltage | 62V | **60V** |
| Max Current | 5A | **20A** |
| Voltage Range | Not specified | 0.01-60V |
| Current Range | Not specified | 0.001-20A |

### Charging Current

| Battery | Initial | Updated | Reasoning |
|---------|---------|---------|-----------|
| 95Ah | 4.75A | **9.5A** | C/10 rate, takes advantage of 20A capability |
| Time | ~10 hours | **~5 hours** | 2x faster charging |

### Battery Type Support

| Initial | Updated |
|---------|---------|
| Generic 14.4V config | Two configs: 15.2V (lead-calcium) and 14.4V (lead-antimony) |
| No distinction | Full battery type identification guide |
| May undercharge modern batteries | Proper voltages for each battery chemistry |

---

## Summary

✅ **All configurations updated** with correct OWON SPE6205 specs (60V 20A)
✅ **Charging current optimized** from 4.75A to 9.5A (2x faster)
✅ **Battery-specific configurations** for lead-calcium (15.2V) and lead-antimony (14.4V)
✅ **Complete documentation** on battery types and voltage requirements
✅ **Default configuration** set to lead-calcium (most common modern batteries)

**Result:** Much faster charging and proper voltages for battery longevity!
