from typing import Dict, List, Any, Type, Optional
import logging
import importlib
import pkgutil
import inspect
import os
# Update imports to use relative paths
from core.event_bus import EventBus
from core.config import ConfigurationManager

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
        
        try:
            # Try to import plugins package in a way that works both with and without proper Python package setup
            try:
                import plugins
                plugin_package = plugins
            except ImportError:
                # If that fails, try the longer path
                try:
                    import heimdall.plugins
                    plugin_package = heimdall.plugins
                except ImportError:
                    # Last resort: try relative import
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    plugins_dir = os.path.join(os.path.dirname(current_dir), "plugins")
                    
                    # Manually load plugins
                    self.logger.info(f"Looking for plugins in {plugins_dir}")
                    if os.path.exists(plugins_dir) and os.path.isdir(plugins_dir):
                        for item in os.listdir(plugins_dir):
                            plugin_dir = os.path.join(plugins_dir, item)
                            if os.path.isdir(plugin_dir) and os.path.exists(os.path.join(plugin_dir, "__init__.py")):
                                try:
                                    self.logger.info(f"Found potential plugin: {item}")
                                    # Try to import the plugin module
                                    spec = importlib.util.spec_from_file_location(
                                        f"plugins.{item}", 
                                        os.path.join(plugin_dir, "__init__.py")
                                    )
                                    module = importlib.util.module_from_spec(spec)
                                    spec.loader.exec_module(module)
                                    
                                    # Find plugin classes in the module
                                    for attr_name in dir(module):
                                        attr = getattr(module, attr_name)
                                        if (inspect.isclass(attr) and 
                                            issubclass(attr, PluginInterface) and 
                                            attr != PluginInterface):
                                            
                                            plugin_instance = attr()
                                            self.plugins[plugin_instance.name] = plugin_instance
                                            self.logger.info(f"Discovered plugin: {plugin_instance.name}")
                                except Exception as e:
                                    self.logger.error(f"Error loading plugin {item}: {e}")
                    return
            
            # If we successfully imported the plugin_package, use the standard approach
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
        except Exception as e:
            self.logger.error(f"Error during plugin discovery: {e}")
        
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