from typing import Dict, List, Any, Optional
import logging
import json
import os
from pathlib import Path

class ConfigurationManager:
    """
    Handles application configuration from multiple sources.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {}
        self.load_defaults()
        
    def load_defaults(self) -> None:
        """
        Load default configuration values.
        """
        self.config = {
            "app": {
                "name": "Heimdall",
                "version": "0.1.0",
                "logging_level": "INFO"
            },
            "plugins": {
                "enabled": ["finance"],
                "paths": ["plugins"]
            },
            "ui": {
                "theme": "light",
                "window_width": 1200,
                "window_height": 800
            },
            "export": {
                "default_format": "csv",
                "default_path": str(Path.home() / "Documents" / "Heimdall" / "exports")
            },
            "r_integration": {
                "enabled": True,
                "timeout": 30  # seconds
            }
        }
        
    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from a file.
        """
        try:
            with open(file_path, 'r') as f:
                file_config = json.load(f)
                self._merge_config(file_config)
            self.logger.info(f"Loaded configuration from {file_path}")
        except Exception as e:
            self.logger.error(f"Error loading configuration from {file_path}: {e}")
            
    def load_from_env(self) -> None:
        """
        Load configuration from environment variables.
        Env vars should be in the format APP_SECTION_KEY=value
        """
        for key, value in os.environ.items():
            if key.startswith("APP_"):
                parts = key.lower().split("_")
                if len(parts) >= 3:
                    section = parts[1]
                    section_key = "_".join(parts[2:])
                    if section in self.config:
                        self.config[section][section_key] = self._convert_value(value)
                        self.logger.debug(f"Loaded config from env: {section}.{section_key}")
                        
    def _convert_value(self, value: str) -> Any:
        """
        Try to convert a string value to the appropriate type.
        """
        # Try to convert to Boolean
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False
            
        # Try to convert to Integer
        try:
            return int(value)
        except ValueError:
            pass
            
        # Try to convert to Float
        try:
            return float(value)
        except ValueError:
            pass
            
        # Return as string
        return value
        
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Merge a new configuration dictionary with the existing config.
        """
        for section, section_config in new_config.items():
            if section not in self.config:
                self.config[section] = {}
                
            if isinstance(section_config, dict):
                for key, value in section_config.items():
                    self.config[section][key] = value
            else:
                self.config[section] = section_config
                
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        """
        try:
            return self.config[section][key]
        except KeyError:
            return default
            
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value.
        """
        if section not in self.config:
            self.config[section] = {}
            
        self.config[section][key] = value
        
    def save_to_file(self, file_path: str) -> None:
        """
        Save configuration to a file.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info(f"Saved configuration to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving configuration to {file_path}: {e}")