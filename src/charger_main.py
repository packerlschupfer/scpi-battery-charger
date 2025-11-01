#!/usr/bin/env python3
"""
Battery Charger Main Application
Raspberry Pi + OWON SPE6205 + MQTT
"""

import sys
import os
import signal
import time
import logging
import argparse
import yaml
import csv
import atexit
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from owon_psu import OwonPSU
from charging_modes import create_charging_mode, ChargingMode
from safety_monitor import SafetyMonitor, SafetyLimits
from mqtt_client import ChargerMQTTClient
from battery_profiles import BatteryProfileManager
from charge_scheduler import ChargeScheduler
from error_recovery import ErrorRecoveryManager
from battery_history import BatteryHistoryTracker

logger = logging.getLogger(__name__)

# Optional temperature sensor support
try:
    from temperature_sensor import BatteryTemperatureMonitor
    TEMPERATURE_AVAILABLE = True
except ImportError:
    TEMPERATURE_AVAILABLE = False
    # Note: Will log warning during initialization if needed


class BatteryCharger:
    """Main battery charger application."""

    def __init__(self, config_path: str):
        """
        Initialize battery charger.

        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path  # Store for profile switching
        self.config = self._load_config(config_path)
        self.psu: Optional[OwonPSU] = None
        self.charging_mode: Optional[ChargingMode] = None
        self.safety_monitor: Optional[SafetyMonitor] = None
        self.mqtt_client: Optional[ChargerMQTTClient] = None
        self.battery_profile_manager: Optional[BatteryProfileManager] = None
        self.charge_scheduler: Optional[ChargeScheduler] = None
        self.error_recovery: Optional[ErrorRecoveryManager] = None
        self.battery_history: Optional[BatteryHistoryTracker] = None
        self.temperature_monitor = None
        self.running = False
        self.charging = False
        self.csv_file = None
        self.csv_writer = None
        self._shutdown_called = False  # Prevent double-shutdown
        self._charge_start_voltage = 0.0  # Track for history
        self._charge_start_time = 0.0  # Track for history

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def initialize(self) -> bool:
        """
        Initialize all components.

        Returns:
            True if successful
        """
        logger.info("Initializing battery charger...")

        # Connect to OWON PSU
        psu_config = self.config.get('power_supply', {})
        port = psu_config.get('port', '/dev/ttyUSB0')
        baudrate = psu_config.get('baudrate', 115200)
        timeout = psu_config.get('timeout', 5.0)

        self.psu = OwonPSU(port, baudrate, timeout)
        if not self.psu.connect():
            logger.error("Failed to connect to OWON PSU")
            return False

        # Initialize safety monitor
        safety_config = self.config.get('safety', {})
        plateau_config = safety_config.get('plateau_detection', {})

        limits = SafetyLimits(
            absolute_max_voltage=safety_config.get('absolute_max_voltage', 16.0),
            absolute_max_current=safety_config.get('absolute_max_current', 5.0),
            min_voltage=safety_config.get('min_voltage', 10.5),
            warning_voltage=safety_config.get('warning_voltage', 12.5),
            max_charging_duration=safety_config.get('max_charging_duration', 43200),
            max_temperature=safety_config.get('max_temperature'),
            min_temperature=safety_config.get('min_temperature'),
            # Plateau detection settings
            plateau_enabled=plateau_config.get('enabled', True),
            plateau_threshold_voltage=plateau_config.get('threshold_voltage', 16.0),
            plateau_time_window=plateau_config.get('time_window', 900),
            plateau_voltage_delta=plateau_config.get('voltage_delta', 0.05),
            # Energy accounting
            charging_efficiency=safety_config.get('charging_efficiency', 0.83)
        )
        self.safety_monitor = SafetyMonitor(limits)

        # Log plateau detection status (now configured via SafetyLimits)
        if limits.plateau_enabled:
            logger.info(
                f"Voltage plateau detection enabled: "
                f"threshold={limits.plateau_threshold_voltage}V, "
                f"window={limits.plateau_time_window}s, "
                f"delta={limits.plateau_voltage_delta}V"
            )
        else:
            logger.info("Voltage plateau detection disabled")

        # Log charging efficiency (now configured via SafetyLimits)
        logger.info(f"Charging efficiency: {limits.charging_efficiency:.1%} (factor: {1/limits.charging_efficiency:.2f})")

        # Initialize temperature sensor if available and enabled
        if TEMPERATURE_AVAILABLE:
            temp_config = self.config.get('temperature', {})
            if temp_config.get('enabled', False):
                try:
                    self.temperature_monitor = BatteryTemperatureMonitor(
                        sensor_type=temp_config.get('sensor_type', 'ds18b20'),
                        sensor_id=temp_config.get('sensor_id')
                    )
                    if self.temperature_monitor.is_available():
                        logger.info("Temperature monitoring enabled")
                    else:
                        logger.warning("Temperature sensor configured but not detected")
                        self.temperature_monitor = None
                except Exception as e:
                    logger.warning(f"Failed to initialize temperature sensor: {e}")
                    self.temperature_monitor = None
            else:
                logger.info("Temperature monitoring disabled in configuration")

        # Initialize battery profile manager
        config_dir = os.path.dirname(self.config_path) or 'config'
        self.battery_profile_manager = BatteryProfileManager(config_dir)
        profiles = self.battery_profile_manager.list_profiles()
        logger.info(f"Battery profiles available: {', '.join(profiles)}")

        # Initialize charge scheduler
        self.charge_scheduler = ChargeScheduler()
        self.charge_scheduler.set_callbacks(
            on_start=self._cmd_start,
            on_stop=self._cmd_stop,
            on_profile=self._cmd_change_profile
        )
        logger.info("Charge scheduler initialized")

        # Initialize error recovery
        self.error_recovery = ErrorRecoveryManager()
        logger.info("Error recovery manager initialized")

        # Initialize battery history tracker
        history_file = "battery_history.json"
        self.battery_history = BatteryHistoryTracker(history_file)
        logger.info(f"Battery history tracker initialized ({history_file})")

        # Initialize MQTT if enabled
        mqtt_config = self.config.get('mqtt', {})
        if mqtt_config.get('enabled', False):
            self.mqtt_client = ChargerMQTTClient(mqtt_config)
            if not self.mqtt_client.connect():
                logger.warning("Failed to connect to MQTT broker (continuing without MQTT)")
                self.mqtt_client = None
            else:
                # Set up command callbacks
                self.mqtt_client.set_command_callbacks(
                    on_start=self._cmd_start,
                    on_stop=self._cmd_stop,
                    on_mode=self._cmd_change_mode,
                    on_current=self._cmd_change_current,
                    on_profile=self._cmd_change_profile,
                    on_schedule=self._cmd_schedule,
                    on_schedule_cancel=self._cmd_schedule_cancel
                )

        logger.info("Initialization complete")
        return True

    def _cmd_start(self):
        """Handle MQTT start command."""
        if not self.charging:
            logger.info("Starting charging via MQTT command")
            self.start_charging()

    def _cmd_stop(self):
        """Handle MQTT stop command."""
        if self.charging:
            logger.info("Stopping charging via MQTT command")
            self.stop_charging()

    def _cmd_change_mode(self, mode_name: str):
        """Handle MQTT mode change command."""
        logger.info(f"Mode change requested to: {mode_name}")
        # Stop current charging if active
        if self.charging:
            self.stop_charging()

        # Create new mode
        try:
            charging_config = self.config.get('charging', {})
            mode_config = charging_config.get(mode_name, {})
            self.charging_mode = create_charging_mode(mode_name, self.psu, mode_config)
            logger.info(f"Switched to {mode_name} mode")
        except Exception as e:
            logger.error(f"Failed to change mode: {e}")

    def _cmd_change_current(self, current: float):
        """Handle MQTT current change command."""
        logger.info(f"Current change requested to: {current}A")
        # Update current in active mode if charging
        if self.charging and self.psu:
            try:
                self.psu.set_current(current)
                logger.info(f"Current set to {current}A")
            except Exception as e:
                logger.error(f"Failed to set current: {e}")

    def _cmd_change_profile(self, profile_name: str):
        """Handle MQTT battery profile change command."""
        logger.info(f"Battery profile change requested to: {profile_name}")

        # Cannot change profile while charging
        if self.charging:
            logger.error("Cannot change battery profile while charging! Stop charging first.")
            return

        # Check if profile exists
        if not self.battery_profile_manager.profile_exists(profile_name):
            available = self.battery_profile_manager.list_profiles()
            logger.error(f"Profile '{profile_name}' not found. Available: {', '.join(available)}")
            return

        # Load new profile
        try:
            new_config = self.battery_profile_manager.load_profile(profile_name)
            if not new_config:
                logger.error(f"Failed to load profile: {profile_name}")
                return

            # Update configuration
            self.config = new_config
            self.config_path = str(self.battery_profile_manager.get_profile_path(profile_name))

            # Clear charging mode (will be recreated on next start)
            self.charging_mode = None

            # Log profile info
            info = self.battery_profile_manager.get_profile_info(profile_name)
            if info:
                logger.info(
                    f"Switched to profile '{profile_name}': "
                    f"{info['model']} ({info['capacity']}Ah, {info['chemistry']}), "
                    f"mode={info['default_mode']}, "
                    f"bulk={info['bulk_current']}A, "
                    f"absorption={info['absorption_voltage']}V"
                )
            else:
                logger.info(f"Switched to battery profile: {profile_name}")

        except Exception as e:
            logger.error(f"Failed to change battery profile: {e}")

    def _cmd_schedule(self, schedule_params: dict):
        """
        Handle MQTT schedule command.

        Args:
            schedule_params: Dictionary with schedule parameters:
                - start_time: Time string ("now", "14:30", "2025-11-02 14:30")
                - duration: Duration string ("1h", "30m", "3600")
                - profile: Battery profile to use (optional)
                - mode: Charging mode to use (optional)
        """
        if not self.charge_scheduler:
            logger.error("Charge scheduler not initialized")
            return

        try:
            # Parse start time
            start_time_str = schedule_params.get('start_time', 'now')
            start_time = self.charge_scheduler.parse_start_time(start_time_str)

            # Parse duration (optional)
            duration = None
            if 'duration' in schedule_params:
                duration = self.charge_scheduler.parse_duration(schedule_params['duration'])

            # Get profile and mode (optional)
            profile = schedule_params.get('profile')
            mode = schedule_params.get('mode')

            # Schedule the charge
            self.charge_scheduler.schedule_charge(
                start_time=start_time,
                duration=duration,
                profile=profile,
                mode=mode
            )

            logger.info(f"Charging scheduled: start={start_time_str}, duration={schedule_params.get('duration', 'unlimited')}, profile={profile or 'current'}")

        except Exception as e:
            logger.error(f"Failed to schedule charge: {e}")

    def _cmd_schedule_cancel(self):
        """Handle MQTT schedule cancel command."""
        if not self.charge_scheduler:
            logger.error("Charge scheduler not initialized")
            return

        try:
            self.charge_scheduler.cancel_schedule()
            logger.info("Scheduled charge cancelled")
        except Exception as e:
            logger.error(f"Failed to cancel schedule: {e}")

    def start_charging(self) -> bool:
        """
        Start charging process.

        Returns:
            True if started successfully
        """
        if self.charging:
            logger.warning("Already charging")
            return False

        try:
            # Create charging mode if not exists
            if not self.charging_mode:
                charging_config = self.config.get('charging', {})
                default_mode = charging_config.get('default_mode', 'IUoU')
                mode_config = charging_config.get(default_mode, {})
                self.charging_mode = create_charging_mode(default_mode, self.psu, mode_config)

            # Start charging mode
            if not self.charging_mode.start():
                logger.error("Failed to start charging mode")
                return False

            # Start safety monitoring
            self.safety_monitor.start_monitoring()

            # Open CSV log file
            self._open_log_file()

            # Record start conditions for history
            if self.psu:
                self._charge_start_voltage = self.psu.measure_voltage()
                self._charge_start_time = time.time()

            self.charging = True
            logger.info("Charging started")
            return True

        except Exception as e:
            logger.error(f"Failed to start charging: {e}")
            return False

    def stop_charging(self):
        """Stop charging process."""
        if not self.charging:
            return

        try:
            # Stop charging mode
            if self.charging_mode:
                self.charging_mode.stop()

            # Stop safety monitoring
            if self.safety_monitor:
                self.safety_monitor.stop_monitoring()

            # Close log file
            self._close_log_file()

            # Record session in battery history
            if self.battery_history and self.psu and self._charge_start_time > 0:
                try:
                    end_voltage = self.psu.measure_voltage()
                    duration = int(time.time() - self._charge_start_time)

                    # Get battery model from config
                    battery_config = self.config.get('battery', {})
                    battery_model = battery_config.get('model', 'Unknown')

                    # Get charge data from safety monitor
                    if self.safety_monitor:
                        ah_delivered = self.safety_monitor.ah_delivered
                        wh_delivered = self.safety_monitor.wh_delivered
                    else:
                        ah_delivered = 0.0
                        wh_delivered = 0.0

                    # Get charging mode (use class name)
                    mode = self.charging_mode.__class__.__name__ if self.charging_mode else 'Unknown'

                    # Record session
                    self.battery_history.record_charge_session(
                        battery_model=battery_model,
                        start_voltage=self._charge_start_voltage,
                        end_voltage=end_voltage,
                        ah_delivered=ah_delivered,
                        wh_delivered=wh_delivered,
                        duration=duration,
                        mode=mode,
                        success=True
                    )
                except Exception as e:
                    logger.error(f"Failed to record battery history: {e}")

            self.charging = False
            logger.info("Charging stopped")

        except Exception as e:
            logger.error(f"Error stopping charging: {e}")

    def _open_log_file(self):
        """Open CSV log file for this charging session."""
        logging_config = self.config.get('logging', {})
        if not logging_config.get('enabled', False):
            return

        try:
            # Create logs directory
            log_dir = Path(logging_config.get('log_dir', 'logs'))
            log_dir.mkdir(exist_ok=True)

            # Create CSV file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_path = log_dir / f'charge_{timestamp}.csv'

            self.csv_file = open(csv_path, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)

            # Write header
            fields = logging_config.get('fields', [])
            self.csv_writer.writerow(fields)

            logger.info(f"Logging to {csv_path}")

        except Exception as e:
            logger.error(f"Failed to open log file: {e}")
            self.csv_file = None
            self.csv_writer = None

    def _close_log_file(self):
        """Close CSV log file."""
        if self.csv_file:
            try:
                self.csv_file.close()
                logger.info("Log file closed")
            except Exception as e:
                logger.error(f"Error closing log file: {e}")
            finally:
                self.csv_file = None
                self.csv_writer = None

    def _log_data(self, status: dict):
        """
        Log charging data to CSV.

        Args:
            status: Status dictionary
        """
        if not self.csv_writer:
            return

        try:
            logging_config = self.config.get('logging', {})
            fields = logging_config.get('fields', [])

            # Extract values for each field
            row = []
            for field in fields:
                if field == 'timestamp':
                    value = datetime.now().isoformat()
                else:
                    value = status.get(field, '')
                row.append(value)

            self.csv_writer.writerow(row)
            self.csv_file.flush()

        except Exception as e:
            logger.error(f"Failed to log data: {e}")

    def run(self):
        """Run main application loop."""
        self.running = True
        logger.info("Battery charger running...")

        # Get measurement interval
        safety_config = self.config.get('safety', {})
        measurement_interval = safety_config.get('measurement_interval', 5.0)
        log_interval = safety_config.get('log_interval', 60.0)
        last_log_time = 0.0

        while self.running:
            try:
                # If charging, update and monitor
                if self.charging and self.charging_mode:
                    # Update charging mode
                    status = self.charging_mode.update()

                    # Read temperature if available
                    temperature = None
                    if self.temperature_monitor:
                        temperature = self.temperature_monitor.read_temperature()
                        if temperature is not None:
                            status['temperature'] = temperature

                    # Check safety
                    voltage = status.get('voltage', 0.0)
                    current = status.get('current', 0.0)
                    power = status.get('power', 0.0)
                    safety_result = self.safety_monitor.check_safety(voltage, current, temperature)

                    # Update energy accounting (Coulomb counting)
                    energy_data = self.safety_monitor.update_energy_accounting(current, power)
                    status.update(energy_data)

                    # Add safety info to status
                    status['progress'] = self.safety_monitor.estimate_progress(
                        mode=status.get('mode', ''),
                        stage=status.get('stage'),
                        current=current,
                        voltage=voltage,
                        target_voltage=status.get('absorption_voltage', 0.0),
                        absorption_current_threshold=status.get('absorption_current_threshold', 1.0)
                    )

                    # Publish to MQTT
                    if self.mqtt_client:
                        self.mqtt_client.publish_status(status)

                    # Log to CSV periodically
                    now = time.time()
                    if now - last_log_time >= log_interval:
                        self._log_data(status)
                        last_log_time = now

                    # Check if should stop due to safety
                    if safety_result['should_stop']:
                        logger.error("Safety violation - stopping charging")
                        self.stop_charging()

                    # Check for voltage plateau (flooded batteries above 16V)
                    # If voltage stops rising, battery is fully charged
                    plateau_status = self.safety_monitor.check_voltage_plateau(voltage)
                    if plateau_status['is_plateau']:
                        logger.info(
                            f"Battery fully charged - voltage plateau detected at {voltage:.3f}V "
                            f"(rise {plateau_status['voltage_rise']:.3f}V over {plateau_status['time_at_high_voltage']/60:.1f} min)"
                        )
                        self.stop_charging()

                    # Check if charging complete
                    if self.safety_monitor.is_charging_complete(
                        mode=status.get('mode', ''),
                        current=current,
                        state=status.get('state', ''),
                        min_current=status.get('min_current', 0.5)
                    ):
                        logger.info("Charging complete")
                        self.stop_charging()

                # Update charge scheduler (if enabled)
                if self.charge_scheduler:
                    self.charge_scheduler.update()

                # Check connections and attempt recovery
                if self.error_recovery:
                    self.error_recovery.check_psu_connection(self.psu, check_interval=10.0)
                    self.error_recovery.check_mqtt_connection(self.mqtt_client, check_interval=10.0)

                # Sleep until next measurement
                time.sleep(measurement_interval)

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(1)

        # Cleanup
        self.shutdown()

    def shutdown(self):
        """Clean shutdown of all components."""
        # Prevent double-shutdown (called by both main loop and atexit)
        if self._shutdown_called:
            return
        self._shutdown_called = True

        logger.info("Shutting down...")

        # Stop charging
        if self.charging:
            self.stop_charging()

        # CRITICAL: Ensure PSU output is OFF (safety!)
        if self.psu and self.psu.is_connected():
            try:
                logger.info("Forcing PSU output OFF for safety...")
                self.psu.set_output(False)
                logger.info("PSU output disabled")
            except Exception as e:
                logger.error(f"Failed to disable PSU output: {e}")

        # Disconnect MQTT
        if self.mqtt_client:
            self.mqtt_client.disconnect()

        # Disconnect PSU
        if self.psu:
            self.psu.disconnect()

        logger.info("Shutdown complete")


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Battery Charger Controller')
    parser.add_argument(
        '-c', '--config',
        default='config/charging_config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--auto-start',
        action='store_true',
        help='Automatically start charging on startup'
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)

    # Print banner
    logger.info("=" * 60)
    logger.info("Battery Charger - Raspberry Pi + OWON SPE6205")
    logger.info("=" * 60)

    # Create and initialize charger
    charger = BatteryCharger(args.config)
    if not charger.initialize():
        logger.error("Initialization failed")
        sys.exit(1)

    # Register cleanup handler for atexit (runs on normal exit)
    atexit.register(charger.shutdown)
    logger.info("Registered atexit cleanup handler")

    # Auto-start if requested
    if args.auto_start:
        charger.start_charging()

    # Run main loop
    try:
        charger.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
