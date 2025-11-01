"""
OWON Power Supply SCPI Driver
Tested with SPE6205 (62V 5A)
"""

import serial
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OwonPSU:
    """OWON Power Supply SCPI interface."""

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 5.0):
        """
        Initialize OWON PSU connection.

        Args:
            port: Serial port (e.g., /dev/ttyUSB0)
            baudrate: Baud rate (default 115200 for OWON)
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self._connected = False

    def connect(self) -> bool:
        """
        Connect to power supply.

        Returns:
            True if connected successfully
        """
        try:
            logger.info(f"Connecting to OWON PSU on {self.port}...")
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            time.sleep(0.5)  # Let connection settle
            self._connected = True  # Set before identify() to allow _query()

            # Test connection
            identity = self.identify()
            if identity:
                logger.info(f"Connected to: {identity}")
                return True
            else:
                logger.error("Failed to get device identity")
                return False

        except serial.SerialException as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from power supply."""
        if self.serial and self.serial.is_open:
            try:
                # Turn off output for safety
                self.set_output(False)
                self.serial.close()
                logger.info("Disconnected from OWON PSU")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
        self._connected = False

    def is_connected(self) -> bool:
        """Check if connected to PSU."""
        return self._connected and self.serial and self.serial.is_open

    def _send_command(self, command: str) -> None:
        """
        Send SCPI command to PSU.

        Args:
            command: SCPI command string
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to PSU")

        cmd_bytes = f"{command}\n".encode('utf-8')
        self.serial.write(cmd_bytes)
        self.serial.flush()
        time.sleep(0.05)  # Small delay for command processing

    def _query(self, command: str) -> str:
        """
        Send SCPI query and read response.

        Args:
            command: SCPI query command

        Returns:
            Response string
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to PSU")

        # Clear any pending data
        self.serial.reset_input_buffer()

        # Send query
        self._send_command(command)

        # Read response
        response = self.serial.readline().decode('utf-8').strip()
        return response

    # Device Information
    def identify(self) -> str:
        """
        Get device identification.

        Returns:
            Device ID string (e.g., "OWON,SPE6205,SN,FW")
        """
        try:
            return self._query("*IDN?")
        except Exception as e:
            logger.error(f"Failed to identify device: {e}")
            return ""

    # Voltage Control
    def set_voltage(self, voltage: float) -> None:
        """
        Set output voltage.

        Args:
            voltage: Voltage in Volts
        """
        self._send_command(f"VOLT {voltage:.3f}")
        logger.debug(f"Set voltage to {voltage:.3f}V")

    def get_voltage(self) -> float:
        """
        Get set voltage value.

        Returns:
            Set voltage in Volts
        """
        response = self._query("VOLT?")
        try:
            return float(response)
        except ValueError:
            logger.error(f"Invalid voltage response: {response}")
            return 0.0

    def measure_voltage(self) -> float:
        """
        Measure actual output voltage.

        Returns:
            Measured voltage in Volts
        """
        response = self._query("MEAS:VOLT?")
        try:
            return float(response)
        except ValueError:
            logger.error(f"Invalid measured voltage: {response}")
            return 0.0

    # Current Control
    def set_current(self, current: float) -> None:
        """
        Set output current limit.

        Args:
            current: Current in Amperes
        """
        self._send_command(f"CURR {current:.3f}")
        logger.debug(f"Set current to {current:.3f}A")

    def get_current(self) -> float:
        """
        Get set current limit.

        Returns:
            Set current in Amperes
        """
        response = self._query("CURR?")
        try:
            return float(response)
        except ValueError:
            logger.error(f"Invalid current response: {response}")
            return 0.0

    def measure_current(self) -> float:
        """
        Measure actual output current.

        Returns:
            Measured current in Amperes
        """
        response = self._query("MEAS:CURR?")
        try:
            return float(response)
        except ValueError:
            logger.error(f"Invalid measured current: {response}")
            return 0.0

    def measure_power(self) -> float:
        """
        Measure actual output power.

        Returns:
            Measured power in Watts
        """
        response = self._query("MEAS:POW?")
        try:
            return float(response)
        except ValueError:
            logger.error(f"Invalid measured power: {response}")
            return 0.0

    def get_system_error(self) -> str:
        """
        Get system error status.

        Returns:
            Error code string (0x0000 = no error)
        """
        response = self._query("SYST:ERR?")
        return response if response else "UNKNOWN"

    # Output Control
    def set_output(self, enabled: bool) -> None:
        """
        Enable or disable power supply output.

        Args:
            enabled: True to enable, False to disable
        """
        state = "ON" if enabled else "OFF"
        self._send_command(f"OUTP {state}")
        logger.info(f"Output {'enabled' if enabled else 'disabled'}")

    def get_output(self) -> bool:
        """
        Get output enable state.

        Returns:
            True if output enabled, False if disabled
        """
        response = self._query("OUTP?")
        return response.strip().upper() in ['ON', '1']

    # Convenience Methods
    def get_status(self) -> dict:
        """
        Get complete PSU status.

        Returns:
            Dictionary with voltage, current, output state
        """
        return {
            'voltage_set': self.get_voltage(),
            'current_set': self.get_current(),
            'voltage_measured': self.measure_voltage(),
            'current_measured': self.measure_current(),
            'output_enabled': self.get_output()
        }

    def set_display_mode(self, mode: str = "NORM") -> bool:
        """
        Set display mode on PSU front panel.

        ⚠️ NOTE: SPE6205 does NOT support display commands (hardware limitation).
        This method is included for API completeness but will return ERR on SPE6205.
        See: https://files.owon.com.cn/software/Application/SP_and_SPE_SPS_programming_manual.pdf

        OWON SCPI command: DISP:MODE <mode>

        Args:
            mode: Display mode
                  "NORM" - Normal mode (default, shows V/A/W)
                  "TEXT" - Text mode (custom message)
                  "WAVE" - Waveform mode (if supported)

        Returns:
            True if command succeeded
        """
        valid_modes = ["NORM", "TEXT", "WAVE"]
        mode = mode.upper()
        if mode not in valid_modes:
            logger.error(f"Invalid display mode: {mode}. Valid: {valid_modes}")
            return False

        try:
            self._send_command(f"DISP:MODE {mode}")
            logger.debug(f"Set display mode to {mode}")
            return True
        except Exception as e:
            logger.error(f"Failed to set display mode: {e}")
            return False

    def set_display_text(self, text: str) -> bool:
        """
        Set custom text on PSU display (TEXT mode).

        ⚠️ NOTE: SPE6205 does NOT support display commands (hardware limitation).
        This method is included for API completeness but will return ERR on SPE6205.
        See: https://files.owon.com.cn/software/Application/SP_and_SPE_SPS_programming_manual.pdf

        OWON SCPI command: DISP:TEXT "<text>"

        Args:
            text: Text to display (max length varies by model)

        Returns:
            True if command succeeded
        """
        try:
            # Switch to TEXT mode first
            self.set_display_mode("TEXT")
            # Set custom text
            self._send_command(f'DISP:TEXT "{text}"')
            logger.info(f"Set display text to: {text}")
            return True
        except Exception as e:
            logger.error(f"Failed to set display text: {e}")
            return False

    def set_display_normal(self) -> bool:
        """
        Restore normal display mode (shows V/A/W).

        Returns:
            True if command succeeded
        """
        return self.set_display_mode("NORM")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
