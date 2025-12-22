import os
import importlib
import threading
from typing import Dict, List, Optional
from src.core.logger import logger
from src.plugins.plugin_base import Plugin

class PluginManager:
    """Manages plugin discovery, loading, and lifecycle."""

    def __init__(self, config_manager, app_context=None):
        self.config_manager = config_manager
        self.app_context = app_context
        self.plugins: Dict[str, Plugin] = {}  # Loaded plugins: name -> instance
        self.available_plugins: Dict[str, type] = {}  # Discovered classes: name -> class
        self.plugin_dir = os.path.dirname(__file__)

    def discover_plugins(self):
        """Scans the plugin directory for valid Plugin classes."""
        logger.info(f"Discovering plugins in {self.plugin_dir}")
        for filename in os.listdir(self.plugin_dir):
            if not filename.endswith(".py") or filename in {"__init__.py", "plugin_base.py", "plugin_manager.py", "plugin_loader.py"}:
                continue
            
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"src.plugins.{module_name}")
                
                # Find any class that inherits from Plugin
                found_plugin = False
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, Plugin) and attr is not Plugin:
                        # Found a valid plugin class
                        # Instantiate temporarily to get name
                        try:
                            temp_instance = attr()
                            self.available_plugins[temp_instance.name] = attr
                            logger.info(f"Discovered plugin: {temp_instance.name} ({module_name})")
                            found_plugin = True
                            break # Only load one plugin per file
                        except Exception as e:
                             logger.error(f"Failed to instantiate plugin class {attr_name} in {module_name}: {e}")
                
                if not found_plugin:
                    logger.warning(f"No valid Plugin subclass found in {module_name}")
            except Exception as e:
                logger.error(f"Failed to load plugin module {module_name}: {e}")

    def load_enabled_plugins(self):
        """Loads all plugins that are enabled in the configuration."""
        plugin_config = self.config_manager.get('plugins', {})
        
        for name, plugin_cls in self.available_plugins.items():
            # Default to plugin's default_enabled setting
            # We need to access the class property, but we only have class in available_plugins
            default_enabled = getattr(plugin_cls, 'default_enabled', False)
            # Check for property object if it's not instantiated (mix of property and class attr issue in python mock/abstract?)
            # Since default_enabled is a property on instance, but we need it from class. 
            # Ideally it should be a class attribute or we instantiate temp.
            # We instantiated temp in discover.
            # But we didn't store temp instances.
            # Let's just instantiate and check.
            try:
               temp = plugin_cls()
               default_enabled = temp.default_enabled
            except:
               default_enabled = False
               
            is_enabled = plugin_config.get(name, default_enabled)
            
            if is_enabled:
                self.load_plugin(name)

    def load_plugin(self, name: str) -> bool:
        """Instantiates and starts a plugin."""
        if name in self.plugins:
            logger.warning(f"Plugin {name} is already loaded.")
            return True
            
        plugin_cls = self.available_plugins.get(name)
        if not plugin_cls:
            logger.error(f"Plugin {name} not found.")
            return False
            
        try:
            plugin = plugin_cls()
            plugin.on_load(self.app_context)
            
            # Start in thread
            thread = threading.Thread(target=plugin.start, daemon=True, name=f"Plugin-{name}")
            thread.start()
            
            self.plugins[name] = plugin
            logger.info(f"Loaded and started plugin: {name}")
            return True
        except Exception as e:
            logger.exception(f"Failed to load plugin {name}: {e}")
            return False

    def unload_plugin(self, name: str) -> bool:
        """Stops and removes a plugin."""
        plugin = self.plugins.get(name)
        if not plugin:
            return False
            
        try:
            plugin.on_unload()
            del self.plugins[name]
            logger.info(f"Unloaded plugin: {name}")
            return True
        except Exception as e:
            logger.exception(f"Failed to unload plugin {name}: {e}")
            return False

    def set_plugin_enabled(self, name: str, enabled: bool):
        """Enable or disable a plugin and update config."""
        plugin_config = self.config_manager.config.get('plugins', {})
        plugin_config[name] = enabled
        self.config_manager.config['plugins'] = plugin_config
        self.config_manager._schedule_save()
        
        if enabled:
            if name not in self.plugins:
                self.load_plugin(name)
        else:
            if name in self.plugins:
                self.unload_plugin(name)

    def get_plugin(self, name: str) -> Optional[Plugin]:
        return self.plugins.get(name)
