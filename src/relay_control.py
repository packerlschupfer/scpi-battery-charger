"""
AC Relay Control for PSU Safety
Supports Shelly Plug, Tasmota, and GPIO relays
"""

import time
import logging
import requests
from typing import Optional
from threading import Thread, Event

logger = logging.getLogger(__name__)


class RelayController:
    """Base class for relay control."""

    def __init__(self, config: dict):
        """
        Initialize relay controller.

        Args:
            config: Relay configuration dictionary
        """
        self.config = config
        self.enabled = config.get('enabled', False)
        self.keepalive_interval = config.get('keepalive_interval', 30)
        self._keepalive_thread: Optional[Thread] = None
        self._keepalive_stop = Event()

    def turn_on(self) -> bool:
        """
        Turn relay ON (enable AC power to PSU).

        Returns:
            True if successful
        """
        raise NotImplementedError

    def turn_off(self) -> bool:
        """
        Turn relay OFF (disable AC power to PSU).

        Returns:
            True if successful
        """
        raise NotImplementedError

    def get_state(self) -> bool:
        """
        Get current relay state.

        Returns:
            True if ON, False if OFF
        """
        raise NotImplementedError

    def start_keepalive(self):
        """Start keepalive thread to ensure relay stays ON."""
        if not self.enabled:
            return

        if self._keepalive_thread and self._keepalive_thread.is_alive():
            logger.warning("Keepalive already running")
            return

        self._keepalive_stop.clear()
        self._keepalive_thread = Thread(target=self._keepalive_loop, daemon=True)
        self._keepalive_thread.start()
        logger.info(f"Keepalive started (interval: {self.keepalive_interval}s)")

    def stop_keepalive(self):
        """Stop keepalive thread."""
        if self._keepalive_thread and self._keepalive_thread.is_alive():
            self._keepalive_stop.set()
            self._keepalive_thread.join(timeout=5)
            logger.info("Keepalive stopped")

    def _keepalive_loop(self):
        """Keepalive loop - periodically turn relay ON."""
        while not self._keepalive_stop.is_set():
            try:
                self.turn_on()
                logger.debug("Keepalive pulse sent")
            except Exception as e:
                logger.error(f"Keepalive failed: {e}")

            # Wait for interval or stop event
            self._keepalive_stop.wait(self.keepalive_interval)


class ShellyRelay(RelayController):
    """
    Shelly Plug control via HTTP API.

    Supports:
    - Shelly Plug S
    - Shelly Plus Plug S
    - Shelly 1PM
    - Other Shelly devices with relay
    """

    def __init__(self, config: dict):
        """
        Initialize Shelly relay.

        Config example:
        {
            'enabled': True,
            'type': 'shelly',
            'host': '192.168.1.100',
            'generation': 1,  # 1 for Gen1, 2 for Plus/Pro
            'timeout': 5,
            'keepalive_interval': 30
        }
        """
        super().__init__(config)
        self.host = config.get('host', 'shellyplug-XXXXXX.local')
        self.generation = config.get('generation', 1)
        self.timeout = config.get('timeout', 5)

    def _get_url(self, endpoint: str) -> str:
        """Build API URL based on generation."""
        if self.generation == 2:
            # Gen2/Plus API
            return f"http://{self.host}/rpc/{endpoint}"
        else:
            # Gen1 API
            return f"http://{self.host}/{endpoint}"

    def turn_on(self) -> bool:
        """Turn Shelly relay ON."""
        if not self.enabled:
            logger.debug("Relay control disabled, skipping ON")
            return True

        try:
            if self.generation == 2:
                # Gen2/Plus: Switch.Set
                url = self._get_url("Switch.Set")
                params = {'id': 0, 'on': True}
            else:
                # Gen1: relay/0?turn=on
                url = self._get_url("relay/0")
                params = {'turn': 'on'}

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            logger.info("Relay turned ON (PSU powered)")
            return True

        except Exception as e:
            logger.error(f"Failed to turn relay ON: {e}")
            return False

    def turn_off(self) -> bool:
        """Turn Shelly relay OFF."""
        if not self.enabled:
            logger.debug("Relay control disabled, skipping OFF")
            return True

        try:
            if self.generation == 2:
                # Gen2/Plus: Switch.Set
                url = self._get_url("Switch.Set")
                params = {'id': 0, 'on': False}
            else:
                # Gen1: relay/0?turn=off
                url = self._get_url("relay/0")
                params = {'turn': 'off'}

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            logger.info("Relay turned OFF (PSU unpowered - SAFE)")
            return True

        except Exception as e:
            logger.error(f"Failed to turn relay OFF: {e}")
            return False

    def get_state(self) -> bool:
        """Get Shelly relay state."""
        if not self.enabled:
            return False

        try:
            if self.generation == 2:
                # Gen2/Plus: Switch.GetStatus
                url = self._get_url("Switch.GetStatus")
                params = {'id': 0}
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                return data.get('output', False)
            else:
                # Gen1: relay/0
                url = self._get_url("relay/0")
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                return data.get('ison', False)

        except Exception as e:
            logger.error(f"Failed to get relay state: {e}")
            return False


class TasmotaRelay(RelayController):
    """
    Tasmota relay control via HTTP API.

    Supports any Tasmota-flashed device (Sonoff, etc.)
    """

    def __init__(self, config: dict):
        """
        Initialize Tasmota relay.

        Config example:
        {
            'enabled': True,
            'type': 'tasmota',
            'host': '192.168.1.101',
            'timeout': 5,
            'keepalive_interval': 30
        }
        """
        super().__init__(config)
        self.host = config.get('host', 'tasmota-XXXXXX.local')
        self.timeout = config.get('timeout', 5)

    def _send_command(self, command: str) -> Optional[dict]:
        """Send Tasmota command."""
        try:
            url = f"http://{self.host}/cm"
            params = {'cmnd': command}
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Tasmota command failed: {e}")
            return None

    def turn_on(self) -> bool:
        """Turn Tasmota relay ON."""
        if not self.enabled:
            logger.debug("Relay control disabled, skipping ON")
            return True

        result = self._send_command("Power ON")
        if result and result.get('POWER') == 'ON':
            logger.info("Relay turned ON (PSU powered)")
            return True
        return False

    def turn_off(self) -> bool:
        """Turn Tasmota relay OFF."""
        if not self.enabled:
            logger.debug("Relay control disabled, skipping OFF")
            return True

        result = self._send_command("Power OFF")
        if result and result.get('POWER') == 'OFF':
            logger.info("Relay turned OFF (PSU unpowered - SAFE)")
            return True
        return False

    def get_state(self) -> bool:
        """Get Tasmota relay state."""
        if not self.enabled:
            return False

        result = self._send_command("Power")
        if result:
            return result.get('POWER') == 'ON'
        return False


class GPIORelay(RelayController):
    """
    GPIO relay control (direct Raspberry Pi pins).

    WARNING: Less safe than network relays!
    If Raspberry Pi freezes, relay stays in last state.
    Only use with external watchdog circuit.
    """

    def __init__(self, config: dict):
        """
        Initialize GPIO relay.

        Config example:
        {
            'enabled': True,
            'type': 'gpio',
            'pin': 17,  # BCM pin number
            'active_high': True,  # True if relay ON = GPIO HIGH
            'keepalive_interval': 30
        }
        """
        super().__init__(config)
        self.pin = config.get('pin', 17)
        self.active_high = config.get('active_high', True)

        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.GPIO.setmode(GPIO.BCM)
            self.GPIO.setup(self.pin, GPIO.OUT)
            logger.info(f"GPIO relay initialized on pin {self.pin}")
        except ImportError:
            logger.error("RPi.GPIO not available - GPIO relay disabled")
            self.enabled = False

    def turn_on(self) -> bool:
        """Turn GPIO relay ON."""
        if not self.enabled:
            logger.debug("Relay control disabled, skipping ON")
            return True

        try:
            state = self.GPIO.HIGH if self.active_high else self.GPIO.LOW
            self.GPIO.output(self.pin, state)
            logger.info("Relay turned ON (PSU powered)")
            return True
        except Exception as e:
            logger.error(f"Failed to turn GPIO relay ON: {e}")
            return False

    def turn_off(self) -> bool:
        """Turn GPIO relay OFF."""
        if not self.enabled:
            logger.debug("Relay control disabled, skipping OFF")
            return True

        try:
            state = self.GPIO.LOW if self.active_high else self.GPIO.HIGH
            self.GPIO.output(self.pin, state)
            logger.info("Relay turned OFF (PSU unpowered - SAFE)")
            return True
        except Exception as e:
            logger.error(f"Failed to turn GPIO relay OFF: {e}")
            return False

    def get_state(self) -> bool:
        """Get GPIO relay state."""
        if not self.enabled:
            return False

        try:
            state = self.GPIO.input(self.pin)
            if self.active_high:
                return state == self.GPIO.HIGH
            else:
                return state == self.GPIO.LOW
        except Exception as e:
            logger.error(f"Failed to get GPIO state: {e}")
            return False

    def cleanup(self):
        """Cleanup GPIO."""
        if self.enabled:
            try:
                self.GPIO.cleanup(self.pin)
            except Exception as e:
                logger.error(f"GPIO cleanup failed: {e}")


def create_relay_controller(config: dict) -> RelayController:
    """
    Factory function to create appropriate relay controller.

    Args:
        config: Relay configuration dictionary

    Returns:
        RelayController instance

    Example config:
    {
        'enabled': True,
        'type': 'shelly',  # or 'tasmota', 'gpio'
        'host': '192.168.1.100',
        'generation': 1,
        'keepalive_interval': 30
    }
    """
    if not config.get('enabled', False):
        logger.info("Relay control disabled in configuration")
        # Return dummy controller that does nothing
        return RelayController(config)

    relay_type = config.get('type', 'shelly').lower()

    if relay_type == 'shelly':
        return ShellyRelay(config)
    elif relay_type == 'tasmota':
        return TasmotaRelay(config)
    elif relay_type == 'gpio':
        return GPIORelay(config)
    else:
        logger.error(f"Unknown relay type: {relay_type}")
        return RelayController(config)
