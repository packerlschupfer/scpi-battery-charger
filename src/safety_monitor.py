"""
Safety monitoring for battery charger.
"""

import time
import logging
from typing import Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SafetyLimits:
    """Safety limit configuration."""
    absolute_max_voltage: float
    absolute_max_current: float
    min_voltage: float
    warning_voltage: float  # Warning threshold (12.5V per German battery guide)
    max_charging_duration: float
    max_temperature: Optional[float] = None
    min_temperature: Optional[float] = None
    # Plateau detection settings (for high-voltage flooded battery charging)
    plateau_enabled: bool = True
    plateau_threshold_voltage: float = 16.0  # V - Start monitoring above this
    plateau_time_window: float = 900  # seconds (15 minutes)
    plateau_voltage_delta: float = 0.05  # V - Max change to consider plateau
    # Energy accounting
    charging_efficiency: float = 0.83  # Lead-acid efficiency (1/1.2 = 83%)


class SafetyMonitor:
    """Monitor charging process for safety violations."""

    def __init__(self, limits: SafetyLimits):
        """
        Initialize safety monitor.

        Args:
            limits: Safety limits configuration
        """
        self.limits = limits
        self.violations = []
        self.start_time = 0.0
        self.last_check_time = 0.0
        self.warning_count = 0

        # Voltage plateau detection (for high-voltage charging >16V)
        # Load settings from config via limits dataclass
        self.voltage_history = []  # List of (timestamp, voltage) tuples
        self.plateau_enabled = limits.plateau_enabled
        self.plateau_threshold_voltage = limits.plateau_threshold_voltage
        self.plateau_time_window = limits.plateau_time_window
        self.plateau_voltage_delta = limits.plateau_voltage_delta

        # Energy accounting (Coulomb counting)
        self.ah_delivered = 0.0  # Ah from PSU
        self.wh_delivered = 0.0  # Wh from PSU
        self.last_energy_update = 0.0  # Timestamp of last update
        self.charging_efficiency = limits.charging_efficiency

    def start_monitoring(self):
        """Start safety monitoring."""
        self.start_time = time.time()
        self.last_check_time = time.time()
        self.violations = []
        self.warning_count = 0
        self.voltage_history = []  # Clear voltage history

        # Reset energy accounting
        self.ah_delivered = 0.0
        self.wh_delivered = 0.0
        self.last_energy_update = time.time()

        logger.info("Safety monitoring started")

    def stop_monitoring(self):
        """Stop safety monitoring."""
        logger.info("Safety monitoring stopped")

    def check_safety(
        self,
        voltage: float,
        current: float,
        temperature: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Check all safety conditions.

        Args:
            voltage: Current voltage in V
            current: Current current in A
            temperature: Optional battery temperature in °C

        Returns:
            Dictionary with safety status:
            {
                'safe': bool,
                'violations': list of violation messages,
                'warnings': list of warning messages,
                'should_stop': bool
            }
        """
        self.last_check_time = time.time()
        violations = []
        warnings = []
        should_stop = False

        # Check voltage limits
        if voltage > self.limits.absolute_max_voltage:
            msg = f"CRITICAL: Voltage {voltage:.2f}V exceeds maximum {self.limits.absolute_max_voltage}V"
            violations.append(msg)
            logger.error(msg)
            should_stop = True

        if voltage < self.limits.min_voltage:
            msg = f"WARNING: Voltage {voltage:.2f}V below minimum {self.limits.min_voltage}V"
            warnings.append(msg)
            logger.warning(msg)

        # Check warning voltage threshold (12.5V - immediate recharge recommended)
        if voltage < self.limits.warning_voltage and voltage >= self.limits.min_voltage:
            msg = f"⚠️  RECHARGE RECOMMENDED: Voltage {voltage:.2f}V below {self.limits.warning_voltage}V (risk of permanent damage)"
            warnings.append(msg)
            logger.warning(msg)

        # Check current limits
        if current > self.limits.absolute_max_current:
            msg = f"CRITICAL: Current {current:.2f}A exceeds maximum {self.limits.absolute_max_current}A"
            violations.append(msg)
            logger.error(msg)
            should_stop = True

        # Check charging duration
        elapsed = self.get_elapsed_time()
        if elapsed > self.limits.max_charging_duration:
            msg = f"CRITICAL: Charging duration {elapsed:.0f}s exceeds maximum {self.limits.max_charging_duration}s"
            violations.append(msg)
            logger.error(msg)
            should_stop = True

        # Check temperature limits if available
        if temperature is not None:
            if self.limits.max_temperature and temperature > self.limits.max_temperature:
                msg = f"CRITICAL: Temperature {temperature:.1f}°C exceeds maximum {self.limits.max_temperature}°C"
                violations.append(msg)
                logger.error(msg)
                should_stop = True

            if self.limits.min_temperature and temperature < self.limits.min_temperature:
                msg = f"WARNING: Temperature {temperature:.1f}°C below minimum {self.limits.min_temperature}°C"
                warnings.append(msg)
                logger.warning(msg)

        # Store violations
        if violations:
            self.violations.extend(violations)
            self.warning_count += 1

        return {
            'safe': len(violations) == 0,
            'violations': violations,
            'warnings': warnings,
            'should_stop': should_stop,
            'elapsed_time': elapsed
        }

    def get_elapsed_time(self) -> float:
        """Get elapsed time since monitoring started."""
        if self.start_time == 0:
            return 0.0
        return time.time() - self.start_time

    def check_voltage_plateau(self, voltage: float) -> dict:
        """
        Check if battery voltage has plateaued (stopped rising).

        For flooded batteries charged above 16V, the voltage should be
        monitored. If it stops rising, the battery is fully charged.

        Args:
            voltage: Current battery voltage in V

        Returns:
            Dictionary with plateau status:
            {
                'is_plateau': bool,
                'monitoring': bool,  # True if voltage > threshold
                'time_at_high_voltage': float,  # seconds above threshold
                'voltage_rise': float  # V change over time window
            }
        """
        # Check if plateau detection is enabled
        logger.debug(f"check_voltage_plateau called: voltage={voltage:.3f}V, enabled={self.plateau_enabled}, threshold={self.plateau_threshold_voltage}V")

        if not self.plateau_enabled:
            logger.debug("Plateau detection disabled")
            return {
                'is_plateau': False,
                'monitoring': False,
                'time_at_high_voltage': 0.0,
                'voltage_rise': 0.0
            }

        now = time.time()

        # Only monitor above threshold voltage (16V for flooded batteries)
        if voltage < self.plateau_threshold_voltage:
            logger.debug(f"Voltage {voltage:.3f}V below threshold {self.plateau_threshold_voltage}V")
            return {
                'is_plateau': False,
                'monitoring': False,
                'time_at_high_voltage': 0.0,
                'voltage_rise': 0.0
            }

        # Record voltage in history
        self.voltage_history.append((now, voltage))

        # Keep only recent history (within time window)
        cutoff_time = now - self.plateau_time_window
        self.voltage_history = [(t, v) for t, v in self.voltage_history if t >= cutoff_time]

        # Need at least 2 data points spanning the time window
        if len(self.voltage_history) < 2:
            time_at_high = now - self.voltage_history[0][0] if self.voltage_history else 0.0
            return {
                'is_plateau': False,
                'monitoring': True,
                'time_at_high_voltage': time_at_high,
                'voltage_rise': 0.0
            }

        # Check if we have enough data spanning the full time window
        oldest_time = self.voltage_history[0][0]
        time_span = now - oldest_time

        if time_span < self.plateau_time_window:
            logger.debug(
                f"Plateau monitoring: {voltage:.3f}V, data span {time_span:.0f}s / {self.plateau_time_window:.0f}s "
                f"({len(self.voltage_history)} points)"
            )
            return {
                'is_plateau': False,
                'monitoring': True,
                'time_at_high_voltage': time_span,
                'voltage_rise': 0.0
            }

        # Calculate voltage rise over the time window
        oldest_voltage = self.voltage_history[0][1]
        newest_voltage = self.voltage_history[-1][1]
        voltage_rise = newest_voltage - oldest_voltage

        # Check for plateau
        is_plateau = abs(voltage_rise) <= self.plateau_voltage_delta

        # Log plateau check results
        logger.info(
            f"Plateau check: {voltage:.3f}V, rise {voltage_rise:.3f}V over {time_span/60:.1f}min "
            f"(threshold {self.plateau_voltage_delta}V, window {self.plateau_time_window/60:.0f}min) "
            f"→ {'PLATEAU!' if is_plateau else 'still rising'}"
        )

        if is_plateau:
            logger.warning(
                f"⚠️  VOLTAGE PLATEAU DETECTED: {voltage:.3f}V "
                f"(rise {voltage_rise:.3f}V over {time_span/60:.1f} min)"
            )

        return {
            'is_plateau': is_plateau,
            'monitoring': True,
            'time_at_high_voltage': time_span,
            'voltage_rise': voltage_rise
        }

    def update_energy_accounting(self, current: float, power: float) -> dict:
        """
        Update energy accounting (Coulomb counting).

        Integrates current and power over time to calculate:
        - Ah delivered from PSU
        - Wh delivered from PSU
        - Ah stored in battery (accounting for efficiency)

        Args:
            current: Current in A
            power: Power in W

        Returns:
            Dictionary with energy accounting data
        """
        now = time.time()

        # Skip first update (no previous timestamp)
        if self.last_energy_update == 0:
            self.last_energy_update = now
            return self.get_energy_accounting()

        # Calculate time delta
        dt_seconds = now - self.last_energy_update
        dt_hours = dt_seconds / 3600.0

        # Integrate current → Ah delivered
        # Ah = ∫ I dt  (where dt is in hours)
        self.ah_delivered += current * dt_hours

        # Integrate power → Wh delivered
        # Wh = ∫ P dt  (where dt is in hours)
        self.wh_delivered += power * dt_hours

        # Update timestamp
        self.last_energy_update = now

        return self.get_energy_accounting()

    def get_energy_accounting(self) -> dict:
        """
        Get current energy accounting values.

        Returns:
            Dictionary with:
            - ah_delivered: Ah from PSU
            - wh_delivered: Wh from PSU
            - ah_stored: Ah stored in battery (accounting for efficiency)
            - efficiency: Charging efficiency factor
        """
        ah_stored = self.ah_delivered * self.charging_efficiency

        return {
            'ah_delivered': self.ah_delivered,
            'wh_delivered': self.wh_delivered,
            'ah_stored': ah_stored,
            'efficiency': self.charging_efficiency
        }

    def estimate_progress(
        self,
        mode: str,
        stage: Optional[str] = None,
        current: float = 0.0,
        voltage: float = 0.0,
        target_voltage: float = 0.0,
        absorption_current_threshold: float = 1.0
    ) -> float:
        """
        Estimate charging progress as percentage.

        Args:
            mode: Charging mode name
            stage: Current stage (for IUoU mode)
            current: Current current in A
            voltage: Current voltage in V
            target_voltage: Target voltage in V
            absorption_current_threshold: Threshold current for IUoU

        Returns:
            Progress percentage (0-100)
        """
        if mode == "IUoU":
            # 3-stage: Bulk 0-70%, Absorption 70-95%, Float 100%
            # Improved for smoother transitions and more realistic progression
            if stage == "bulk":
                # Progress based on voltage approaching target
                if target_voltage > 0:
                    voltage_progress = min(voltage / target_voltage, 1.0)
                    return voltage_progress * 70.0
                return 0.0

            elif stage == "absorption":
                # Progress based on current taper
                # Typical range: bulk_current (e.g., 4.4A) → threshold (e.g., 0.44A)
                # Use threshold * 10 as realistic starting point
                if absorption_current_threshold > 0:
                    max_current = absorption_current_threshold * 10.0
                    current_progress = 1.0 - min(current / max_current, 1.0)
                    return 70.0 + (current_progress * 25.0)
                return 70.0

            elif stage == "float":
                return 100.0

            return 0.0

        elif mode == "CV":
            # Constant voltage: estimate based on current taper
            # Assume starts at ~5A and drops to ~0.5A
            if current > 0.5:
                progress = 1.0 - ((current - 0.5) / 4.5)
                return min(max(progress * 100.0, 0.0), 100.0)
            return 100.0

        elif mode == "Pulse":
            # Pulse mode: based on elapsed time and max duration
            # Typically completes in fixed time
            max_duration = self.limits.max_charging_duration
            elapsed = self.get_elapsed_time()
            return min((elapsed / max_duration) * 100.0, 100.0)

        elif mode == "Trickle":
            # Trickle is maintenance - no real "completion"
            return 50.0  # Always show 50% as it's maintenance

        return 0.0

    def get_status(self) -> dict:
        """
        Get safety monitor status.

        Returns:
            Status dictionary
        """
        return {
            'monitoring': self.start_time > 0,
            'elapsed_time': self.get_elapsed_time(),
            'violation_count': len(self.violations),
            'violations': self.violations[-10:],  # Last 10 violations
            'warning_count': self.warning_count
        }

    def is_charging_complete(
        self,
        mode: str,
        current: float,
        state: str,
        min_current: float = 0.5
    ) -> bool:
        """
        Check if charging should be considered complete.

        Args:
            mode: Charging mode
            current: Current current in A
            state: Charging state
            min_current: Minimum current threshold

        Returns:
            True if charging is complete
        """
        # Check if mode reports completion
        if state == "completed":
            return True

        # CV mode: current dropped below threshold
        if mode == "CV" and current < min_current:
            return True

        # IUoU mode: only complete if in float stage or explicitly completed
        if mode == "IUoU" and state == "completed":
            return True

        return False
