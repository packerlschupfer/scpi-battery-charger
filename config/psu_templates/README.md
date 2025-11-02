# OWON PSU Configuration Templates

**English | [Deutsch](README.de.md)**

This directory contains configuration templates for different OWON SPE series power supplies.

## Supported Models

| Model | Voltage | Current | Power | Recommended Battery Size |
|-------|---------|---------|-------|-------------------------|
| **SPE3102** | 30V | 10A | 200W | Up to 70-80Ah (12V only) |
| **SPE3103** | 30V | 10A | 300W | Up to 70-80Ah (12V only) |
| **SPE6103** | 60V | 10A | 300W | Up to 70-80Ah (12V, 24V, 48V) |
| **SPE6205** | 60V | 20A | 500W | Up to 200Ah+ (12V, 24V, 48V) |

## Usage

### 1. Choose Your PSU Template

Select the template that matches your power supply:

```bash
# For SPE3102 users:
cp config/psu_templates/SPE3102_config.yaml config/charging_config.yaml

# For SPE3103 users:
cp config/psu_templates/SPE3103_config.yaml config/charging_config.yaml

# For SPE6103 users:
cp config/psu_templates/SPE6103_config.yaml config/charging_config.yaml

# For SPE6205 users:
cp config/psu_templates/SPE6205_config.yaml config/charging_config.yaml
```

### 2. Customize for Your Battery

Edit `config/charging_config.yaml` and adjust these values for YOUR specific battery:

**Battery Specifications:**
```yaml
battery:
  capacity: 95.0                  # YOUR battery's Ah rating
  manufacture_year: 2015          # YOUR battery's year
  chemistry: "lead_calcium"       # or "lead_antimony" for old batteries
```

**Charging Current (0.1C rule):**
```yaml
charging:
  IUoU:
    bulk_current: 9.5             # 0.1 × YOUR battery capacity
                                   # Example: 44Ah → 4.4A
                                   #          70Ah → 7.0A
                                   #          95Ah → 9.5A
```

### 3. Important: Battery Size Limits

**SPE3102/3103 (10A models):**
- **Recommended maximum**: 70-80Ah batteries
- **Absolute maximum**: 100Ah (but runs at 100% continuous load)
- **Why**: 0.1C charging for 100Ah = 10A (at PSU limit)

**SPE6103 (60V / 10A):**
- Same current limit as SPE3102/3103
- Can charge 12V, 24V, or 48V batteries
- Battery size limit same as above

**SPE6205 (60V / 20A):**
- Can handle up to 200Ah batteries comfortably
- 0.1C for 200Ah = 20A (at PSU limit)
- Recommended: 150Ah max for continuous operation

## Battery Voltage Systems

All templates are configured for **12V batteries** by default.

### For 24V Batteries

Multiply all voltages by 2:
```yaml
charging:
  IUoU:
    absorption_voltage: 30.4      # 15.2V × 2
    float_voltage: 27.0           # 13.5V × 2

safety:
  absolute_max_voltage: 33.0      # 16.5V × 2
  min_voltage: 21.0               # 10.5V × 2
  warning_voltage: 25.0           # 12.5V × 2
```

### For 48V Batteries

Multiply all voltages by 4:
```yaml
charging:
  IUoU:
    absorption_voltage: 60.8      # 15.2V × 4 (limited by PSU to 60V)
    float_voltage: 54.0           # 13.5V × 4

safety:
  absolute_max_voltage: 60.0      # Limited by PSU (16.5V × 4 = 66V would exceed)
  min_voltage: 42.0               # 10.5V × 4
  warning_voltage: 50.0           # 12.5V × 4
```

**Note**: SPE3102 and SPE3103 are limited to 30V, so they **cannot** charge 24V or 48V batteries!

## Compatibility

All OWON SPE series power supplies use the same SCPI protocol, so these templates should work without code changes.

**Other SCPI power supplies may also work** - just create a custom config file with the correct voltage/current/power limits.

## Example: Banner 544 09 (44Ah) with SPE3102

```yaml
power_supply:
  model: "OWON SPE3102"
  max_voltage: 30.0
  max_current: 10.0
  max_power: 200.0

battery:
  capacity: 44.0                  # 44Ah battery
  chemistry: "lead_calcium"

charging:
  IUoU:
    bulk_current: 4.4             # 0.1C = 4.4A
    absorption_voltage: 15.2      # Lead-calcium standard
```

**PSU load**: 4.4A / 10A = 44% - Perfect for continuous operation! ✓

## Example: Exide EA954 (95Ah) with SPE6205

```yaml
power_supply:
  model: "OWON SPE6205"
  max_voltage: 60.0
  max_current: 20.0
  max_power: 500.0

battery:
  capacity: 95.0                  # 95Ah battery
  chemistry: "lead_calcium"

charging:
  IUoU:
    bulk_current: 9.5             # 0.1C = 9.5A
    absorption_voltage: 15.2      # Lead-calcium standard
```

**PSU load**: 9.5A / 20A = 47.5% - Excellent for continuous operation! ✓

## Why SPE6205 for Larger Batteries?

If you have a 95Ah battery:
- **SPE3102/3103**: Would need 9.5A (95% load) - runs very hot during 24-48h conditioning
- **SPE6205**: Uses 9.5A (47.5% load) - stays cool, longer lifespan

**Also useful for**:
- Charging multiple smaller batteries
- Other projects requiring higher power
- Future expansion

## Need Help?

See the main documentation:
- `docs/SYSTEMD_SERVICE.md` - Installation guide
- `README.md` - Main documentation
- `CONFIGURATION_SUMMARY.md` - Battery chemistry guide

GitHub: https://github.com/packerlschupfer/scpi-battery-charger
