import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional, Dict, Any

class LoggingService:
    """
    Comprehensive logging infrastructure.
    """
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.root_logger = logging.getLogger()
        self.app_logger = logging.getLogger('heimdall')
        
    def initialize(self) -> None:
        """
        Initialize the logging system.
        """
        # Get configuration
        if self.config_manager:
            log_level_name = self.config_manager.get('app', 'logging_level', 'INFO')
            log_directory = self.config_manager.get('logging', 'directory', 
                                                  str(Path.home() / "Documents" / "Heimdall" / "logs"))
        else:
            log_level_name = 'INFO'
            log_directory = str(Path.home() / "Documents" / "Heimdall" / "logs")
            
        # Convert string log level to numeric value
        log_level = getattr(logging, log_level_name.upper(), logging.INFO)
        
        # Reset handlers
        self.root_logger.handlers = []
        
        # Configure root logger
        self.root_logger.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add console handler to root logger
        self.root_logger.addHandler(console_handler)
        
        # Create file handler for app-specific logs
        os.makedirs(log_directory, exist_ok=True)
        log_file = os.path.join(log_directory, 'app.log')
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # Add file handler to app logger
        self.app_logger.addHandler(file_handler)
        
        # Log initialization
        self.app_logger.info(f"Logging initialized (level={log_level_name})")
        
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger for a specific component.
        
        Args:
            name: The name of the logger
            
        Returns:
            A configured logger instance
        """
        return logging.getLogger(name)
        
    def set_level(self, level: str) -> None:
        """
        Set the logging level for the application.
        
        Args:
            level: The logging level to set (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR')
        """
        log_level = getattr(logging, level.upper(), None)
        if log_level is None:
            self.app_logger.warning(f"Invalid logging level: {level}")
            return
            
        self.root_logger.setLevel(log_level)
        for handler in self.root_logger.handlers:
            handler.setLevel(log_level)
            
        self.app_logger.setLevel(log_level)
        for handler in self.app_logger.handlers:
            handler.setLevel(log_level)
            
        self.app_logger.info(f"Logging level set to {level}")