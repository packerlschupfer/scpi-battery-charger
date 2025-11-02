# Battery Type Identification Guide

**CRITICAL:** Using the wrong charging voltages can damage your battery or prevent it from charging properly!

This guide helps you identify your battery type and select the correct configuration.

---

## Quick Identification

### Is Your Battery Lead-Calcium or Lead-Antimony?

```
┌─────────────────────────────────────────┐
│  When was your battery manufactured?    │
└─────────────────┬───────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    Before 2010        2010 or Later
         │                 │
         ▼                 ▼
   LEAD-ANTIMONY     LEAD-CALCIUM
         │                 │
         │                 │
   Use config:       Use config:
   lead_antimony     lead_calcium
   14.4V charging    15.2V charging
```

---

## Detailed Identification

### Method 1: Check Manufacturing Date

**Look for date code on battery label:**
- Format varies: "C15" (March 2015), "05/2018", "2019-07", etc.
- Often stamped or engraved on top or side

**Decision:**
- **Before 2010** → Lead-Antimony (legacy)
- **2010 or later** → Lead-Calcium (modern)

### Method 2: Check Battery Label

**Look for these markings:**

#### Lead-Calcium Indicators:
- "Calcium" or "Ca/Ca"
- "Maintenance Free"
- "MF" (Maintenance Free)
- "Sealed" (but not AGM)
- No removable caps (or sealed plugs)
- "Low Self-Discharge"

#### Lead-Antimony Indicators:
- "Sb" or "Antimony"
- "Conventional"
- "Low Maintenance" (paradoxically needs MORE maintenance)
- Removable caps for water refill
- "Add Water Only"

### Method 3: Physical Inspection

#### Lead-Calcium Battery:
- **Caps:** Sealed or decorative only (can't remove)
- **Top:** Smooth, no openings
- **Label:** "Do not open", "Sealed for life"
- **Weight:** Lighter for same capacity
- **Appearance:** Clean top, no corrosion

#### Lead-Antimony Battery:
- **Caps:** 6 removable screw caps (one per cell)
- **Top:** Can see individual cells
- **Label:** Instructions for water refill
- **Weight:** Heavier
- **Appearance:** May have acid residue/corrosion on top

### Method 4: Measure Resting Voltage

**Important:** Let battery rest for 2+ hours without charging

| Resting Voltage | Lead-Antimony | Lead-Calcium |
|-----------------|---------------|--------------|
| 12.8V | ~95% charge | ~100% charge |
| 12.6V | ~85% charge | ~90% charge |
| 12.4V | ~70% charge | ~75% charge |

Lead-calcium batteries typically show slightly lower resting voltage for same state of charge.

### Method 5: Vehicle Year (for automotive batteries)

| Vehicle Year | Standard Battery Type |
|--------------|----------------------|
| Before 1996 | Lead-Antimony |
| 1996-2009 | Transition (check label) |
| 2010+ | Lead-Calcium |

**VW:** Lead-calcium from 1996
**Ford:** Lead-calcium from 1997
**Other manufacturers:** Mostly 2000-2010

---

## Battery Chemistry Comparison

### Lead-Calcium (Modern, Ca/Ca)

**Introduced:** 1996-1997 (VW/Ford), widespread by 2010

**Electrode Material:** Lead-Calcium alloy

**Characteristics:**
- Maintenance-free (no water loss)
- Low self-discharge (1 year standby)
- Longer lifespan (6-10+ years)
- Sealed construction
- Taschen-Separators (pocket separators)
- Higher charging voltages required
- Sensitive to deep discharge below 50%
- Acid stratification when deeply discharged

**Charging Voltages:**
| Stage | Voltage |
|-------|---------|
| Bulk/Absorption | 15.0 - 15.4V |
| Float | 13.8V |
| Gassing starts at | 15.8V |
| Charging end | 17.0V (max) |

**Configuration:** `charging_config_lead_calcium.yaml`

---

### Lead-Antimony (Legacy, Sb)

**Used:** Before 1996-2010 (depending on manufacturer)

**Electrode Material:** Lead-Antimony alloy

**Characteristics:**
- Tolerates deep discharge better
- Lower charging voltages
- Easier to recondition
- Requires regular water refill
- High self-discharge (3 months standby)
- Shorter lifespan (3-5 years)
- Produces more gas when charging

**Charging Voltages:**
| Stage | Voltage |
|-------|---------|
| Bulk/Absorption | 14.0 - 14.4V |
| Float | 13.6V |
| Gassing starts at | 14.8V |
| Charging end | 16.0V (max) |

**Configuration:** `charging_config_lead_antimony.yaml`

---

## Special Cases

### AGM Batteries

**Absorbent Glass Mat** - Sealed lead-acid with absorbed electrolyte

**Identification:**
- Label says "AGM" or "VRLA"
- Very heavy
- Sealed (no caps)
- Often used in:
  - Start-stop vehicles
  - Motorcycles
  - UPS systems
  - Marine applications

**Modern AGM uses lead-calcium chemistry**

**Charging:**
- Similar to flooded lead-calcium
- Slightly lower voltages (14.4-14.7V absorption)
- More sensitive to overcharge
- Use `charging_config_lead_calcium.yaml` but reduce:
  - `absorption_voltage: 14.7` (instead of 15.2V)
  - `float_voltage: 13.6` (instead of 13.8V)

### EFB Batteries

**Enhanced Flooded Battery** - Modern flooded with improvements

**Identification:**
- Label says "EFB"
- Used in start-stop vehicles
- Flooded but enhanced design

**Charging:**
- Use lead-calcium configuration
- Same as standard flooded lead-calcium

### Gel Batteries

**Gelled electrolyte** - Sealed with gel instead of liquid

**Identification:**
- Label says "Gel"
- Very heavy
- Sealed
- Often used in solar/marine

**Charging:**
- LOWER voltages than AGM/Flooded
- Absorption: 14.1-14.4V
- Float: 13.5-13.8V
- Very sensitive to overcharge
- **Not covered by default configs - needs custom configuration**

---

## Configuration Selection

### Step-by-Step

1. **Identify your battery type** using methods above

2. **Select configuration file:**

   **Most common (2010+ automotive):**
   ```bash
   # Lead-Calcium (DEFAULT)
   python3 src/charger_main.py --config config/charging_config.yaml
   ```

   **Legacy batteries (pre-2010):**
   ```bash
   # Lead-Antimony
   python3 src/charger_main.py --config config/charging_config_lead_antimony.yaml
   ```

   **Custom (AGM, Gel, etc):**
   ```bash
   # Copy and modify lead-calcium config
   cp config/charging_config_lead_calcium.yaml config/my_battery.yaml
   nano config/my_battery.yaml
   python3 src/charger_main.py --config config/my_battery.yaml
   ```

3. **Verify with first charge:**
   - Monitor voltage during absorption stage
   - Lead-calcium: Should reach 15.2V
   - Lead-antimony: Should reach 14.4V
   - If voltage seems wrong, STOP and recheck battery type

---

## Why Voltage Matters

### The Problem with Wrong Voltages

#### Using Lead-Antimony Voltages (14.4V) on Lead-Calcium Battery:

**Result:** ❌ UNDERCHARGING
- Battery never reaches full charge
- Operates at ~80-90% capacity
- Sulfation builds up over time
- Premature failure (1-2 years instead of 6-10)
- **This is why many "dead" batteries actually just need proper charging!**

**Why this happens:**
- Vehicle alternators run at 14.0-14.4V (designed for maintenance, not full charging)
- Lead-calcium batteries in vehicles rely on low self-discharge
- External chargers using old 14.4V don't bring them to 100%

#### Using Lead-Calcium Voltages (15.2V) on Lead-Antimony Battery:

**Result:**  OVERCHARGING (but less dangerous)
- Excessive gassing (hydrogen production)
- Water consumption
- Possible grid corrosion
- Shorter lifespan
- **Not immediately dangerous but reduces battery life**

**Safety:** Lead-antimony can tolerate it briefly but wastes water

---

## Historical Context

### The Transition (1996-2010)

**Why the change?**

**Lead-Antimony problems:**
- Required regular maintenance (water refill every 3-6 months)
- High self-discharge (dead after 3 months storage)
- Warranty claims from customers not maintaining batteries
- Expensive for manufacturers (dry shipping, dealer fill/charge)

**Lead-Calcium advantages:**
- Zero maintenance (sealed for life)
- 1 year standby time (vs 3 months)
- Factory-filled and charged
- Simpler distribution chain
- 6-10 year lifespan (vs 3-5 years)

**Timeline:**
- **1996:** VW first adoption
- **1997:** Ford adoption
- **1997-2010:** Gradual industry transition
- **2010:** Full market conversion complete
- **2020+:** Only lead-calcium in automotive sector

**Reference:** [German Battery Wiki](https://wiki.w311.info/index.php?title=Batterie_Heute)

---

## Testing Your Configuration

### Safe First Charge Test

1. **Start with battery at room temperature** (15-25°C)

2. **Measure initial voltage:**
   ```bash
   mosquitto_sub -h localhost -t "battery-charger/status/voltage" -C 1
   ```

3. **Start charging with monitoring:**
   ```bash
   mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m ""
   mosquitto_sub -h localhost -t "battery-charger/status/#" -v
   ```

4. **Watch bulk stage:**
   - Voltage should gradually rise
   - Current should be constant at setpoint
   - Typical: 30 minutes to 2 hours

5. **Check absorption voltage reached:**
   - Lead-calcium: Should reach ~15.2V
   - Lead-antimony: Should reach ~14.4V
   - If voltage plateaus too early, wrong config!

6. **Monitor temperature:**
   - Battery should be warm but not hot
   - If > 40°C, reduce current or check configuration

7. **Observe completion:**
   - Current should gradually decrease
   - Float stage should engage
   - Battery should not be excessively gassing

### Signs of Wrong Configuration

**Configuration too high (voltage too high for battery):**
- Excessive gassing/bubbling (can hear it)
- Battery getting hot (>45°C)
- Acid smell
- Quick water loss (if serviceable)

**Configuration too low (voltage too low for battery):**
- Charging never completes
- Current never drops in absorption
- Battery feels only slightly warm
- Voltage never reaches expected level

---

## Common Scenarios

### Scenario 1: Car Battery (2015+ Vehicle)

**Battery:** Original equipment from 2015 VW Golf

**Type:** Lead-Calcium (Ca/Ca), Maintenance-Free

**Config:** `charging_config.yaml` (default lead-calcium)

**Voltages:** 15.2V absorption, 13.8V float

---

### Scenario 2: Classic Car Battery (1980s Vehicle)

**Battery:** Serviceable battery with removable caps

**Type:** Lead-Antimony (Sb), Conventional

**Config:** `charging_config_lead_antimony.yaml`

**Voltages:** 14.4V absorption, 13.6V float

---

### Scenario 3: Motorcycle AGM Battery

**Battery:** Sealed AGM for BMW R1200GS

**Type:** AGM with lead-calcium electrodes

**Config:** Copy lead-calcium, modify:
```yaml
IUoU:
  absorption_voltage: 14.7  # Lower than flooded
  float_voltage: 13.6
```

---

### Scenario 4: Marine Deep-Cycle

**Battery:** Trojan flooded deep-cycle

**Type:** Likely lead-calcium if modern (check label)

**Config:** Lead-calcium with extended absorption:
```yaml
IUoU:
  absorption_voltage: 15.2
  absorption_timeout: 14400  # 4 hours for deep-cycle
```

---

## Still Unsure?

### When in Doubt

1. **Start conservative:** Use lead-antimony config (14.4V)
2. **Monitor first charge carefully**
3. **If battery reaches 14.4V and current doesn't drop:**
   - Likely lead-calcium
   - Switch to lead-calcium config
4. **If battery reaches 14.4V and current drops quickly:**
   - Likely lead-antimony
   - Config is correct

### Get Expert Help

- Take photo of battery label and post to:
  - /r/batteries subreddit
  - Battery forums
  - Include: brand, model, date code, any markings

---

## See Also

- [CHARGING_MODES.md](CHARGING_MODES.md) - Charging algorithms explained
- [README.md](../README.md) - Main documentation
- [German Battery Wiki](https://wiki.w311.info/index.php?title=Batterie_Heute) - Technical reference
