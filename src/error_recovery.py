#!/usr/bin/env python3
"""
Error Recovery Module
Handles PSU disconnects, MQTT failures, and automatic recovery
"""

import logging
import time
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class ErrorRecoveryManager:
    """Manages error detection and automatic recovery."""

    def __init__(self):
        """Initialize error recovery manager."""
        self.psu_disconnects = 0
        self.mqtt_disconnects = 0
        self.last_psu_check = 0.0
        self.last_mqtt_check = 0.0
        self.recovery_enabled = True

        # Callbacks
        self.on_psu_reconnect: Optional[Callable] = None
        self.on_mqtt_reconnect: Optional[Callable] = None

    def set_callbacks(
        self,
        on_psu_reconnect: Optional[Callable] = None,
        on_mqtt_reconnect: Optional[Callable] = None
    ):
        """
        Set recovery callbacks.

        Args:
            on_psu_reconnect: Callback when PSU reconnects
            on_mqtt_reconnect: Callback when MQTT reconnects
        """
        self.on_psu_reconnect = on_psu_reconnect
        self.on_mqtt_reconnect = on_mqtt_reconnect

    def check_psu_connection(self, psu, check_interval: float = 10.0) -> bool:
        """
        Check PSU connection and attempt recovery.

        Args:
            psu: PSU instance
            check_interval: Seconds between checks

        Returns:
            True if connected
        """
        now = time.time()
        if now - self.last_psu_check < check_interval:
            return True  # Don't check too frequently

        self.last_psu_check = now

        if not psu or not psu.is_connected():
            self.psu_disconnects += 1
            logger.warning(f"PSU disconnected (count: {self.psu_disconnects})")

            if self.recovery_enabled and psu:
                logger.info("Attempting PSU reconnection...")
                try:
                    if psu.connect():
                        logger.info("PSU reconnected successfully")
                        if self.on_psu_reconnect:
                            self.on_psu_reconnect()
                        return True
                except Exception as e:
                    logger.error(f"PSU reconnection failed: {e}")

            return False

        return True

    def check_mqtt_connection(self, mqtt_client, check_interval: float = 10.0) -> bool:
        """
        Check MQTT connection and attempt recovery.

        Args:
            mqtt_client: MQTT client instance
            check_interval: Seconds between checks

        Returns:
            True if connected
        """
        now = time.time()
        if now - self.last_mqtt_check < check_interval:
            return True

        self.last_mqtt_check = now

        if not mqtt_client or not mqtt_client.is_connected():
            self.mqtt_disconnects += 1
            logger.warning(f"MQTT disconnected (count: {self.mqtt_disconnects})")

            if self.recovery_enabled and mqtt_client:
                logger.info("Attempting MQTT reconnection...")
                try:
                    if mqtt_client.connect():
                        logger.info("MQTT reconnected successfully")
                        if self.on_mqtt_reconnect:
                            self.on_mqtt_reconnect()
                        return True
                except Exception as e:
                    logger.error(f"MQTT reconnection failed: {e}")

            return False

        return True

    def get_stats(self) -> dict:
        """
        Get error recovery statistics.

        Returns:
            Dictionary with stats
        """
        return {
            'psu_disconnects': self.psu_disconnects,
            'mqtt_disconnects': self.mqtt_disconnects,
            'recovery_enabled': self.recovery_enabled
        }

    def reset_stats(self):
        """Reset error counters."""
        self.psu_disconnects = 0
        self.mqtt_disconnects = 0
        logger.info("Error recovery stats reset")
