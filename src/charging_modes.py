"""
Charging mode implementations for battery charger.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Optional
from owon_psu import OwonPSU

logger = logging.getLogger(__name__)


class ChargingMode(ABC):
    """Base class for charging modes."""

    def __init__(self, psu: OwonPSU, config: dict):
        """
        Initialize charging mode.

        Args:
            psu: OWON PSU instance
            config: Mode-specific configuration dictionary
        """
        self.psu = psu
        self.config = config
        self.start_time = 0.0
        self.state = "idle"  # idle, charging, completed, error

    def start(self) -> bool:
        """
        Start charging mode.

        Returns:
            True if started successfully
        """
        self.start_time = time.time()
        self.state = "charging"
        logger.info(f"Starting {self.config.get('name', 'unknown')} mode")
        return True

    def stop(self):
        """Stop charging mode."""
        try:
            self.psu.set_output(False)
            self.state = "stopped"
            self._update_display("STOPPED")
            logger.info("Charging stopped")
        except Exception as e:
            logger.error(f"Error stopping charging: {e}")

    def _update_display(self, text: str):
        """
        Update PSU display with status text.

        Args:
            text: Text to display (max ~16 chars depending on PSU model)
        """
        try:
            self.psu.set_display_text(text[:16])  # Limit length
        except Exception as e:
            # Don't fail charging if display update fails
            logger.debug(f"Failed to update display: {e}")

    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time == 0:
            return 0.0
        return time.time() - self.start_time

    @abstractmethod
    def update(self) -> dict:
        """
        Update charging logic. Called periodically.

        Returns:
            Status dictionary with voltage, current, state, etc.
        """
        pass

    def get_status(self) -> dict:
        """Get current status information."""
        return {
            'mode': self.config.get('name', 'unknown'),
            'state': self.state,
            'elapsed': self.get_elapsed_time()
        }


class IUoUMode(ChargingMode):
    """
    IUoU (3-stage) charging mode.

    Stages:
    1. Bulk (I): Constant current until absorption voltage reached
    2. Absorption (Uo): Hold absorption voltage until current drops
    3. Float (U): Hold float voltage for maintenance
    """

    def __init__(self, psu: OwonPSU, config: dict):
        super().__init__(psu, config)
        self.stage = "bulk"  # bulk, absorption, float
        self.absorption_start_time = 0.0

    def start(self) -> bool:
        """Start IUoU charging."""
        if not super().start():
            return False

        self.stage = "bulk"
        self.absorption_start_time = 0.0

        try:
            # Configure for bulk stage (constant current)
            bulk_current = self.config.get('bulk_current', 5.0)
            absorption_voltage = self.config.get('absorption_voltage', 14.4)

            self.psu.set_current(bulk_current)
            self.psu.set_voltage(absorption_voltage)
            self.psu.set_output(True)
            self._update_display(f"BULK {bulk_current:.1f}A")

            logger.info(f"IUoU Bulk stage: {bulk_current}A until {absorption_voltage}V")
            return True

        except Exception as e:
            logger.error(f"Failed to start IUoU mode: {e}")
            self.state = "error"
            return False

    def update(self) -> dict:
        """Update IUoU charging logic."""
        try:
            voltage = self.psu.measure_voltage()
            current = self.psu.measure_current()
            power = self.psu.measure_power()

            # State machine for 3-stage charging
            if self.stage == "bulk":
                self._update_bulk_stage(voltage)

            elif self.stage == "absorption":
                self._update_absorption_stage(current)

            elif self.stage == "float":
                # Float stage runs indefinitely or until manually stopped
                pass

            status = self.get_status()
            status.update({
                'voltage': voltage,
                'current': current,
                'power': power,
                'stage': self.stage,
                'bulk_current': self.config.get('bulk_current', 5.0),
                'absorption_voltage': self.config.get('absorption_voltage', 14.4),
                'float_voltage': self.config.get('float_voltage', 13.6)
            })

            return status

        except Exception as e:
            logger.error(f"Error in IUoU update: {e}")
            self.state = "error"
            return self.get_status()

    def _update_bulk_stage(self, voltage: float):
        """Check transition from bulk to absorption."""
        absorption_voltage = self.config.get('absorption_voltage', 14.4)

        if voltage >= absorption_voltage - 0.1:
            logger.info(f"Transitioning to absorption stage at {voltage:.2f}V")
            self.stage = "absorption"
            self.absorption_start_time = time.time()
            self._update_display(f"ABS {absorption_voltage:.1f}V")
            # Voltage already set, just maintain it

    def _update_absorption_stage(self, current: float):
        """Check transition from absorption to float."""
        threshold = self.config.get('absorption_current_threshold', 1.0)
        timeout = self.config.get('absorption_timeout', 7200)
        absorption_time = time.time() - self.absorption_start_time

        # Check if current dropped below threshold or timeout
        if current < threshold:
            logger.info(f"Current dropped to {current:.2f}A, entering float stage")
            self._enter_float_stage()
        elif absorption_time > timeout:
            logger.warning(f"Absorption timeout ({timeout}s), entering float stage")
            self._enter_float_stage()

    def _enter_float_stage(self):
        """Transition to float stage."""
        if not self.config.get('enable_float', True):
            logger.info("Float stage disabled, marking as completed")
            self.state = "completed"
            self.psu.set_output(False)
            self._update_display("COMPLETE")
            return

        float_voltage = self.config.get('float_voltage', 13.6)
        self.stage = "float"
        self.psu.set_voltage(float_voltage)
        self._update_display(f"FLOAT {float_voltage:.1f}V")
        logger.info(f"Float stage: maintaining {float_voltage}V")


class ConstantVoltageMode(ChargingMode):
    """Constant Voltage (CV) charging mode."""

    def start(self) -> bool:
        """Start CV charging."""
        if not super().start():
            return False

        try:
            voltage = self.config.get('voltage', 13.8)
            max_current = self.config.get('max_current', 5.0)

            self.psu.set_voltage(voltage)
            self.psu.set_current(max_current)
            self.psu.set_output(True)
            self._update_display(f"CV {voltage:.1f}V")

            logger.info(f"CV mode: {voltage}V, max {max_current}A")
            return True

        except Exception as e:
            logger.error(f"Failed to start CV mode: {e}")
            self.state = "error"
            return False

    def update(self) -> dict:
        """Update CV charging logic."""
        try:
            voltage = self.psu.measure_voltage()
            current = self.psu.measure_current()
            power = self.psu.measure_power()

            # Check if charging complete (current dropped below threshold)
            min_current = self.config.get('min_current', 0.5)
            if current < min_current:
                logger.info(f"Current dropped to {current:.2f}A, charging complete")
                self.state = "completed"

            status = self.get_status()
            status.update({
                'voltage': voltage,
                'current': current,
                'power': power,
                'target_voltage': self.config.get('voltage', 13.8),
                'min_current': min_current
            })

            return status

        except Exception as e:
            logger.error(f"Error in CV update: {e}")
            self.state = "error"
            return self.get_status()


class PulseChargingMode(ChargingMode):
    """
    Pulse charging mode for desulfation and recovery.

    Alternates between high-voltage pulse and rest periods.
    """

    def __init__(self, psu: OwonPSU, config: dict):
        super().__init__(psu, config)
        self.cycle_count = 0
        self.phase = "pulse"  # pulse or rest
        self.phase_start_time = 0.0

    def start(self) -> bool:
        """Start pulse charging."""
        if not super().start():
            return False

        self.cycle_count = 0
        self.phase = "pulse"
        self.phase_start_time = time.time()

        try:
            self._enter_pulse_phase()
            return True
        except Exception as e:
            logger.error(f"Failed to start pulse mode: {e}")
            self.state = "error"
            return False

    def update(self) -> dict:
        """Update pulse charging logic."""
        try:
            voltage = self.psu.measure_voltage()
            current = self.psu.measure_current()
            power = self.psu.measure_power()

            phase_elapsed = time.time() - self.phase_start_time

            # Check phase transitions
            if self.phase == "pulse":
                pulse_duration = self.config.get('pulse_duration', 30)
                if phase_elapsed >= pulse_duration:
                    self._enter_rest_phase()

            elif self.phase == "rest":
                rest_duration = self.config.get('rest_duration', 30)
                if phase_elapsed >= rest_duration:
                    self.cycle_count += 1
                    max_cycles = self.config.get('max_cycles', 20)

                    if self.cycle_count >= max_cycles:
                        logger.info(f"Completed {max_cycles} pulse cycles")
                        self.state = "completed"
                        self.psu.set_output(False)
                    else:
                        self._enter_pulse_phase()

            status = self.get_status()
            status.update({
                'voltage': voltage,
                'current': current,
                'power': power,
                'phase': self.phase,
                'cycle': self.cycle_count,
                'max_cycles': self.config.get('max_cycles', 20),
                'phase_elapsed': phase_elapsed
            })

            return status

        except Exception as e:
            logger.error(f"Error in pulse update: {e}")
            self.state = "error"
            return self.get_status()

    def _enter_pulse_phase(self):
        """Enter pulse phase (high voltage/current)."""
        self.phase = "pulse"
        self.phase_start_time = time.time()

        pulse_voltage = self.config.get('pulse_voltage', 15.5)
        pulse_current = self.config.get('pulse_current', 5.0)

        self.psu.set_voltage(pulse_voltage)
        self.psu.set_current(pulse_current)
        self.psu.set_output(True)

        logger.debug(f"Pulse phase: {pulse_voltage}V, {pulse_current}A")

    def _enter_rest_phase(self):
        """Enter rest phase (low voltage, minimal current)."""
        self.phase = "rest"
        self.phase_start_time = time.time()

        rest_voltage = self.config.get('rest_voltage', 13.0)
        self.psu.set_voltage(rest_voltage)
        self.psu.set_current(0.1)  # Very low current during rest

        logger.debug(f"Rest phase: {rest_voltage}V")


class TrickleChargeMode(ChargingMode):
    """Trickle charge maintenance mode."""

    def start(self) -> bool:
        """Start trickle charging."""
        if not super().start():
            return False

        try:
            voltage = self.config.get('voltage', 13.5)
            current = self.config.get('current', 0.5)

            self.psu.set_voltage(voltage)
            self.psu.set_current(current)
            self.psu.set_output(True)

            logger.info(f"Trickle mode: {voltage}V, {current}A")
            return True

        except Exception as e:
            logger.error(f"Failed to start trickle mode: {e}")
            self.state = "error"
            return False

    def update(self) -> dict:
        """Update trickle charging logic."""
        try:
            voltage = self.psu.measure_voltage()
            current = self.psu.measure_current()
            power = self.psu.measure_power()

            status = self.get_status()
            status.update({
                'voltage': voltage,
                'current': current,
                'power': power,
                'target_voltage': self.config.get('voltage', 13.5),
                'target_current': self.config.get('current', 0.5)
            })

            return status

        except Exception as e:
            logger.error(f"Error in trickle update: {e}")
            self.state = "error"
            return self.get_status()


class ConstantCurrentMode(ChargingMode):
    """
    Pure Constant Current (CC) charging mode.

    The traditional 150-year-old method recommended by experts for open batteries.
    Uses constant current with voltage plateau detection to determine full charge.

    Expert quote: "Die Stromladung ist die schnellste und sicherste Methode
    eine Batterie aufzuladen. Das wurde 150 Jahre lang so gemacht."

    Method:
    1. Apply 10% of capacity (C/10) until gassing starts or voltage plateaus
    2. Optionally reduce to 5% (C/20) for final topping
    3. Monitor voltage every 2 hours - when it stops rising or drops, battery is full
    4. Battery reaches 17-17.5V (new) or 16V (older)
    """

    def __init__(self, psu: OwonPSU, config: dict):
        """Initialize Constant Current mode."""
        super().__init__(psu, config)


class ConditioningMode(ChargingMode):
    """
    Extended High-Voltage Conditioning Mode (Tom's Method).

    Applies sustained high voltage (15.4-15.6V) for 24-48 hours to condition
    the battery beyond normal charging. Results in elevated resting voltage
    and improved charge retention.

    Source: Microcharge forum thread on high-voltage charging
    https://www.microcharge.de/forum/forum/thread/847-hochspannungsladung-von-bleiakkus

    Benefits observed:
    - Resting voltage increases from 12.6V → 13.3V
    - Better charge retention over weeks
    - Improved starting power
    - Possible sulfation reversal

    Warnings:
    - Only for open/flooded batteries with valve caps removed
    - Monitor for excessive gassing (water electrolysis vs charging)
    - Check water level after treatment
    - Not suitable for sealed/AGM batteries
    """

    def __init__(self, psu: OwonPSU, config: dict):
        """Initialize Conditioning mode."""
        super().__init__(psu, config)
        self.phase = "conditioning"
        self.high_current_start = 0  # Track sustained high current

    def start(self) -> bool:
        """Start conditioning mode."""
        try:
            voltage = self.config.get('voltage', 15.5)
            max_current = self.config.get('max_current', 4.4)
            duration = self.config.get('duration', 86400)  # 24 hours default

            logger.info(f"Starting Conditioning mode (Tom's Method)")
            logger.info(f"Voltage: {voltage}V, Max current: {max_current}A")
            logger.info(f"Duration: {duration/3600:.1f} hours")
            logger.warning("⚠️  Only for OPEN batteries - remove valve caps!")
            logger.warning("⚠️  Monitor for excessive gassing (water loss)")

            # Set voltage and current
            self.psu.set_voltage(voltage)
            self.psu.set_current(max_current)
            self.psu.set_output(True)
            self._update_display(f"COND {voltage:.1f}V")

            self.state = "charging"
            self.start_time = time.time()

            logger.info("Conditioning started - monitor current for electrolysis detection")

            return True

        except Exception as e:
            logger.error(f"Failed to start Conditioning mode: {e}")
            self.state = "error"
            return False

    def update(self) -> dict:
        """Update conditioning mode logic."""
        try:
            voltage = self.psu.measure_voltage()
            current = self.psu.measure_current()
            power = self.psu.measure_power()

            elapsed = self.get_elapsed_time()
            duration = self.config.get('duration', 86400)

            # Monitor for sustained high current (electrolysis warning)
            # During normal conditioning, current should drop as battery charges
            # Sustained high current = water electrolysis, not charging
            if current > 1.0:  # > 1A after initial phase
                if self.high_current_start == 0:
                    self.high_current_start = time.time()
                elif time.time() - self.high_current_start > 3600:  # 1 hour
                    logger.warning(
                        f"⚠️  Sustained high current ({current:.2f}A) for >1h "
                        f"- likely water electrolysis, not charging!"
                    )
            else:
                self.high_current_start = 0  # Reset

            # Check if duration reached
            if elapsed >= duration:
                logger.info(f"Conditioning duration ({duration/3600:.1f}h) complete")
                self.state = "completed"
                self.psu.set_output(False)
                self._update_display("COND DONE")

            status = self.get_status()
            status.update({
                'voltage': voltage,
                'current': current,
                'power': power,
                'phase': self.phase,
                'target_voltage': self.config.get('voltage', 15.5),
                'duration': duration,
                'elapsed': elapsed,
                'progress': min(100, int(elapsed / duration * 100)),
                'electrolysis_warning': (time.time() - self.high_current_start > 3600) if self.high_current_start > 0 else False
            })

            return status

        except Exception as e:
            logger.error(f"Error in Conditioning update: {e}")
            self.state = "error"
            return self.get_status()


class ConstantCurrentMode(ChargingMode):
    """
    Pure Constant Current (CC) charging mode.

    The traditional 150-year-old method recommended by experts for open batteries.
    Uses constant current with voltage plateau detection to determine full charge.

    Expert quote: "Die Stromladung ist die schnellste und sicherste Methode
    eine Batterie aufzuladen. Das wurde 150 Jahre lang so gemacht."

    Method:
    1. Apply 10% of capacity (C/10) until gassing starts or voltage plateaus
    2. Optionally reduce to 5% (C/20) for final topping
    3. Monitor voltage every 2 hours - when it stops rising or drops, battery is full
    4. Battery reaches 17-17.5V (new) or 16V (older)
    """

    def __init__(self, psu: OwonPSU, config: dict):
        """Initialize Constant Current mode."""
        super().__init__(psu, config)

    def start(self) -> bool:
        """Start constant current charging."""
        try:
            current = self.config.get('current', 4.4)
            max_voltage = self.config.get('max_voltage', 18.0)  # Safety limit only

            logger.info(f"Starting Constant Current mode: {current}A")
            logger.info(f"Safety voltage limit: {max_voltage}V")
            logger.info("Battery will charge with constant current until voltage plateaus")

            # Set current and high voltage limit (safety only)
            self.psu.set_current(current)
            self.psu.set_voltage(max_voltage)
            self.psu.set_output(True)

            self.state = "charging"
            self.start_time = time.time()

            logger.info("Constant Current charging started")
            logger.info("Monitor for voltage plateau - charging complete when voltage stops rising")

            return True

        except Exception as e:
            logger.error(f"Failed to start Constant Current mode: {e}")
            self.state = "error"
            return False

    def update(self) -> dict:
        """Update constant current charging logic."""
        try:
            voltage = self.psu.measure_voltage()
            current = self.psu.measure_current()
            power = self.psu.measure_power()

            # Pure constant current - just measure and report
            # Plateau detection is handled by safety_monitor in main loop

            status = self.get_status()
            status.update({
                'voltage': voltage,
                'current': current,
                'power': power,
                'target_current': self.config.get('current', 4.4),
                'max_voltage': self.config.get('max_voltage', 18.0),
                'charging_method': 'constant_current'
            })

            return status

        except Exception as e:
            logger.error(f"Error in Constant Current update: {e}")
            self.state = "error"
            return self.get_status()


# Mode factory
def create_charging_mode(mode_name: str, psu: OwonPSU, config: dict) -> ChargingMode:
    """
    Factory function to create charging mode instance.

    Args:
        mode_name: Name of mode (IUoU, CV, Pulse, Trickle)
        psu: OWON PSU instance
        config: Mode configuration dictionary

    Returns:
        ChargingMode instance
    """
    modes = {
        'IUoU': IUoUMode,
        'CV': ConstantVoltageMode,
        'CC': ConstantCurrentMode,
        'Conditioning': ConditioningMode,
        'Pulse': PulseChargingMode,
        'Trickle': TrickleChargeMode
    }

    mode_class = modes.get(mode_name)
    if not mode_class:
        raise ValueError(f"Unknown charging mode: {mode_name}")

    # Add name to config
    config['name'] = mode_name

    return mode_class(psu, config)
