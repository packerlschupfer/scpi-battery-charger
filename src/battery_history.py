#!/usr/bin/env python3
"""
Battery History & Health Tracking
Tracks charge cycles, capacity, and battery health over time
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class BatteryHistoryTracker:
    """Tracks battery charge history and health."""

    def __init__(self, history_file: str = "battery_history.json"):
        """
        Initialize battery history tracker.

        Args:
            history_file: Path to history JSON file
        """
        self.history_file = Path(history_file)
        self.history: Dict[str, List[dict]] = {}
        self._load_history()

    def _load_history(self):
        """Load history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
                logger.info(f"Loaded battery history from {self.history_file}")
            except Exception as e:
                logger.error(f"Failed to load history: {e}")
                self.history = {}
        else:
            logger.info("No existing history file, starting fresh")
            self.history = {}

    def _save_history(self):
        """Save history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.debug(f"Saved battery history to {self.history_file}")
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def record_charge_session(
        self,
        battery_model: str,
        start_voltage: float,
        end_voltage: float,
        ah_delivered: float,
        wh_delivered: float,
        duration: int,
        mode: str,
        success: bool = True
    ):
        """
        Record a charging session.

        Args:
            battery_model: Battery model/profile name
            start_voltage: Starting voltage
            end_voltage: Ending voltage
            ah_delivered: Amp-hours delivered
            wh_delivered: Watt-hours delivered
            duration: Charging duration in seconds
            mode: Charging mode used
            success: Whether charge completed successfully
        """
        session = {
            'timestamp': datetime.now().isoformat(),
            'start_voltage': round(start_voltage, 3),
            'end_voltage': round(end_voltage, 3),
            'ah_delivered': round(ah_delivered, 3),
            'wh_delivered': round(wh_delivered, 2),
            'duration': duration,
            'mode': mode,
            'success': success
        }

        # Initialize battery if not exists
        if battery_model not in self.history:
            self.history[battery_model] = []

        # Add session
        self.history[battery_model].append(session)
        logger.info(f"Recorded charge session for {battery_model}: {ah_delivered:.2f}Ah in {duration/3600:.1f}h")

        # Save to file
        self._save_history()

    def get_battery_stats(self, battery_model: str) -> Optional[Dict]:
        """
        Get statistics for a battery.

        Args:
            battery_model: Battery model/profile name

        Returns:
            Dictionary with statistics or None
        """
        if battery_model not in self.history:
            return None

        sessions = self.history[battery_model]
        if not sessions:
            return None

        total_sessions = len(sessions)
        successful_sessions = sum(1 for s in sessions if s.get('success', True))

        total_ah = sum(s['ah_delivered'] for s in sessions)
        total_wh = sum(s['wh_delivered'] for s in sessions)
        avg_ah = total_ah / total_sessions if total_sessions > 0 else 0

        # Get recent sessions (last 10)
        recent = sessions[-10:]
        recent_avg_ah = sum(s['ah_delivered'] for s in recent) / len(recent) if recent else 0

        # Estimate health (capacity degradation)
        # Compare recent average to overall average
        if avg_ah > 0:
            health_estimate = (recent_avg_ah / avg_ah) * 100
        else:
            health_estimate = 100

        return {
            'battery': battery_model,
            'total_sessions': total_sessions,
            'successful_sessions': successful_sessions,
            'total_ah_delivered': round(total_ah, 2),
            'total_wh_delivered': round(total_wh, 2),
            'avg_ah_per_session': round(avg_ah, 2),
            'recent_avg_ah': round(recent_avg_ah, 2),
            'estimated_health': round(min(health_estimate, 100), 1),
            'last_charge': sessions[-1]['timestamp'] if sessions else None
        }

    def get_all_batteries(self) -> List[str]:
        """Get list of all tracked batteries."""
        return list(self.history.keys())

    def get_charge_history(self, battery_model: str, limit: int = 20) -> List[dict]:
        """
        Get charge history for a battery.

        Args:
            battery_model: Battery model/profile name
            limit: Maximum number of sessions to return

        Returns:
            List of charge sessions (most recent first)
        """
        if battery_model not in self.history:
            return []

        sessions = self.history[battery_model]
        return list(reversed(sessions[-limit:]))

    def export_csv(self, battery_model: str, output_file: str):
        """
        Export battery history to CSV.

        Args:
            battery_model: Battery model/profile name
            output_file: Output CSV file path
        """
        import csv

        if battery_model not in self.history:
            logger.error(f"No history for battery: {battery_model}")
            return

        sessions = self.history[battery_model]

        try:
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['timestamp', 'start_voltage', 'end_voltage',
                                'ah_delivered', 'wh_delivered', 'duration', 'mode', 'success']
                )
                writer.writeheader()
                writer.writerows(sessions)

            logger.info(f"Exported {len(sessions)} sessions to {output_file}")

        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
