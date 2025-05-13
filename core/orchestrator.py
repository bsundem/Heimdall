from typing import Dict, List, Any, Optional
import logging
from heimdall.core.plugin_manager import PluginManager
from heimdall.core.event_bus import EventBus
from heimdall.core.config import ConfigurationManager

class ApplicationOrchestrator:
    """
    Responsible for initializing and coordinating all system components.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigurationManager()
        self.event_bus = EventBus()
        self.plugin_manager = PluginManager(self.event_bus, self.config_manager)
        self.services = {}
        
    def initialize(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the application with the provided configuration.
        """
        self.logger.info("Initializing application")
        
        # Load configuration
        if config_path:
            self.config_manager.load_from_file(config_path)
        
        # Set up event bus
        self.event_bus.initialize()
        
        # Discover and initialize plugins
        self.plugin_manager.discover_plugins()
        self.plugin_manager.initialize_plugins()
        
        self.logger.info("Application initialized successfully")
        
    def shutdown(self) -> None:
        """
        Cleanly shut down the application.
        """
        self.logger.info("Shutting down application")
        
        # Shutdown plugins
        self.plugin_manager.shutdown_plugins()
        
        # Shutdown event bus
        self.event_bus.shutdown()
        
        self.logger.info("Application shutdown complete")
        
    def get_service(self, service_name: str) -> Any:
        """
        Get a service from the service registry.
        """
        return self.services.get(service_name)
    
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """
        Register a service in the service registry.
        """
        self.services[service_name] = service_instance
        self.logger.debug(f"Service registered: {service_name}")