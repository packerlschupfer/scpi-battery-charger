# Charging Modes Guide

Detailed explanation of all charging modes, when to use them, and how they work.

## Overview

The battery charger supports 4 charging modes:

1. **IUoU (3-Stage)** - Recommended for regular charging
2. **CV (Constant Voltage)** - Simple maintenance charging
3. **Pulse** - Recovery and desulfation
4. **Trickle** - Long-term storage maintenance

---

## IUoU Mode (3-Stage Charging)

**Recommended for:** Regular battery charging, optimal for lead-acid batteries

### How It Works

IUoU charging consists of three sequential stages:

```
Bulk (I) → Absorption (Uo) → Float (U)
```

### Stage 1: Bulk Charging (Constant Current)

**Duration:** Until absorption voltage reached
**Voltage:** Rises from battery voltage to absorption voltage
**Current:** Constant (e.g., 4.75A for 95Ah battery)

```
Time:    0s ─────────────────────────→ Variable
Voltage: 12.0V ─────────────────────→ 14.4V
Current: 4.75A ══════════════════════ 4.75A (constant)
```

**What happens:**
- PSU runs in constant current (CC) mode
- Battery voltage gradually rises
- Bulk of charge delivered here (~60% of total)
- Fastest charging stage

**Transition:** When voltage reaches absorption voltage (14.4V ± 0.1V)

### Stage 2: Absorption (Constant Voltage)

**Duration:** Until current drops below threshold OR timeout (2 hours)
**Voltage:** Constant at absorption voltage (14.4V)
**Current:** Gradually decreases

```
Time:    0s ─────────────────────────→ ~2h max
Voltage: 14.4V ══════════════════════ 14.4V (constant)
Current: 4.75A ─────────────────────→ <1.0A
```

**What happens:**
- PSU runs in constant voltage (CV) mode
- Current naturally tapers as battery fills
- Top-off charging, last ~30% of charge
- Critical for battery longevity

**Transition:** When current drops below threshold (e.g., 1.0A) OR timeout

### Stage 3: Float (Maintenance)

**Duration:** Indefinite (or until manually stopped)
**Voltage:** Constant at float voltage (13.6V)
**Current:** Very low (<0.5A)

```
Time:    0s ─────────────────────────→ ∞
Voltage: 13.6V ══════════════════════ 13.6V (constant)
Current: <0.5A ══════════════════════ <0.5A
```

**What happens:**
- PSU maintains safe float voltage
- Compensates for self-discharge
- Can stay connected indefinitely
- Final ~10% of charge

**Transition:** Manual stop or power off

### Configuration

```yaml
charging:
  IUoU:
    bulk_current: 4.75              # A - Charging current (0.05C for 95Ah)
    absorption_voltage: 14.4        # V - Bulk/absorption voltage
    float_voltage: 13.6             # V - Maintenance voltage
    absorption_current_threshold: 1.0  # A - Switch to float threshold
    absorption_timeout: 7200        # s - Max absorption time (2h)
    enable_float: true              # Enable float stage
```

### Voltage Guidelines by Battery Type

**IMPORTANT: Modern batteries (2010+) use lead-calcium chemistry and need HIGHER voltages!**

**Lead-Calcium (Modern, 2010+):**
- Bulk/Absorption: 15.0 - 15.4V (sealed: 15.2V, flooded: 16.2V)
- Float: 13.5 - 13.8V

**Lead-Antimony (Legacy, pre-2010):**
- Bulk/Absorption: 14.4 - 14.8V
- Float: 13.5 - 13.8V

**AGM/Gel (Sealed):**
- Bulk/Absorption: 14.4 - 15.2V (check manufacturer specs)
- Float: 13.4 - 13.7V

**Note:** The examples in this document use legacy 14.4V values for simplicity. For modern lead-calcium batteries, use 15.2V for sealed or 16.2V for flooded. See main README.md for detailed battery type identification.

### Typical Timeline

**Example: 95Ah battery at 50% discharge**

| Stage | Duration | Charge Added |
|-------|----------|--------------|
| Bulk | 6 hours | ~28.5Ah (60%) |
| Absorption | 2 hours | ~14.3Ah (30%) |
| Float | Ongoing | ~4.8Ah (10%) |
| **Total** | **~8 hours** | **~47.5Ah** |

---

## CV Mode (Constant Voltage)

**Recommended for:** Simple charging, maintenance, topping off

### How It Works

Single-stage constant voltage charging. Simplest method.

```
Time:    0s ─────────────────────────→ Variable
Voltage: 13.8V ══════════════════════ 13.8V (constant)
Current: 9.5A ──────────────────────→ <0.5A (tapers naturally)
```

**What happens:**
- PSU holds constant voltage (e.g., 13.8V)
- Current starts high, gradually decreases
- Battery charges until current drops to minimum
- Automatically stops when complete

### Configuration

```yaml
charging:
  CV:
    voltage: 13.8          # V - Hold at this voltage
    max_current: 4.0       # A - Current limit
    min_current: 0.5       # A - Complete when below this
```

### When to Use

**Good for:**
- Topping off partially charged battery
- Maintenance charging
- Simple operation
- Older batteries that don't tolerate high voltage

**Not ideal for:**
- Deep discharge recovery
- Fast charging
- Precise state of charge

### Comparison to IUoU

| Feature | CV | IUoU |
|---------|----|----- |
| Speed | Slower | Faster |
| Complexity | Simple | Advanced |
| Battery life | Good | Best |
| Deep discharge | Adequate | Optimal |

---

## Pulse Mode (Desulfation)

**Recommended for:** Sulfated batteries, recovery, old batteries

### How It Works

Alternates between high-voltage pulses and rest periods.

```
Cycle 1:  Pulse (30s) ─→ Rest (30s)
Cycle 2:  Pulse (30s) ─→ Rest (30s)
...
Cycle 20: Pulse (30s) ─→ Rest (30s) ─→ Complete
```

**Pulse Phase:**
```
Voltage: 15.5V (high!)
Current: 9.5A (typical)
Duration: 30s
```

**Rest Phase:**
```
Voltage: 13.0V (low)
Current: 0.1A (minimal)
Duration: 30s
```

### What Is Sulfation?

Lead-acid batteries develop lead sulfate crystals over time, especially when:
- Stored discharged
- Undercharged repeatedly
- Aged batteries

Sulfation reduces capacity and performance.

### How Pulse Charging Helps

High voltage pulses can:
- Break down sulfate crystals
- Restore some lost capacity
- Improve battery response
- NOT A MIRACLE CURE - can help 10-30%

### Configuration

```yaml
charging:
  Pulse:
    pulse_voltage: 15.5      # V - High pulse voltage
    pulse_current: 9.5       # A - Pulse current (C/10 rate for 95Ah)
    rest_voltage: 13.0       # V - Rest voltage
    pulse_duration: 30       # s - Pulse time
    rest_duration: 30        # s - Rest time
    max_cycles: 20           # Number of pulse cycles
```

### Safety Notes

**IMPORTANT:**
- 15.5V is HIGH for 12V battery
- Can cause gassing (hydrogen release)
- DO NOT use on AGM/Gel without research
- Only use in well-ventilated area
- Monitor battery temperature
- Not for regular charging

### When to Use

**Try pulse mode when:**
- Battery won't hold charge
- Capacity significantly reduced
- Battery has been stored discharged
- Before replacing old battery

**Don't use for:**
- Regular charging
- New batteries
- Sealed AGM/Gel (check specs first)
- High temperature conditions

### Expected Results

- **Best case:** 20-30% capacity restoration
- **Typical:** 10-15% improvement
- **Worst case:** No improvement (battery too far gone)

---

## Trickle Mode (Storage Maintenance)

**Recommended for:** Long-term storage, seasonal vehicles, backup batteries

### How It Works

Very low current, low voltage maintenance charging.

```
Time:    0s ─────────────────────────→ ∞
Voltage: 13.5V ══════════════════════ 13.5V (constant)
Current: 0.5A ═══════════════════════ 0.5A (constant)
```

**What happens:**
- Compensates for self-discharge
- Prevents sulfation during storage
- Safe to leave connected for months
- Very gentle on battery

### Configuration

```yaml
charging:
  Trickle:
    voltage: 13.5          # V - Maintenance voltage
    current: 0.5           # A - Low current
```

### When to Use

**Perfect for:**
- Winter vehicle storage (3-6 months)
- Backup power systems
- Seasonal equipment (boat, RV, motorcycle)
- Maintaining fully charged battery

**Not for:**
- Charging discharged battery (too slow)
- Fast charging needed
- Active use vehicles

### Float vs Trickle

| Feature | Float (IUoU) | Trickle |
|---------|--------------|---------|
| Voltage | 13.6V | 13.5V |
| Current | Variable (<0.5A) | Fixed (0.5A) |
| Usage | After full charge | Long-term storage |
| Start | After IUoU complete | Anytime |

---

## Selecting the Right Mode

### Decision Tree

```
Is battery deeply discharged? (< 12.0V)
├─ YES → IUoU Mode (best recovery)
└─ NO → Is battery sulfated/old?
    ├─ YES → Try Pulse Mode first, then IUoU
    └─ NO → What's your goal?
        ├─ Fast charging → IUoU Mode
        ├─ Simple maintenance → CV Mode
        └─ Storage (weeks/months) → Trickle Mode
```

### Quick Reference

| Situation | Recommended Mode | Alternative |
|-----------|------------------|-------------|
| Dead battery (< 11.5V) | IUoU | CV |
| Regular charging | IUoU | CV |
| Maintenance | CV or Trickle | IUoU Float |
| Storage (> 1 month) | Trickle | CV |
| Old/sulfated battery | Pulse → IUoU | CV |
| Quick top-off | CV | IUoU |
| Winter storage | Trickle | CV |

---

## Charging Times

**Approximate times for 95Ah battery:**

| Mode | 50% Discharged | 80% Discharged |
|------|----------------|----------------|
| IUoU @ 4.75A | ~8 hours | ~14 hours |
| CV @ 3.8V, 4A | ~10 hours | ~18 hours |
| Pulse (recovery) | ~10 hours | Not recommended |
| Trickle @ 0.5A | ~95 hours | ~152 hours |

**Note:** Times are estimates. Actual time depends on:
- Battery condition and age
- Temperature
- Previous charge history
- Battery chemistry

---

## Safety Guidelines

### Voltage Limits

**Recommended charging voltages for 12V battery:**
- Lead-Calcium Flooded (modern): 16.2V absorption, 17.0V absolute max
- Lead-Calcium Sealed (modern): 15.2V absorption, 16.5V absolute max
- Lead-Antimony (legacy): 14.4-14.8V absorption, 15.5V absolute max
- AGM/Gel (sealed): 14.1-15.2V (check specs), 15.5V absolute max

**Configured safety limit:**
```yaml
safety:
  absolute_max_voltage: 16.5  # For sealed lead-calcium
  # Use 17.0 for flooded lead-calcium
  # Use 15.5 for legacy lead-antimony
```

### Current Limits

**Hardware Limits by Model:**
- SPE3102/SPE3103: 10A maximum
- SPE6103: 10A maximum
- SPE6205: 20A maximum

**Recommended by battery capacity:**
- C/10 rate = Capacity / 10 (e.g., 95Ah / 10 = 9.5A) - Standard rate
- C/20 rate = Capacity / 20 (e.g., 95Ah / 20 = 4.75A) - Gentler/slower

**For 95Ah battery with SPE6205:**
- Gentle: 4.75A (C/20)
- Standard: 9.5A (C/10) - recommended
- Maximum: 20A (hardware limit, not recommended for battery longevity)

### Temperature

**Safe charging range:**
- Minimum: 0°C (32°F) - charging creates heat
- Maximum: 45°C (113°F) - can damage battery

**Below 0°C:** Don't charge (internal resistance too high)
**Above 45°C:** Stop charging immediately

### Ventilation

**WARNING: Flooded batteries produce hydrogen gas when charging**

Requirements:
- Well-ventilated area
- No sparks or flames nearby
- Never charge in sealed container
- Especially important during:
  - Absorption stage (gassing)
  - Pulse mode (high gassing)

---

## Monitoring Charging Progress

### Voltage Indicators

**During IUoU Mode:**
- 12.0-12.5V: Starting (Bulk)
- 12.5-14.0V: Bulk charging
- 14.0-14.4V: Approaching absorption
- 14.4V (steady): Absorption stage
- 13.6V (steady): Float stage

### Current Indicators

**Bulk stage:** Current constant at setpoint
**Absorption stage:** Current gradually decreasing
**Float stage:** Very low current (<0.5A)

### Completion Signs

**Battery is full when:**
1. IUoU: Reached float stage
2. CV: Current dropped below min_current
3. Pulse: Completed all cycles
4. Trickle: Indefinite maintenance

---

## Advanced Topics

### Temperature Compensation

**Not currently implemented**, but standard is:
- -3mV per °C per cell
- For 6-cell 12V battery: -18mV/°C
- Example: At 30°C, reduce absorption voltage by 0.18V

### Equalization Charging

**Not currently implemented**, but for flooded batteries:
- Periodic high voltage charge (15.5V)
- Balances cell voltages
- Prevents stratification
- Only for flooded, not AGM/Gel

### State of Charge (SOC) Estimation

**Rough voltage-based SOC (at rest):**
- 12.7V+ = 100%
- 12.5V = 75%
- 12.3V = 50%
- 12.1V = 25%
- 11.9V = 0%

**Note:** Voltage during charging is NOT accurate for SOC

---

## Troubleshooting

### Charging Never Completes

**Possible causes:**
- Battery capacity loss (old age)
- High self-discharge (internal short)
- Absorption current threshold too low

**Solutions:**
- Increase `absorption_current_threshold` to 1.5A
- Reduce `absorption_timeout` if waiting too long
- Consider battery replacement if very old

### Battery Gets Hot

**Normal:** Slight warmth during charging
**Problem:** Hot to touch (> 45°C)

**Actions:**
1. Stop charging immediately
2. Check ventilation
3. Reduce charging current
4. Check for internal short
5. May indicate failing battery

### Voltage Won't Reach Target

**Possible causes:**
- Heavy load connected
- Battery sulfated
- Poor connections (voltage drop)

**Solutions:**
1. Disconnect loads
2. Check and clean connections
3. Try Pulse mode for sulfation
4. Verify PSU output with multimeter

---

## See Also

- [README.md](../README.md) - Main documentation
- [MQTT_API.md](MQTT_API.md) - MQTT control reference
- [HOME_ASSISTANT.md](HOME_ASSISTANT.md) - Home Assistant integration
