"""
Base classes and interfaces for selfuse-tool plugins.

Plugins should inherit from :class:`Plugin` and implement the
 :meth:`start` method to define their functionality.  The plugin
 loader will call :meth:`start` in a separate daemon thread.
"""

from abc import ABC, abstractmethod


class Plugin(ABC):
    """Abstract base class for all plugins."""

    @abstractmethod
    def start(self) -> None:
        """Start the plugin.

        This method will be invoked by the plugin loader in a separate
        daemon thread.  Override this method in subclasses to perform
        whatever initialization or long-running tasks your plugin needs.
        """
        raise NotImplementedError("Plugin subclasses must implement start()")

    def stop(self) -> None:
        """Optional clean-up method.

        Plugins that need to perform clean-up work when the application
        shuts down can override this method.  The default implementation
        does nothing.
        """
        # This method is intentionally left blank so that subclasses only
        # override it when necessary.
        return
