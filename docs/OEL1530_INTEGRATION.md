# OWON OEL1530 Electronic Load Integration

**English | [Deutsch](OEL1530_INTEGRATION.de.md)**

Integration guide for adding OWON OEL1530 electronic load to the battery testing system.

## Hardware Overview

**OWON OEL1530 Specifications:**
- Power: 300W continuous
- Voltage: 0-150V
- Current: 0-30A
- Resolution: 1mV / 1mA
- Slew Rate: Up to 2A/μs
- Dynamic Mode: 5kHz
- Display: 2.8" LCD
- Control: USB, RS232, RS485

**Built-in Features:**
- Battery discharge test mode
- OCP test (Over Current Protection)
- OPP test (Over Power Protection)
- Remote compensation (Kelvin sensing)
- Direct banana plug connections

---

## Physical Connections

### Basic Setup (Manual Switching)

```
Charging Mode:
┌─────────────┐
│  SPE6205    │ (Power Supply)
│   60V 20A   │
└──┬──────┬───┘
   │ RED  │ BLACK
   ↓      ↓
┌──●──────●───┐
│   Battery   │
│   95Ah 12V  │
└─────────────┘

Discharge Mode:
┌─────────────┐
│   Battery   │
│   95Ah 12V  │
└──┬──────┬───┘
   │ RED  │ BLACK
   ↓      ↓
┌──●──────●───┐
│  OEL1530    │ (Electronic Load)
│   300W      │
└─────────────┘
```

**Manual Operation:**
1. Disconnect PSU banana plugs from battery
2. Connect Load banana plugs to battery
3. Run discharge test
4. Disconnect Load
5. Reconnect PSU for charging

### Advanced Setup (Relay Switching)

```
                   SPE6205 (PSU)
                       ↓
                   ┌───●───┐
                   │ Relay │ (DPDT relay)
                   └───┬───┘
                       ↓
                   ┌───●───┐
                   │Battery│
                   └───┬───┘
                       ↓
                   ┌───●───┐
                   │ Relay │ (DPDT relay)
                   └───┬───┘
                       ↓
                   OEL1530 (Load)

Controlled by Raspberry Pi GPIO
```

**Benefits:**
- Automated switching
- No manual cable swapping
- Complete unattended testing
- Safety interlocks

---

## Software Integration

### Electronic Load Driver

**File:** `src/owon_load.py`

```python
"""
OWON OEL1530 Electronic Load Driver
"""

import serial
import time
import logging

logger = logging.getLogger(__name__)


class OwonLoad:
    """Driver for OWON OEL1530 electronic load."""

    def __init__(self, port: str = '/dev/ttyUSB1', baudrate: int = 115200):
        """
        Initialize electronic load.

        Args:
            port: Serial port (e.g., /dev/ttyUSB1)
            baudrate: Communication speed
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to electronic load."""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=5.0
            )
            time.sleep(0.5)

            # Test connection
            identity = self.identify()
            if identity:
                logger.info(f"Connected to: {identity}")
                self._connected = True
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def identify(self) -> str:
        """Get device identification."""
        return self._query("*IDN?")

    def set_mode(self, mode: str):
        """
        Set operating mode.

        Args:
            mode: CC, CV, CR, CP, BATT (battery discharge)
        """
        self._send(f"MODE {mode}")

    def set_current(self, current: float):
        """Set constant current (CC mode)."""
        self._send(f"CURR {current:.3f}")

    def set_voltage(self, voltage: float):
        """Set constant voltage (CV mode)."""
        self._send(f"VOLT {voltage:.3f}")

    def enable_load(self):
        """Enable load (start sinking current)."""
        self._send("LOAD ON")

    def disable_load(self):
        """Disable load (stop sinking current)."""
        self._send("LOAD OFF")

    def measure_voltage(self) -> float:
        """Measure voltage across load."""
        response = self._query("MEAS:VOLT?")
        return float(response)

    def measure_current(self) -> float:
        """Measure current through load."""
        response = self._query("MEAS:CURR?")
        return float(response)

    def measure_power(self) -> float:
        """Measure power dissipation."""
        response = self._query("MEAS:POW?")
        return float(response)

    # Battery discharge mode
    def setup_battery_test(
        self,
        discharge_current: float,
        cutoff_voltage: float,
        capacity_limit: float = 0
    ):
        """
        Setup battery discharge test.

        Args:
            discharge_current: Discharge current in A
            cutoff_voltage: Stop voltage in V
            capacity_limit: Optional capacity limit in Ah (0 = no limit)
        """
        self._send("MODE BATT")
        self._send(f"BATT:CURR {discharge_current:.3f}")
        self._send(f"BATT:CUTOFF {cutoff_voltage:.3f}")

        if capacity_limit > 0:
            self._send(f"BATT:CAP {capacity_limit:.3f}")

    def start_battery_test(self):
        """Start battery discharge test."""
        self._send("BATT:START")

    def get_battery_test_status(self) -> dict:
        """
        Get battery test status.

        Returns:
            Dictionary with test progress
        """
        voltage = self.measure_voltage()
        current = self.measure_current()
        capacity = float(self._query("BATT:CAP?"))  # Ah discharged
        elapsed = float(self._query("BATT:TIME?"))  # seconds

        return {
            'voltage': voltage,
            'current': current,
            'capacity_ah': capacity,
            'elapsed_time': elapsed,
            'running': self._query("BATT:STAT?") == "RUN"
        }

    def _send(self, command: str):
        """Send command to load."""
        if not self._connected:
            raise RuntimeError("Not connected to load")

        cmd_bytes = f"{command}\n".encode('utf-8')
        self.serial.write(cmd_bytes)
        self.serial.flush()
        time.sleep(0.05)

    def _query(self, command: str) -> str:
        """Send query and read response."""
        if not self._connected:
            raise RuntimeError("Not connected to load")

        self.serial.reset_input_buffer()
        self._send(command)

        time.sleep(0.1)
        response = b''
        while self.serial.in_waiting:
            response += self.serial.read(self.serial.in_waiting)
            time.sleep(0.05)

        return response.decode('utf-8').strip()

    def disconnect(self):
        """Disconnect from load."""
        if self.serial:
            self.disable_load()
            self.serial.close()
            self._connected = False
```

---

## Complete Battery Testing Workflow

### Automated Capacity Test

```python
def full_capacity_test(battery_capacity_ah: float = 95):
    """
    Complete battery capacity test.

    1. Charge battery to 100%
    2. Rest period
    3. Discharge until cutoff
    4. Calculate capacity and health
    """

    # Step 1: Charge to full
    print("Step 1: Charging battery to 100%...")
    psu = OwonPSU('/dev/ttyUSB0')
    psu.connect()

    charger = BatteryCharger(psu)
    charger.charge_IUoU()  # Full IUoU charge cycle

    psu.disconnect()
    print("✓ Charging complete")

    # Step 2: Rest period (2 hours)
    print("\nStep 2: Rest period (2 hours)...")
    time.sleep(7200)
    print("✓ Rest complete")

    # Step 3: Discharge test
    print("\nStep 3: Discharge capacity test...")
    load = OwonLoad('/dev/ttyUSB1')
    load.connect()

    # Setup test: C/20 rate (4.75A), cutoff at 10.5V
    discharge_rate = battery_capacity_ah / 20  # C/20
    load.setup_battery_test(
        discharge_current=discharge_rate,
        cutoff_voltage=10.5
    )

    # Start test
    load.start_battery_test()
    print(f"  Discharging at {discharge_rate:.2f}A until 10.5V")

    # Monitor progress
    start_time = time.time()
    while True:
        status = load.get_battery_test_status()

        if not status['running']:
            break

        print(f"  {status['voltage']:.2f}V, "
              f"{status['current']:.2f}A, "
              f"{status['capacity_ah']:.2f}Ah, "
              f"{status['elapsed_time']/3600:.1f}h")

        time.sleep(60)  # Update every minute

    # Get final results
    final_status = load.get_battery_test_status()
    actual_capacity = final_status['capacity_ah']

    load.disconnect()

    # Step 4: Calculate health
    health_percent = (actual_capacity / battery_capacity_ah) * 100

    print("\n" + "="*60)
    print("CAPACITY TEST RESULTS")
    print("="*60)
    print(f"Rated Capacity:  {battery_capacity_ah:.1f} Ah")
    print(f"Actual Capacity: {actual_capacity:.2f} Ah")
    print(f"Battery Health:  {health_percent:.1f}%")

    if health_percent >= 80:
        print("Status: GOOD")
    elif health_percent >= 50:
        print("Status: FAIR ")
    else:
        print("Status: POOR (consider replacement)")

    print("="*60)

    return {
        'rated_capacity': battery_capacity_ah,
        'actual_capacity': actual_capacity,
        'health_percent': health_percent,
        'discharge_time': final_status['elapsed_time']
    }
```

---

## Built-in Test Functions

### 1. Battery Discharge Test (Built-in Mode)

**Advantages:**
- Fully automated by OEL1530 firmware
- No need to poll measurements
- Accurate Ah calculation
- Auto-stop at cutoff voltage

**Usage:**
```python
load.set_mode("BATT")
load.set_discharge_current(4.75)  # A (C/20)
load.set_cutoff_voltage(10.5)      # V
load.start()

# Wait for completion
while load.is_running():
    time.sleep(60)

capacity = load.get_capacity()  # Ah
```

### 2. OCP Test (Over Current Protection)

Tests if your PSU (SPE6205) current limit works correctly:

```python
# Set load to draw more than PSU limit
load.set_current(25.0)  # Try to draw 25A
psu.set_current(20.0)   # PSU limited to 20A

# PSU should limit at 20A (OCP working)
measured = psu.measure_current()
# Should be 20A, not 25A
```

### 3. OPP Test (Over Power Protection)

Tests if PSU power limit works:

```python
# Try to exceed power limit
load.set_current(20.0)  # 20A
psu.set_voltage(60.0)   # 60V = 1200W (max for SPE6205)

# PSU should protect itself
```

---

## MQTT Integration

Add discharge test topics:

```
battery-charger/discharge/running        # true/false
battery-charger/discharge/voltage        # V
battery-charger/discharge/current        # A
battery-charger/discharge/capacity       # Ah
battery-charger/discharge/elapsed        # seconds
battery-charger/discharge/progress       # %
```

---

## Safety Considerations

### 1. Heat Dissipation

**300W = significant heat!**

OEL1530 at full load:
- 12V × 25A = 300W
- Generates heat (cooling fan included)
- Ensure good ventilation
- Don't block vents

### 2. Switching Between PSU and Load

**NEVER connect both simultaneously!**

```python
def switch_to_discharge():
    # 1. Disable PSU output
    psu.disable_output()
    time.sleep(2)

    # 2. Switch relay OR manually swap cables
    # relay.set_mode("DISCHARGE")

    # 3. Connect load
    load.enable_load()

def switch_to_charge():
    # 1. Disable load
    load.disable_load()
    time.sleep(2)

    # 2. Switch relay OR manually swap cables
    # relay.set_mode("CHARGE")

    # 3. Enable PSU
    psu.enable_output()
```

### 3. Deep Discharge Protection

**Don't discharge below 10.5V:**
- Permanent battery damage below 10V
- Set cutoff at 10.5V minimum
- Monitor voltage continuously

---

## Cost-Effective Setup

As mentioned in the description:
**"kompakte und kostengünstige Last"** (compact and cost-effective load)

**Total System Cost:**
- OWON SPE6205: ~$200-300
- OWON OEL1530: ~$150-200
- Raspberry Pi 3: ~$35
- Cables, sensor: ~$20
- **Total: ~$400-550**

**Comparable commercial battery analyzer: $1000-3000+**

You're building a professional system for a fraction of the cost!

---

## Next Steps

1. **Purchase OEL1530**
2. **Connect to Raspberry Pi via second USB port**
3. **Test SCPI communication** (similar to PSU)
4. **Implement owon_load.py driver**
5. **Run first capacity test**
6. **Add automated charge/discharge cycling**

---

## References

- OWON OEL1530 specifications
- Battery discharge testing standards
- Capacity measurement methods
- Home lab battery testing best practices

**The OEL1530 is the perfect complement to your SPE6205!**
