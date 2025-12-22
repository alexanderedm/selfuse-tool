"""
Base classes and interfaces for selfuse-tool plugins.

Plugins should inherit from :class:`Plugin` and implement the
 :meth:`start` method to define their functionality.  The plugin
 loader will call :meth:`start` in a separate daemon thread.
"""

from abc import ABC, abstractmethod


class Plugin(ABC):
    """Abstract base class for all plugins."""
    
    def __init__(self):
        self.context = None  # Will be set by PluginManager
        self._enabled = False

    @property
    def name(self) -> str:
        """Plugin name (unique identifier)."""
        raise NotImplementedError


    @property
    def version(self) -> str:
        """Plugin version."""
        return "0.1.0"

    @property
    def description(self) -> str:
        """Plugin description."""
        return ""

    @property
    def default_enabled(self) -> bool:
        """Whether the plugin is enabled by default."""
        return False

    @abstractmethod
    def start(self) -> None:
        """Start the plugin main logic (daemon thread)."""
        pass

    def stop(self) -> None:
        """Stop the plugin."""
        pass

    def on_load(self, context) -> None:
        """Called when the plugin is loaded/enabled.
        
        Args:
           context: The application context (usually PluginManager or App)
        """
        self.context = context
        self._enabled = True

    def on_unload(self) -> None:
        """Called when the plugin is unloaded/disabled."""
        self.stop()
        self._enabled = False

    def get_menu_items(self) -> list:
        """Return a list of pystray.MenuItem objects to add to the main menu."""
        return []

