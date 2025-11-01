"""
Temperature sensor support for battery monitoring.
DS18B20 1-Wire digital temperature sensor.
"""

import time
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DS18B20Sensor:
    """
    DS18B20 digital temperature sensor via 1-Wire interface.

    Hardware:
    - DS18B20 sensor connected to Raspberry Pi GPIO 4
    - 4.7kΩ pull-up resistor between DATA and VCC

    Setup:
    1. Enable 1-Wire interface:
       sudo raspi-config → Interface Options → 1-Wire → Enable

    2. Reboot or load module:
       sudo modprobe w1-gpio
       sudo modprobe w1-therm

    3. Find sensor ID:
       ls /sys/bus/w1/devices/
       # Look for 28-xxxxxxxxxxxx
    """

    def __init__(self, sensor_id: Optional[str] = None):
        """
        Initialize temperature sensor.

        Args:
            sensor_id: Sensor ID (e.g., "28-0123456789ab")
                      If None, auto-detect first sensor
        """
        self.sensor_id = sensor_id
        self.base_path = Path("/sys/bus/w1/devices")
        self.sensor_path = None
        self.available = False

        self._detect_sensor()

    def _detect_sensor(self):
        """Auto-detect temperature sensor."""
        if not self.base_path.exists():
            logger.warning("1-Wire interface not available")
            logger.warning("Enable with: sudo raspi-config → Interface Options → 1-Wire")
            return

        if self.sensor_id:
            # Use specified sensor ID
            self.sensor_path = self.base_path / self.sensor_id / "w1_slave"
        else:
            # Auto-detect first sensor
            try:
                sensors = list(self.base_path.glob("28-*"))
                if sensors:
                    self.sensor_path = sensors[0] / "w1_slave"
                    self.sensor_id = sensors[0].name
                    logger.info(f"Auto-detected sensor: {self.sensor_id}")
            except Exception as e:
                logger.error(f"Failed to detect sensor: {e}")
                return

        if self.sensor_path and self.sensor_path.exists():
            self.available = True
            logger.info(f"Temperature sensor available: {self.sensor_id}")
        else:
            logger.warning(f"Temperature sensor not found: {self.sensor_id}")

    def read_temperature(self) -> Optional[float]:
        """
        Read temperature from sensor.

        Returns:
            Temperature in °C, or None if sensor not available
        """
        if not self.available:
            return None

        try:
            # Read raw data
            with open(self.sensor_path, 'r') as f:
                lines = f.readlines()

            # Check CRC
            if len(lines) < 2 or lines[0].strip()[-3:] != 'YES':
                logger.error("Temperature read failed (CRC error)")
                return None

            # Extract temperature
            temp_pos = lines[1].find('t=')
            if temp_pos != -1:
                temp_string = lines[1][temp_pos + 2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c

        except Exception as e:
            logger.error(f"Failed to read temperature: {e}")

        return None

    def is_available(self) -> bool:
        """Check if sensor is available."""
        return self.available

    def get_sensor_id(self) -> Optional[str]:
        """Get sensor ID."""
        return self.sensor_id


class BatteryTemperatureMonitor:
    """Monitor battery temperature with multiple sensor support."""

    def __init__(self, sensor_type: str = "ds18b20", sensor_id: Optional[str] = None):
        """
        Initialize temperature monitor.

        Args:
            sensor_type: Type of sensor ("ds18b20" or "none")
            sensor_id: Sensor ID (for DS18B20)
        """
        self.sensor_type = sensor_type
        self.sensor = None
        self.last_temperature = None
        self.last_read_time = 0

        if sensor_type == "ds18b20":
            self.sensor = DS18B20Sensor(sensor_id)
        else:
            logger.info("No temperature sensor configured")

    def read_temperature(self, use_cache: bool = True, cache_time: float = 2.0) -> Optional[float]:
        """
        Read battery temperature.

        Args:
            use_cache: Use cached value if recent
            cache_time: Cache validity time in seconds

        Returns:
            Temperature in °C, or None if not available
        """
        if self.sensor is None:
            return None

        # Check cache
        now = time.time()
        if use_cache and self.last_temperature is not None:
            if (now - self.last_read_time) < cache_time:
                return self.last_temperature

        # Read new value
        temp = self.sensor.read_temperature()
        if temp is not None:
            self.last_temperature = temp
            self.last_read_time = now

        return temp

    def is_available(self) -> bool:
        """Check if temperature monitoring is available."""
        return self.sensor is not None and self.sensor.is_available()

    def check_temperature_limits(
        self,
        temperature: Optional[float],
        min_temp: float = 0.0,
        max_temp: float = 45.0
    ) -> dict:
        """
        Check if temperature is within safe limits.

        Args:
            temperature: Current temperature in °C
            min_temp: Minimum safe temperature
            max_temp: Maximum safe temperature

        Returns:
            Dictionary with warning/error status
        """
        if temperature is None:
            return {
                'safe': True,
                'warning': None,
                'available': False
            }

        warnings = []
        safe = True

        if temperature < min_temp:
            warnings.append(f"Temperature too low: {temperature:.1f}°C < {min_temp}°C")
            safe = False
        elif temperature < (min_temp + 5):
            warnings.append(f"Temperature low: {temperature:.1f}°C (warn at {min_temp}°C)")

        if temperature > max_temp:
            warnings.append(f"Temperature too high: {temperature:.1f}°C > {max_temp}°C")
            safe = False
        elif temperature > (max_temp - 5):
            warnings.append(f"Temperature high: {temperature:.1f}°C (limit {max_temp}°C)")

        return {
            'safe': safe,
            'warnings': warnings,
            'available': True,
            'temperature': temperature
        }


# Test/demo code
if __name__ == '__main__':
    import sys

    print("DS18B20 Temperature Sensor Test")
    print("=" * 60)

    # Try to detect sensor
    sensor = DS18B20Sensor()

    if not sensor.is_available():
        print("❌ No temperature sensor detected!")
        print()
        print("Setup instructions:")
        print("1. Enable 1-Wire interface:")
        print("   sudo raspi-config → Interface Options → 1-Wire → Enable")
        print()
        print("2. Reboot or load modules:")
        print("   sudo modprobe w1-gpio")
        print("   sudo modprobe w1-therm")
        print()
        print("3. Check for sensors:")
        print("   ls /sys/bus/w1/devices/")
        print()
        sys.exit(1)

    print(f"✓ Sensor found: {sensor.get_sensor_id()}")
    print()

    # Read temperature
    print("Reading temperature...")
    for i in range(5):
        temp = sensor.read_temperature()
        if temp is not None:
            print(f"  Reading {i+1}: {temp:.2f}°C")
        else:
            print(f"  Reading {i+1}: Failed")
        time.sleep(1)

    print()
    print("=" * 60)
