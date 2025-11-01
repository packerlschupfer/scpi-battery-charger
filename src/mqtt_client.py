"""
MQTT client for battery charger monitoring and control.
"""

import json
import logging
import time
from typing import Optional, Callable, Dict
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class ChargerMQTTClient:
    """MQTT client for charger monitoring and control."""

    def __init__(self, config: dict):
        """
        Initialize MQTT client.

        Args:
            config: MQTT configuration dictionary
        """
        self.config = config
        self.client: Optional[mqtt.Client] = None
        self.connected = False

        # Command callbacks
        self.on_start_callback: Optional[Callable] = None
        self.on_stop_callback: Optional[Callable] = None
        self.on_mode_callback: Optional[Callable[[str], None]] = None
        self.on_current_callback: Optional[Callable[[float], None]] = None
        self.on_profile_callback: Optional[Callable[[str], None]] = None
        self.on_schedule_callback: Optional[Callable[[dict], None]] = None
        self.on_schedule_cancel_callback: Optional[Callable] = None

        # Status tracking
        self.last_publish_time = 0.0
        self.base_topic = config.get('base_topic', 'battery-charger')

    def connect(self) -> bool:
        """
        Connect to MQTT broker.

        Returns:
            True if connected successfully
        """
        try:
            client_id = self.config.get('client_id', 'battery-charger')
            self.client = mqtt.Client(client_id=client_id)

            # Set up callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

            # Set username/password if provided
            username = self.config.get('username', '')
            password = self.config.get('password', '')
            if username:
                self.client.username_pw_set(username, password)

            # Set Last Will and Testament
            lwt_topic = self.config.get('lwt_topic', f'{self.base_topic}/status/online')
            lwt_payload = self.config.get('lwt_payload', 'false')
            qos = self.config.get('qos', 1)
            retain = self.config.get('retain', True)
            self.client.will_set(lwt_topic, lwt_payload, qos=qos, retain=retain)

            # Connect to broker
            broker = self.config.get('broker', 'localhost')
            port = self.config.get('port', 1883)
            logger.info(f"Connecting to MQTT broker {broker}:{port}...")
            self.client.connect(broker, port, keepalive=60)

            # Start network loop in background thread
            self.client.loop_start()

            # Wait for connection (up to 5 seconds)
            timeout = time.time() + 5.0
            while not self.connected and time.time() < timeout:
                time.sleep(0.1)

            if self.connected:
                logger.info("MQTT connected successfully")
                return True
            else:
                logger.error("MQTT connection timeout")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self.client:
            try:
                # Publish offline status
                self._publish_online_status(False)

                # Stop loop and disconnect
                self.client.loop_stop()
                self.client.disconnect()
                logger.info("Disconnected from MQTT broker")
            except Exception as e:
                logger.error(f"Error during MQTT disconnect: {e}")

        self.connected = False

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker."""
        if rc == 0:
            self.connected = True
            logger.info("MQTT connected")

            # Publish online status
            self._publish_online_status(True)

            # Subscribe to command topics
            self._subscribe_commands()
        else:
            self.connected = False
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker."""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnect (code {rc})")
        else:
            logger.info("MQTT disconnected")

    def _on_message(self, client, userdata, msg):
        """Callback when message received."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8').strip()
            logger.debug(f"MQTT message: {topic} = {payload}")

            # Parse command topic
            if topic == f"{self.base_topic}/cmd/start":
                logger.info("MQTT command: START")
                if self.on_start_callback:
                    self.on_start_callback()

            elif topic == f"{self.base_topic}/cmd/stop":
                logger.info("MQTT command: STOP")
                if self.on_stop_callback:
                    self.on_stop_callback()

            elif topic == f"{self.base_topic}/cmd/mode":
                logger.info(f"MQTT command: SET MODE to {payload}")
                if self.on_mode_callback:
                    self.on_mode_callback(payload)

            elif topic == f"{self.base_topic}/cmd/current":
                try:
                    current = float(payload)
                    logger.info(f"MQTT command: SET CURRENT to {current}A")
                    if self.on_current_callback:
                        self.on_current_callback(current)
                except ValueError:
                    logger.error(f"Invalid current value: {payload}")

            elif topic == f"{self.base_topic}/cmd/profile":
                logger.info(f"MQTT command: SET PROFILE to {payload}")
                if self.on_profile_callback:
                    self.on_profile_callback(payload)

            elif topic == f"{self.base_topic}/cmd/schedule":
                logger.info(f"MQTT command: SCHEDULE charging")
                try:
                    # Parse JSON payload with schedule parameters
                    schedule_params = json.loads(payload)
                    if self.on_schedule_callback:
                        self.on_schedule_callback(schedule_params)
                except json.JSONDecodeError:
                    logger.error(f"Invalid schedule JSON: {payload}")

            elif topic == f"{self.base_topic}/cmd/schedule/cancel":
                logger.info("MQTT command: CANCEL schedule")
                if self.on_schedule_cancel_callback:
                    self.on_schedule_cancel_callback()

        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _subscribe_commands(self):
        """Subscribe to command topics."""
        qos = self.config.get('qos', 1)
        topics = [
            (f"{self.base_topic}/cmd/start", qos),
            (f"{self.base_topic}/cmd/stop", qos),
            (f"{self.base_topic}/cmd/mode", qos),
            (f"{self.base_topic}/cmd/current", qos),
            (f"{self.base_topic}/cmd/profile", qos),
            (f"{self.base_topic}/cmd/schedule", qos),
            (f"{self.base_topic}/cmd/schedule/cancel", qos),
        ]

        for topic, topic_qos in topics:
            self.client.subscribe(topic, topic_qos)
            logger.debug(f"Subscribed to {topic}")

    def _publish_online_status(self, online: bool):
        """Publish online/offline status."""
        topic = self.config.get('lwt_topic', f'{self.base_topic}/status/online')
        payload = 'true' if online else 'false'
        qos = self.config.get('qos', 1)
        retain = self.config.get('retain', True)
        self._publish(topic, payload, qos=qos, retain=retain)

    def _publish(self, topic: str, payload: str, qos: int = 1, retain: bool = False):
        """
        Publish message to topic.

        Args:
            topic: MQTT topic
            payload: Message payload
            qos: Quality of Service
            retain: Retain flag
        """
        if self.client and self.connected:
            try:
                self.client.publish(topic, payload, qos=qos, retain=retain)
                logger.debug(f"Published: {topic} = {payload}")
            except Exception as e:
                logger.error(f"Failed to publish to {topic}: {e}")

    def publish_status(self, status: dict):
        """
        Publish charger status.

        Args:
            status: Status dictionary from charging mode
        """
        if not self.connected:
            return

        # Check update interval
        update_interval = self.config.get('update_interval', 5.0)
        now = time.time()
        if now - self.last_publish_time < update_interval:
            return

        self.last_publish_time = now

        # Publish individual status fields
        qos = self.config.get('qos', 1)
        retain = self.config.get('retain', True)

        # Extract and publish fields
        fields = {
            'voltage': status.get('voltage', 0.0),
            'current': status.get('current', 0.0),
            'power': status.get('power', 0.0),
            'mode': status.get('mode', 'unknown'),
            'state': status.get('state', 'idle'),
            'stage': status.get('stage', ''),
            'elapsed': int(status.get('elapsed', 0)),
            'progress': int(status.get('progress', 0)),
            'ah_delivered': round(status.get('ah_delivered', 0.0), 3),
            'wh_delivered': round(status.get('wh_delivered', 0.0), 2),
            'ah_stored': round(status.get('ah_stored', 0.0), 3)
        }

        for key, value in fields.items():
            topic = f"{self.base_topic}/status/{key}"
            self._publish(topic, str(value), qos=qos, retain=retain)

        # Also publish as JSON for convenience (with rounded values)
        json_status = status.copy()
        json_status['elapsed'] = round(json_status.get('elapsed', 0), 1)  # Round to 0.1s
        json_status['progress'] = round(json_status.get('progress', 0), 1)  # Round to 0.1%
        json_status['ah_delivered'] = round(json_status.get('ah_delivered', 0.0), 3)  # 3 decimals
        json_status['wh_delivered'] = round(json_status.get('wh_delivered', 0.0), 2)  # 2 decimals
        json_status['ah_stored'] = round(json_status.get('ah_stored', 0.0), 3)  # 3 decimals

        json_topic = f"{self.base_topic}/status/json"
        json_payload = json.dumps(json_status)
        self._publish(json_topic, json_payload, qos=qos, retain=False)

    def set_command_callbacks(
        self,
        on_start: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        on_mode: Optional[Callable[[str], None]] = None,
        on_current: Optional[Callable[[float], None]] = None,
        on_profile: Optional[Callable[[str], None]] = None,
        on_schedule: Optional[Callable[[dict], None]] = None,
        on_schedule_cancel: Optional[Callable] = None
    ):
        """
        Set callbacks for MQTT commands.

        Args:
            on_start: Callback for start command
            on_stop: Callback for stop command
            on_mode: Callback for mode change (receives mode name)
            on_current: Callback for current change (receives current value)
            on_profile: Callback for battery profile change (receives profile name)
            on_schedule: Callback for scheduling charge (receives schedule params dict)
            on_schedule_cancel: Callback for canceling schedule
        """
        self.on_start_callback = on_start
        self.on_stop_callback = on_stop
        self.on_mode_callback = on_mode
        self.on_current_callback = on_current
        self.on_profile_callback = on_profile
        self.on_schedule_callback = on_schedule
        self.on_schedule_cancel_callback = on_schedule_cancel

    def is_connected(self) -> bool:
        """Check if connected to broker."""
        return self.connected
