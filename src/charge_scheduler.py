#!/usr/bin/env python3
"""
Charge Scheduler
Allows scheduling charging sessions (start time, duration, etc.)
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScheduledCharge:
    """Scheduled charging session."""
    start_time: Optional[datetime] = None  # When to start (None = disabled)
    duration: Optional[int] = None  # Duration in seconds (None = unlimited)
    profile: Optional[str] = None  # Battery profile to use
    mode: Optional[str] = None  # Charging mode to use
    enabled: bool = False  # Is schedule active


class ChargeScheduler:
    """Manages charging schedules."""

    def __init__(self):
        """Initialize charge scheduler."""
        self.schedule = ScheduledCharge()
        self.on_start_callback: Optional[Callable] = None
        self.on_stop_callback: Optional[Callable] = None
        self.on_profile_callback: Optional[Callable[[str], None]] = None
        self.charge_started = False
        self.charge_start_time: Optional[datetime] = None

    def set_callbacks(
        self,
        on_start: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        on_profile: Optional[Callable[[str], None]] = None
    ):
        """
        Set callbacks for scheduler actions.

        Args:
            on_start: Callback to start charging
            on_stop: Callback to stop charging
            on_profile: Callback to change battery profile
        """
        self.on_start_callback = on_start
        self.on_stop_callback = on_stop
        self.on_profile_callback = on_profile

    def schedule_charge(
        self,
        start_time: Optional[datetime] = None,
        duration: Optional[int] = None,
        profile: Optional[str] = None,
        mode: Optional[str] = None
    ):
        """
        Schedule a charging session.

        Args:
            start_time: When to start (None = start immediately)
            duration: How long to charge in seconds (None = until complete)
            profile: Battery profile to use
            mode: Charging mode to use
        """
        self.schedule = ScheduledCharge(
            start_time=start_time,
            duration=duration,
            profile=profile,
            mode=mode,
            enabled=True
        )

        if start_time:
            logger.info(f"Charging scheduled for {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            if duration:
                logger.info(f"Duration: {duration}s ({duration/3600:.1f}h)")
        else:
            logger.info("Charging scheduled to start immediately")

        if profile:
            logger.info(f"Profile: {profile}")
        if mode:
            logger.info(f"Mode: {mode}")

    def cancel_schedule(self):
        """Cancel scheduled charging."""
        self.schedule.enabled = False
        logger.info("Charging schedule cancelled")

    def is_scheduled(self) -> bool:
        """Check if charging is scheduled."""
        return self.schedule.enabled

    def get_schedule_info(self) -> dict:
        """
        Get schedule information.

        Returns:
            Dictionary with schedule details
        """
        if not self.schedule.enabled:
            return {'enabled': False}

        info = {
            'enabled': True,
            'start_time': self.schedule.start_time.isoformat() if self.schedule.start_time else 'immediate',
            'duration': self.schedule.duration,
            'profile': self.schedule.profile,
            'mode': self.schedule.mode
        }

        # Calculate time until start
        if self.schedule.start_time:
            now = datetime.now()
            if self.schedule.start_time > now:
                time_until = (self.schedule.start_time - now).total_seconds()
                info['time_until_start'] = int(time_until)
            else:
                info['time_until_start'] = 0

        # Calculate time remaining
        if self.charge_started and self.schedule.duration:
            elapsed = (datetime.now() - self.charge_start_time).total_seconds()
            remaining = self.schedule.duration - elapsed
            info['time_remaining'] = max(0, int(remaining))

        return info

    def update(self):
        """
        Update scheduler (call this periodically).

        Checks if scheduled charge should start or stop.
        """
        if not self.schedule.enabled:
            return

        now = datetime.now()

        # Check if it's time to start
        if not self.charge_started:
            should_start = False

            if self.schedule.start_time is None:
                # Start immediately
                should_start = True
            elif self.schedule.start_time <= now:
                # Start time reached
                should_start = True

            if should_start:
                logger.info("Starting scheduled charge")

                # Switch profile if specified
                if self.schedule.profile and self.on_profile_callback:
                    logger.info(f"Switching to profile: {self.schedule.profile}")
                    self.on_profile_callback(self.schedule.profile)
                    time.sleep(1)  # Give it time to switch

                # Start charging
                if self.on_start_callback:
                    self.on_start_callback()
                    self.charge_started = True
                    self.charge_start_time = now

        # Check if it's time to stop (duration limit)
        elif self.schedule.duration:
            elapsed = (now - self.charge_start_time).total_seconds()
            if elapsed >= self.schedule.duration:
                logger.info(f"Scheduled charge duration reached ({elapsed:.0f}s)")
                if self.on_stop_callback:
                    self.on_stop_callback()

                # Disable schedule (one-time)
                self.schedule.enabled = False
                self.charge_started = False

    def parse_duration(self, duration_str: str) -> Optional[int]:
        """
        Parse duration string to seconds.

        Supports:
        - "1h" = 1 hour
        - "30m" = 30 minutes
        - "3600" = 3600 seconds

        Args:
            duration_str: Duration string

        Returns:
            Duration in seconds or None if invalid
        """
        try:
            duration_str = duration_str.strip().lower()

            if duration_str.endswith('h'):
                hours = float(duration_str[:-1])
                return int(hours * 3600)
            elif duration_str.endswith('m'):
                minutes = float(duration_str[:-1])
                return int(minutes * 60)
            else:
                return int(duration_str)

        except (ValueError, AttributeError):
            logger.error(f"Invalid duration format: {duration_str}")
            return None

    def parse_start_time(self, time_str: str) -> Optional[datetime]:
        """
        Parse start time string to datetime.

        Supports:
        - "now" = immediate
        - "14:30" = today at 14:30 (or tomorrow if already passed)
        - "2025-11-02 14:30" = specific date and time

        Args:
            time_str: Time string

        Returns:
            Datetime or None if invalid/immediate
        """
        try:
            time_str = time_str.strip().lower()

            if time_str == "now":
                return None  # Immediate

            now = datetime.now()

            # Try HH:MM format
            if ':' in time_str and len(time_str) <= 5:
                hour, minute = map(int, time_str.split(':'))
                start_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                # If time already passed today, schedule for tomorrow
                if start_time <= now:
                    start_time += timedelta(days=1)

                return start_time

            # Try full datetime format
            return datetime.fromisoformat(time_str)

        except (ValueError, AttributeError):
            logger.error(f"Invalid time format: {time_str}")
            return None
