from typing import Dict, List, Any, Type, Optional
import logging
import importlib
import pkgutil
import inspect
import os
from heimdall.core.event_bus import EventBus
from heimdall.core.config import ConfigurationManager

class PluginInterface:
    """
    Interface that all plugins must implement.
    """
    def initialize(self) -> None:
        """
        Initialize the plugin.
        """
        raise NotImplementedError("Plugin must implement initialize method")
    
    def shutdown(self) -> None:
        """
        Shutdown the plugin.
        """
        raise NotImplementedError("Plugin must implement shutdown method")
    
    @property
    def name(self) -> str:
        """
        Get the name of the plugin.
        """
        raise NotImplementedError("Plugin must implement name property")

class PluginManager:
    """
    Manages the discovery, loading, and lifecycle of plugins.
    """
    def __init__(self, event_bus: EventBus, config_manager: ConfigurationManager):
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.plugins = {}
        
    def discover_plugins(self) -> None:
        """
        Discover available plugins.
        """
        self.logger.info("Discovering plugins")
        
        # Dynamically import plugin modules
        import heimdall.plugins
        
        plugin_package = heimdall.plugins
        
        for _, name, is_pkg in pkgutil.iter_modules(plugin_package.__path__, 
                                                 plugin_package.__name__ + '.'):
            if is_pkg:  # Only process subpackages
                try:
                    module = importlib.import_module(name)
                    
                    # Find plugin classes in the module
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if (inspect.isclass(item) and 
                            issubclass(item, PluginInterface) and 
                            item != PluginInterface):
                            
                            plugin_instance = item()
                            self.plugins[plugin_instance.name] = plugin_instance
                            self.logger.info(f"Discovered plugin: {plugin_instance.name}")
                except Exception as e:
                    self.logger.error(f"Error discovering plugin {name}: {e}")
        
    def initialize_plugins(self) -> None:
        """
        Initialize all discovered plugins.
        """
        self.logger.info("Initializing plugins")
        
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.initialize()
                self.logger.info(f"Initialized plugin: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Error initializing plugin {plugin_name}: {e}")
                
    def shutdown_plugins(self) -> None:
        """
        Shutdown all plugins.
        """
        self.logger.info("Shutting down plugins")
        
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.shutdown()
                self.logger.info(f"Shutdown plugin: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Error shutting down plugin {plugin_name}: {e}")
                
    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """
        Get a plugin by name.
        """
        return self.plugins.get(plugin_name)