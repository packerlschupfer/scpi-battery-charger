#!/usr/bin/env python3
"""
Battery Profile Manager
Allows dynamic switching between battery configurations
"""

import os
import logging
import yaml
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class BatteryProfileManager:
    """Manages battery charging profiles."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize battery profile manager.

        Args:
            config_dir: Directory containing battery config files
        """
        self.config_dir = Path(config_dir)
        self.profiles: Dict[str, Path] = {}
        self.current_profile: Optional[str] = None
        self.current_config: Optional[dict] = None

        # Discover available profiles
        self._discover_profiles()

    def _discover_profiles(self):
        """Scan config directory for battery profiles."""
        if not self.config_dir.exists():
            logger.warning(f"Config directory not found: {self.config_dir}")
            return

        # Look for YAML config files
        for config_file in self.config_dir.glob("charging_config*.yaml"):
            # Extract profile name from filename
            # charging_config_lucas_44ah.yaml → lucas_44ah
            # charging_config.yaml → default
            name = config_file.stem.replace("charging_config_", "").replace("charging_config", "default")
            if not name:
                name = "default"

            self.profiles[name] = config_file
            logger.debug(f"Found battery profile: {name} -> {config_file}")

        logger.info(f"Discovered {len(self.profiles)} battery profiles: {list(self.profiles.keys())}")

    def list_profiles(self) -> List[str]:
        """
        Get list of available battery profiles.

        Returns:
            List of profile names
        """
        return sorted(self.profiles.keys())

    def get_profile_info(self, profile_name: str) -> Optional[Dict]:
        """
        Get information about a battery profile.

        Args:
            profile_name: Name of profile

        Returns:
            Dictionary with profile info (battery specs, charging params)
        """
        if profile_name not in self.profiles:
            return None

        try:
            config = self.load_profile(profile_name)
            if not config:
                return None

            battery = config.get('battery', {})
            charging = config.get('charging', {})
            default_mode = charging.get('default_mode', 'IUoU')
            mode_config = charging.get(default_mode, {})

            return {
                'name': profile_name,
                'model': battery.get('model', 'Unknown'),
                'type': battery.get('type', 'Unknown'),
                'capacity': battery.get('capacity', 0),
                'chemistry': battery.get('chemistry', 'Unknown'),
                'default_mode': default_mode,
                'bulk_current': mode_config.get('bulk_current', 0),
                'absorption_voltage': mode_config.get('absorption_voltage', 0),
                'float_voltage': mode_config.get('float_voltage', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get profile info for {profile_name}: {e}")
            return None

    def load_profile(self, profile_name: str) -> Optional[dict]:
        """
        Load a battery profile configuration.

        Args:
            profile_name: Name of profile to load

        Returns:
            Configuration dictionary or None if failed
        """
        if profile_name not in self.profiles:
            logger.error(f"Profile not found: {profile_name}")
            logger.info(f"Available profiles: {list(self.profiles.keys())}")
            return None

        config_path = self.profiles[profile_name]

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            self.current_profile = profile_name
            self.current_config = config
            logger.info(f"Loaded battery profile: {profile_name} from {config_path}")
            return config

        except Exception as e:
            logger.error(f"Failed to load profile {profile_name}: {e}")
            return None

    def get_current_profile(self) -> Optional[str]:
        """Get name of currently loaded profile."""
        return self.current_profile

    def get_current_config(self) -> Optional[dict]:
        """Get currently loaded configuration."""
        return self.current_config

    def profile_exists(self, profile_name: str) -> bool:
        """Check if a profile exists."""
        return profile_name in self.profiles

    def get_profile_path(self, profile_name: str) -> Optional[Path]:
        """Get file path for a profile."""
        return self.profiles.get(profile_name)
