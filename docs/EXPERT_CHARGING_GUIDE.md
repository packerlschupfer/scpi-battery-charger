# Expert Battery Charging Guide

**English | [Deutsch](EXPERT_CHARGING_GUIDE.de.md)**

Traditional battery charging wisdom from 150 years of experience with lead-acid batteries.

**Source:** German battery forum expert recommendations
- **Forum Thread:** https://www.microcharge.de/forum/forum/thread/847-hochspannungsladung-von-bleiakkus
- **Technical Reference:** https://wiki.w311.info/index.php?title=Batterie_Heute

## The Traditional Method: Constant Current Charging

### Expert Quote

> "Die Stromladung ist die schnellste und sicherste Methode eine Batterie aufzuladen. Das wurde 150 Jahre lang so gemacht."

**Translation:** "Constant current charging is the fastest and safest method to charge a battery. This has been done for 150 years."

### Why Constant Current?

**The battery is a storage device for electrical work:**
- `Capacity = Current × Time` (Ah = A × h)
- Giving the battery constant current provides exactly what it needs
- Voltage is a consequence, not the control parameter
- Constant voltage charging came later only for **sealed batteries** and **in-car charging** to prevent overcharging

### Method for Open (Flooded) Batteries

1. **Initial Phase:** 10% of capacity (C/10)
   - For 44Ah battery: 4.4A
   - For 95Ah battery: 9.5A
   - Continue until gassing starts

2. **Finishing Phase:** 5% of capacity (C/20)
   - For 44Ah battery: 2.2A
   - For 95Ah battery: 4.75A
   - Continue until voltage plateaus

3. **Monitoring:** Check voltage every 2 hours
   - If voltage stops rising → battery is full
   - If voltage drops → battery is full
   - Battery should be hand-warm, but not hot

4. **End-of-Charge Voltage:**
   - New battery: 17-17.5V
   - Older battery (sulfation, dendrites): 16V or less

5. **After Charging:**
   - Top up with distilled or deionized water
   - Tap water acceptable 1-2 times only

## State of Charge - Resting Voltage

**After 2+ hours of rest, no charging or discharging:**

### Flooded Lead-Calcium Batteries

| SOC | Voltage | Specific Gravity |
|-----|---------|------------------|
| 100% | 12.7V | 1.28 g/cm³ |
| 90% | 12.6V | 1.26 g/cm³ |
| 80% | 12.5V | 1.24 g/cm³ |
| 70% | 12.4V | 1.22 g/cm³ |
| 60% | 12.3V | 1.20 g/cm³ |
| 50% | 12.2V | 1.18 g/cm³ |
| 40% | 12.1V | - |
| 30% | 11.9V | - |
| 20% | 11.8V | 1.10 g/cm³ |
| 0-10% | 11.5V | 1.05 g/cm³ |

### AGM Batteries

AGM batteries have slightly higher resting voltages:

| SOC | Voltage |
|-----|---------|
| 100% | >12.9V |
| 90% | >12.75V |
| 80% | >12.65V |
| 70% | >12.50V |
| 60% | >12.40V |
| 50% | >12.25V |
| 20% | >11.80V |
| 0-10% | >10.50V |

## Critical Thresholds

### 12.5V Warning - Recharge Immediately!

** When resting voltage drops to 12.5V (80% SOC), recharge immediately!**
- Risk of permanent damage if discharged further
- Sulfation accelerates below this point
- Per German technical diagram: "Batterie sofort laden!"

### Charging Voltages by Battery Type

**Wet/Flooded:** 14.4V
**AGM:** 14.8V
**Lead-Calcium (PbCa):** 15.4V

**Flooded with open caps:** 17-17.5V (end-of-charge voltage)

## Specific Gravity Formula

### Cell Voltage from Specific Gravity

```
Zellspannung = 0.84 + (Säuredichte in g/cm³)
Cell Voltage = 0.84 + (Specific Gravity)
```

**Example:**
- SG = 1.28 g/cm³ → Cell voltage = 2.12V → Battery = 12.72V (6 cells)
- SG = 1.24 g/cm³ → Cell voltage = 2.08V → Battery = 12.48V

### Specific Gravity from Cell Voltage

```
Specific Gravity = Cell Voltage - 0.84
SG = (Battery Voltage / 6) - 0.84
```

## Battery Health Tests

### Rest Current Test (Dendrite Detection)

**After full charge, apply 14.5V constant voltage:**

Measure current after settling (1 hour):
- **Healthy battery (44-110Ah):** ≤10mA
- **Elevated:** 10-20mA (acceptable)
- **Suspect dendrites:** >20mA
- **Poor:** >50mA (internal shorts)

**High current indicates:**
1. Dendrites forming (internal shorts)
2. Battery still charging (wait longer)
3. Sulfation

### Voltage Drop Test (Self-Discharge)

**After full charge, measure voltage over time:**

| Time | Expected Voltage | Status |
|------|------------------|--------|
| Day 1-2 | 13.0V | Normal settling |
| Week 1 | 12.9-12.8V | Good |
| Week 4 | 12.7-12.8V | Healthy |

**Rapid voltage drop indicates:**
- Dendrites discharging the battery
- Internal shorts
- If driven daily, dendrites don't matter (constantly recharged)

## Why Constant Voltage Came Later

### Historical Context

**Original method (150 years):** Constant current
- **Used:** Everywhere, by everyone
- **Advantages:** Direct, simple, what batteries need
- **Disadvantage:** Requires monitoring (gassing detection)

**Modern method:** Constant voltage (CC+CV)
- **Used:** In vehicles, sealed batteries
- **Reason:** Prevents overcharging when unmonitored
- **Disadvantage:** Slower, current tapers, may not fully charge

### For Open Batteries: Use Constant Current

If you can:
1. Open the valve caps
2. Provide ventilation
3. Monitor the charging

**Then use constant current!** It's faster, safer, and proven for 150 years.

## Desulfation (Recovery Charging)

**For deeply discharged or neglected batteries:**

1. **Method:** Constant current at 1% of capacity
   - For 44Ah: 0.44A
   - For 95Ah: 0.95A

2. **Duration:** Extended (days to weeks)

3. **Purpose:** Break down sulfate crystals on plates

4. **Alternative:** Pulse charging at higher voltage

## Warning About High Voltages

**Never use >15V on sealed AGM batteries!**
- AGM can handle: 14.8V
- Wet/flooded: 15.4V (sealed caps)
- **Flooded with open caps: 17-17.5V** (expert method)

**Most AGM batteries have opening screws** (VARTA, Banner, Moll)
- Check for screws under labels
- If found, can use higher voltages with caps open

## Tom's Advanced Conditioning Method

### Extended High-Voltage Conditioning (15.4-15.6V for 24-48h)

**Source:** Forum expert Tom's field experience with problem batteries

**Problem:** Battery won't hold charge properly
- Resting voltage drops quickly
- Shows good voltage immediately after charging
- Fails within hours or days

**Traditional Solution:**
- Charge to 14.4V (following mainstream guides)
- Battery appears charged but fails quickly

**Tom's Discovery:**
- Apply 15.4-15.6V continuously for 24-48 hours
- Monitor current (should drop as battery charges)
- Result: Resting voltage improves from 12.6V → 13.3V
- Battery holds charge much better

### Critical Monitoring During Conditioning

**Electrolysis Detection:**
- Normal: Current drops over time as battery charges
- Warning: Current stays high (>1A) for extended period (>1 hour)
- High sustained current = water electrolysis (water loss), not charging
- Action: Check water level, reduce voltage if excessive

**Gassing Threshold:**
- Poor battery: Starts gassing at 14.7V (degraded)
- Healthy battery: Only gases above 15.8V
- Test available to determine battery health

### Float Voltage Warning - Grid Corrosion

**Problem:** Continuous 13.8V float charging
- Causes positive grid corrosion
- Battery fails in ~1.5 years
- Common with always-connected chargers

**Solution:**
1. **For daily-driven vehicles:** Disable float entirely
   - Alternator provides maintenance charging
   - Only deep-charge occasionally

2. **For storage:** Lower float voltage
   - Use 13.5V maximum (not 13.8V)
   - Or use periodic conditioning instead (15.5V for 24h monthly)

3. **For standby batteries:** Periodic conditioning
   - Better than continuous float
   - 15.5V for 24h every 2-4 weeks
   - Prevents sulfation and maintains capacity

### Why Conditioning Works

From traditional battery maintenance:
- Removes light sulfation
- Equalizes cell voltages
- Activates plate material
- Improves electrolyte mixing (through gassing)
- Restores lost capacity

## Implementation in This System

### Available Charging Modes

1. **CC (Constant Current)** - Pure traditional method
   - Recommended for open flooded batteries
   - Uses plateau detection instead of voltage limit
   - 150-year proven method

2. **IUoU (3-Stage)** - Modern CC+CV hybrid
   - Good for sealed batteries
   - Bulk (CC) + Absorption (CV) + Float
   - Automatic transitions
   - **Updated:** Float voltage reduced to 13.5V (was 13.8V)

3. **Conditioning (Tom's Method)** - Extended high-voltage maintenance
   - 15.4-15.6V for 24-48 hours
   - For batteries that won't hold charge
   - Includes electrolysis detection
   - Better than continuous float for storage

4. **CV (Constant Voltage)** - Simple maintenance
   - Good for topped-up batteries
   - Gentle charging

5. **Pulse** - Desulfation mode
   - For recovery of neglected batteries

### Safety Features

- **12.5V warning** - Critical recharge threshold
- **Voltage plateau detection** - Auto-stop for CC mode
- **Energy accounting** - Track Ah delivered vs stored (83% efficiency)
- **Rest current test** - Dendrite detection at 14.5V (healthy: ≤10mA)
- **Gassing threshold test** - Determine battery health (poor: 14.7V, good: >15.8V)
- **Electrolysis monitoring** - Detect water loss during conditioning
- **SOC tables** - For both flooded and AGM batteries
- **SG calculator** - Voltage ↔ specific gravity conversion
- **Grid corrosion prevention** - Reduced float voltage (13.5V)

## Practical Tips

### Before Charging

1. Check water level (covers plates?)
2. Open valve caps if flooded
3. Ensure ventilation
4. Clean terminals
5. Measure resting voltage and specific gravity

### During Charging

1. Monitor temperature (hand-warm OK, hot = problem)
2. Watch for gassing (normal above 15.8V for Ca-Ca)
3. Check voltage every 2 hours
4. Look for plateau (voltage stops rising)

### After Charging

1. Let rest 1-2 hours
2. Measure final voltage (should be 12.7-12.8V)
3. Top up water if needed
4. Clean any acid residue
5. Close valve caps
6. Test specific gravity (should be 1.265-1.280)

### Long-Term Maintenance

1. Measure voltage weekly
2. Recharge at 12.5V (don't wait!)
3. Monthly: Check specific gravity
4. Annually: Perform rest current test
5. Keep clean and dry

## References

- **Technical Wiki:** https://wiki.w311.info/index.php?title=Batterie_Heute
- **150 years of experience:** Traditional constant current method
- **Modern safety:** Voltage plateau detection, automatic monitoring
- **Best of both worlds:** CC mode with smart electronics
