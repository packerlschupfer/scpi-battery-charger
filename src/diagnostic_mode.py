"""
Diagnostic mode for battery testing (without external load).
"""

import time
import logging
from typing import Dict, Optional
from owon_psu import OwonPSU

logger = logging.getLogger(__name__)


class BatteryDiagnostics:
    """Battery diagnostic tests using only the PSU."""

    def __init__(self, psu: OwonPSU):
        """
        Initialize diagnostics.

        Args:
            psu: Connected OWON PSU instance
        """
        self.psu = psu

    def test_resting_voltage(self, rest_time: int = 300) -> float:
        """
        Measure battery resting voltage (no load).

        Args:
            rest_time: Time to wait before measurement (seconds)

        Returns:
            Resting voltage in V
        """
        logger.info(f"Testing resting voltage (waiting {rest_time}s)...")

        # Ensure output is off
        self.psu.disable_output()
        time.sleep(rest_time)

        # Measure voltage
        voltage = self.psu.measure_voltage()
        logger.info(f"Resting voltage: {voltage:.3f}V")

        return voltage

    def estimate_state_of_charge(self, voltage: float, battery_type: str = 'flooded') -> Dict:
        """
        Estimate state of charge from resting voltage.

        Args:
            voltage: Resting voltage in V (after 2+ hours rest)
            battery_type: 'flooded' or 'agm'

        Returns:
            Dictionary with SOC estimate and battery status
        """
        # SOC lookup tables based on battery type
        # Source: https://wiki.w311.info/index.php?title=Batterie_Heute

        if battery_type == 'agm':
            # AGM batteries have higher resting voltages
            soc_table = [
                (12.90, 100),
                (12.75, 90),
                (12.65, 80),
                (12.50, 70),
                (12.40, 60),
                (12.25, 50),
                (11.80, 20),
                (10.50, 5),
            ]
        else:  # flooded (default)
            # Flooded lead-calcium batteries
            soc_table = [
                (12.70, 100),
                (12.60, 90),
                (12.50, 80),  # ⚠️ Critical threshold - recharge immediately!
                (12.40, 70),
                (12.30, 60),
                (12.20, 50),
                (12.10, 40),
                (11.90, 30),
                (11.80, 20),
                (11.50, 10),
                (10.50, 0),
            ]

        # Find closest match
        soc = 0
        for v, s in soc_table:
            if voltage >= v:
                soc = s
                break

        # Determine battery health
        if voltage < 10.5:
            status = "critically_low"
        elif voltage < 11.5:
            status = "deeply_discharged"
        elif voltage < 12.5:
            status = "needs_charging"  # ⚠️ Critical 80% threshold per German diagram!
        elif voltage < 12.7:
            status = "good"
        else:
            status = "excellent"

        return {
            'voltage': voltage,
            'soc_percent': soc,
            'status': status,
            'battery_type': battery_type
        }

    def voltage_to_specific_gravity(self, cell_voltage: float) -> float:
        """
        Calculate specific gravity from cell voltage.

        Formula: Zellspannung = 0.84 + (Säuredichte in g/cm³)
        Rearranged: Säuredichte = Zellspannung - 0.84

        Args:
            cell_voltage: Voltage per cell (battery_voltage / 6)

        Returns:
            Specific gravity in g/cm³ (kg/L)
        """
        return cell_voltage - 0.84

    def specific_gravity_to_voltage(self, specific_gravity: float) -> float:
        """
        Calculate cell voltage from specific gravity.

        Formula: Zellspannung = 0.84 + (Säuredichte in g/cm³)

        Args:
            specific_gravity: Specific gravity in g/cm³ (kg/L)

        Returns:
            Voltage per cell
        """
        return 0.84 + specific_gravity

    def analyze_specific_gravity(self, sg_reading: float) -> Dict:
        """
        Analyze specific gravity reading and correlate to battery state.

        Args:
            sg_reading: Specific gravity reading in g/cm³ (kg/L)

        Returns:
            Dictionary with analysis
        """
        # Calculate expected voltage
        cell_voltage = self.specific_gravity_to_voltage(sg_reading)
        battery_voltage = cell_voltage * 6

        # Estimate SOC from SG (flooded batteries)
        # Source: https://wiki.w311.info/index.php?title=Batterie_Heute
        sg_soc_table = [
            (1.28, 100),
            (1.26, 90),
            (1.24, 80),
            (1.22, 70),
            (1.20, 60),
            (1.18, 50),
            (1.10, 20),
            (1.05, 5),
        ]

        soc = 0
        for sg, s in sg_soc_table:
            if sg_reading >= sg:
                soc = s
                break

        return {
            'specific_gravity': sg_reading,
            'cell_voltage': round(cell_voltage, 3),
            'battery_voltage': round(battery_voltage, 2),
            'soc_percent': soc,
            'fully_charged_sg': 1.28,
            'needs_water': sg_reading > 1.30,  # Too high = water loss
            'sulfation_risk': sg_reading < 1.15  # Too low = sulfation
        }

    def test_rest_current(self, test_voltage: float = 14.5, duration: int = 300) -> Dict:
        """
        Test rest current at maintenance voltage (dendrite detection).

        After full charge, apply constant voltage and measure rest current.
        Healthy battery: ≤10mA for 44-110Ah batteries
        High current indicates dendrites (internal shorts) or ongoing charging.

        Expert recommendation: "Bei einer Spannung um 14,5 V stellt sich bei
        einer intakten Batterie (44...110 Ah) eine Ruhestrom von maximal 10 mA ein."

        Args:
            test_voltage: Test voltage in V (default 14.5V)
            duration: Test duration in seconds (default 5 minutes)

        Returns:
            Dictionary with rest current analysis
        """
        logger.info(f"Testing rest current at {test_voltage}V for {duration}s...")

        # Set voltage and enable output
        self.psu.set_voltage(test_voltage)
        self.psu.set_current(0.1)  # Low current limit
        self.psu.enable_output()

        # Wait for settling (1 minute)
        logger.info("Waiting 60s for settling...")
        time.sleep(60)

        # Measure current over time
        measurements = []
        sample_interval = 30  # seconds
        num_samples = duration // sample_interval

        for i in range(num_samples):
            current_ma = self.psu.measure_current() * 1000  # Convert to mA
            voltage = self.psu.measure_voltage()
            measurements.append({
                'time': i * sample_interval,
                'current_ma': current_ma,
                'voltage': voltage
            })
            logger.info(f"Sample {i+1}/{num_samples}: {current_ma:.1f}mA @ {voltage:.2f}V")

            if i < num_samples - 1:
                time.sleep(sample_interval)

        # Disable output
        self.psu.disable_output()

        # Analysis
        avg_current = sum(m['current_ma'] for m in measurements) / len(measurements)
        max_current = max(m['current_ma'] for m in measurements)
        min_current = min(m['current_ma'] for m in measurements)

        # Assessment based on expert's criteria
        # Healthy: ≤10mA for 44-110Ah batteries
        if avg_current <= 10:
            status = "excellent"
            assessment = "Battery is healthy - very low rest current"
        elif avg_current <= 20:
            status = "good"
            assessment = "Battery is acceptable - slightly elevated rest current"
        elif avg_current <= 50:
            status = "fair"
            assessment = "Possible dendrites or incomplete charge - monitor closely"
        else:
            status = "poor"
            assessment = "High rest current - likely dendrites (internal shorts) or sulfation"

        return {
            'test_voltage': test_voltage,
            'duration_seconds': duration,
            'measurements': measurements,
            'avg_current_ma': round(avg_current, 2),
            'max_current_ma': round(max_current, 2),
            'min_current_ma': round(min_current, 2),
            'status': status,
            'assessment': assessment,
            'healthy_threshold_ma': 10,
            'dendrites_suspected': avg_current > 20
        }

    def test_voltage_drop_over_time(self, initial_voltage: float = None,
                                     duration_hours: int = 24) -> Dict:
        """
        Test voltage drop over time (self-discharge rate).

        After full charge, measure voltage decay over time.
        Expert recommendation: After 4 weeks, voltage should still be 12.7-12.8V

        "Hat sie nach 4 Wochen immer noch 12,7...12,8 V ist sie in Ordnung.
        Fällt die Spannung schneller, entladen die Dendriden die Batterie."

        Args:
            initial_voltage: Starting voltage (None = measure now)
            duration_hours: Test duration in hours (default 24h for quick test)

        Returns:
            Dictionary with self-discharge analysis
        """
        logger.info(f"Starting voltage drop test for {duration_hours} hours...")

        # Measure initial voltage
        self.psu.disable_output()
        time.sleep(5)

        if initial_voltage is None:
            initial_voltage = self.psu.measure_voltage()

        logger.info(f"Initial voltage: {initial_voltage:.3f}V")

        # Expected voltage targets (from expert's post)
        # Day 1-2: 13.0V
        # After weeks: 12.9-12.8V
        # After 4 weeks: 12.7-12.8V (healthy)

        expected_voltages = {
            1: 13.0,   # 1 hour (approximate)
            24: 12.95,  # 1 day
            168: 12.85, # 1 week
            672: 12.75  # 4 weeks
        }

        measurements = []
        start_time = time.time()

        # For practical testing, we'll sample every hour for duration_hours
        # In production, this would be called periodically
        logger.info(f"⚠️  For complete test, run this over {duration_hours} hours")
        logger.info(f"⚠️  Call this function periodically to track voltage decay")

        # Measure current voltage
        current_voltage = self.psu.measure_voltage()
        elapsed_hours = 0

        # Calculate expected drop rate
        # Healthy: ~0.2V over 4 weeks = 0.007V per day = 0.0003V per hour
        expected_drop_per_hour = 0.0003

        return {
            'initial_voltage': initial_voltage,
            'current_voltage': current_voltage,
            'elapsed_hours': elapsed_hours,
            'voltage_drop': initial_voltage - current_voltage,
            'expected_drop_per_hour': expected_drop_per_hour,
            'healthy_after_4_weeks': 12.7,  # Should be ≥12.7V after 4 weeks
            'assessment': 'Test requires extended monitoring (hours to weeks)',
            'recommendation': 'Measure voltage daily for 1 week to assess self-discharge rate'
        }

    def test_gassing_threshold(self, duration: int = 600) -> Dict:
        """
        Test gassing threshold voltage (determine when battery starts gassing).

        Some batteries start gassing early at 14.7V (poor condition),
        healthy modern batteries should only gas above 15.8V.

        Tom's observation: "Er stellte fest, dass die Batterie bereits ab
        14,7 V begann zu gasen."

        This test gradually increases voltage and monitors current to detect
        when gassing starts (current begins to rise despite voltage plateau).

        Args:
            duration: Test duration in seconds (default 10 minutes)

        Returns:
            Dictionary with gassing threshold analysis
        """
        logger.info("Testing gassing threshold voltage...")
        logger.warning("⚠️  ONLY for FLOODED batteries with OPEN valve caps!")
        logger.warning("⚠️  Ensure good ventilation - hydrogen gas!")

        # Start at safe voltage and increment
        start_voltage = 14.0
        max_voltage = 17.0
        voltage_step = 0.2
        step_duration = 60  # 1 minute per voltage step

        measurements = []
        current_voltage = start_voltage

        self.psu.set_current(5.0)  # Allow reasonable current
        self.psu.set_voltage(current_voltage)
        self.psu.enable_output()

        start_time = time.time()

        while current_voltage <= max_voltage and (time.time() - start_time) < duration:
            # Set voltage
            self.psu.set_voltage(current_voltage)
            logger.info(f"Testing at {current_voltage:.1f}V...")

            # Wait for stabilization
            time.sleep(10)

            # Measure current over step duration
            step_currents = []
            for i in range(5):  # 5 samples over 50 seconds
                current = self.psu.measure_current()
                voltage = self.psu.measure_voltage()
                step_currents.append(current)
                logger.info(f"  {voltage:.2f}V @ {current:.3f}A")
                if i < 4:
                    time.sleep(10)

            avg_current = sum(step_currents) / len(step_currents)
            measurements.append({
                'voltage': current_voltage,
                'avg_current': avg_current,
                'max_current': max(step_currents),
                'current_trend': 'rising' if len(measurements) > 0 and avg_current > measurements[-1]['avg_current'] * 1.2 else 'stable'
            })

            # Check if gassing detected (current rising despite voltage plateau)
            if len(measurements) >= 2:
                if measurements[-1]['current_trend'] == 'rising':
                    logger.info(f"🫧 Gassing detected at {current_voltage:.1f}V")
                    break

            current_voltage += voltage_step

        self.psu.disable_output()

        # Analyze results
        gassing_voltage = None
        for m in measurements:
            if m['current_trend'] == 'rising':
                gassing_voltage = m['voltage']
                break

        if gassing_voltage:
            if gassing_voltage < 15.0:
                assessment = "poor"
                status = "Battery starts gassing early - may be sulfated or degraded"
            elif gassing_voltage < 15.5:
                assessment = "fair"
                status = "Moderate gassing threshold - acceptable for older batteries"
            else:
                assessment = "good"
                status = "Healthy gassing threshold - battery in good condition"
        else:
            assessment = "unknown"
            status = "No clear gassing detected in test range"

        return {
            'measurements': measurements,
            'gassing_voltage': gassing_voltage,
            'assessment': assessment,
            'status': status,
            'healthy_threshold': 15.8,  # Healthy batteries gas above 15.8V
            'poor_threshold': 14.7,     # Poor batteries gas at 14.7V
            'test_duration_seconds': int(time.time() - start_time)
        }

    def test_internal_resistance(self, test_current: float = 1.0) -> Dict:
        """
        Measure battery internal resistance.

        Args:
            test_current: Test current in A (default 1A)

        Returns:
            Dictionary with resistance and health assessment
        """
        logger.info("Testing internal resistance...")

        # 1. Measure no-load voltage
        self.psu.disable_output()
        time.sleep(5)
        v_noload = self.psu.measure_voltage()
        logger.info(f"No-load voltage: {v_noload:.3f}V")

        # 2. Apply small discharge by setting voltage below battery
        # This makes the battery "push" current into the PSU input
        # (Actually this won't work - PSU can't sink current!)
        # Alternative: Brief high-current charge pulse

        logger.warning("Internal resistance test requires battery to be under load")
        logger.warning("Connect a known load (e.g. 1A bulb) and run test again")

        # For now, return estimated value based on battery age/condition
        return {
            'note': 'Requires external load for accurate measurement',
            'method': 'Connect 1A load, measure voltage drop',
            'formula': 'R = (V_noload - V_load) / I_load'
        }

    def test_voltage_recovery(self, charge_time: int = 60) -> Dict:
        """
        Test battery voltage recovery after brief charge.
        Good batteries recover voltage quickly.

        Args:
            charge_time: Brief charge duration (seconds)

        Returns:
            Dictionary with recovery characteristics
        """
        logger.info("Testing voltage recovery...")

        # 1. Measure initial voltage
        self.psu.disable_output()
        time.sleep(10)
        v_initial = self.psu.measure_voltage()

        # 2. Brief charge
        self.psu.set_voltage(14.4)
        self.psu.set_current(2.0)
        self.psu.enable_output()
        time.sleep(charge_time)
        v_charging = self.psu.measure_voltage()

        # 3. Disable and measure recovery
        self.psu.disable_output()

        recovery_times = [1, 5, 10, 30, 60]  # seconds
        voltages = []

        for t in recovery_times:
            time.sleep(t if len(voltages) == 0 else (t - recovery_times[len(voltages)-1]))
            v = self.psu.measure_voltage()
            voltages.append(v)
            logger.info(f"After {t}s: {v:.3f}V")

        # Calculate recovery characteristics
        voltage_drop = v_charging - voltages[0]
        recovery_1s = v_charging - voltages[0]
        recovery_60s = v_charging - voltages[-1]

        # Good battery: quick voltage rise, slow decay
        # Bad battery: slow voltage rise, fast decay

        return {
            'v_initial': v_initial,
            'v_charging': v_charging,
            'v_1s': voltages[0],
            'v_5s': voltages[1],
            'v_60s': voltages[-1],
            'voltage_drop_1s': recovery_1s,
            'voltage_drop_60s': recovery_60s,
            'assessment': 'good' if recovery_60s < 0.5 else 'fair' if recovery_60s < 1.0 else 'poor'
        }

    def comprehensive_test(self) -> Dict:
        """
        Run comprehensive battery diagnostic test.

        Returns:
            Complete diagnostic report
        """
        logger.info("=" * 60)
        logger.info("Starting comprehensive battery diagnostics")
        logger.info("=" * 60)

        results = {}

        # 1. Resting voltage test
        try:
            v_rest = self.test_resting_voltage(rest_time=60)
            results['resting_voltage'] = v_rest
            results['soc_estimate'] = self.estimate_state_of_charge(v_rest)
        except Exception as e:
            logger.error(f"Resting voltage test failed: {e}")
            results['resting_voltage'] = None

        # 2. Voltage recovery test
        try:
            results['voltage_recovery'] = self.test_voltage_recovery()
        except Exception as e:
            logger.error(f"Voltage recovery test failed: {e}")
            results['voltage_recovery'] = None

        # 3. Internal resistance (informational only)
        results['internal_resistance'] = self.test_internal_resistance()

        logger.info("=" * 60)
        logger.info("Diagnostic tests complete")
        logger.info("=" * 60)

        return results

    def print_report(self, results: Dict):
        """Print human-readable diagnostic report."""
        print("\n" + "=" * 60)
        print("BATTERY DIAGNOSTIC REPORT")
        print("=" * 60)

        if results.get('resting_voltage'):
            print(f"\n1. RESTING VOLTAGE: {results['resting_voltage']:.3f}V")

            soc = results.get('soc_estimate', {})
            print(f"   State of Charge: ~{soc.get('soc_percent', 0)}%")
            print(f"   Status: {soc.get('status', 'unknown').upper()}")

            if soc.get('voltage', 0) < 12.5:
                print("   ⚠️  WARNING: Voltage below 12.5V - recharge immediately!")

        if results.get('voltage_recovery'):
            rec = results['voltage_recovery']
            print(f"\n2. VOLTAGE RECOVERY TEST:")
            print(f"   Initial: {rec['v_initial']:.3f}V")
            print(f"   During charge: {rec['v_charging']:.3f}V")
            print(f"   After 1s: {rec['v_1s']:.3f}V")
            print(f"   After 60s: {rec['v_60s']:.3f}V")
            print(f"   Assessment: {rec['assessment'].upper()}")

        if results.get('internal_resistance'):
            ir = results['internal_resistance']
            print(f"\n3. INTERNAL RESISTANCE:")
            print(f"   {ir.get('note', 'Not measured')}")

        print("\n" + "=" * 60)
        print("RECOMMENDATIONS:")
        print("=" * 60)

        # Generate recommendations based on results
        if results.get('soc_estimate', {}).get('voltage', 0) < 12.5:
            print("❌ URGENT: Battery needs immediate charging (< 12.5V)")
        elif results.get('soc_estimate', {}).get('soc_percent', 0) < 50:
            print("⚠️  Battery should be charged soon (< 50% SOC)")
        else:
            print("✓ Battery voltage is acceptable")

        if results.get('voltage_recovery', {}).get('assessment') == 'poor':
            print("⚠️  Poor voltage recovery - battery may be sulfated or aged")
            print("   → Try Pulse charging mode for recovery")
        elif results.get('voltage_recovery', {}).get('assessment') == 'good':
            print("✓ Good voltage recovery - battery health appears good")

        print("\nFor full capacity test, an external load is required.")
        print("=" * 60 + "\n")


# CLI interface
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')

    from owon_psu import OwonPSU

    print("Battery Diagnostics Tool")
    print("Connecting to OWON PSU...")

    psu = OwonPSU('/dev/ttyUSB0')
    if not psu.connect():
        print("Failed to connect to PSU")
        sys.exit(1)

    print("Connected successfully!")
    print()

    # Run diagnostics
    diag = BatteryDiagnostics(psu)
    results = diag.comprehensive_test()

    # Print report
    diag.print_report(results)

    # Cleanup
    psu.disconnect()
