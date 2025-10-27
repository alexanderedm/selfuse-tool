"""
Dynamic plugin loader for selfuse-tool.

The PluginLoader scans a directory for Python files (excluding
internal helper modules) and attempts to import each as a plugin.  If a
module defines a Plugin subclass, an instance of that class is
instantiated and stored.  Plugins are started via the start_all
method, which spins up a daemon thread for each plugin.
"""

from __future__ import annotations

import importlib
import os
import threading
from typing import List

from src.plugins.plugin_base import Plugin  # type: ignore
from src.core.logger import logger  # type: ignore


class PluginLoader:
    """Loader for discovering and starting plugins."""

    def __init__(self, plugin_dir: str) -> None:
        """Initialize with plugin directory path."""
        self.plugin_dir = plugin_dir
        self.plugins: List[Plugin] = []

    def load_plugins(self) -> None:
        """Discover and instantiate all plugin modules in plugin_dir."""
        if not os.path.isdir(self.plugin_dir):
            logger.warning(f"Plugin directory {self.plugin_dir} does not exist")
            return

        for filename in os.listdir(self.plugin_dir):
            if not filename.endswith(".py"):
                continue

            if filename in {"__init__.py", "plugin_base.py", "plugin_loader.py"}:
                continue

            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"src.plugins.{module_name}")
            except Exception as exc:
                logger.exception(f"Failed to import plugin module {module_name}: {exc}")
                continue

            plugin_cls = getattr(module, "Plugin", None)
            if plugin_cls is None:
                logger.warning(f"No Plugin class found in module {module_name}")
                continue

            if not issubclass(plugin_cls, Plugin):
                logger.warning(
                    f"Plugin class in {module_name} does not inherit from Plugin"
                )
                continue

            try:
                plugin_instance = plugin_cls()  # type: ignore
                self.plugins.append(plugin_instance)
                logger.info(f"Loaded plugin {module_name}")
            except Exception as exc:
                logger.exception(f"Failed to instantiate plugin {module_name}: {exc}")

    def start_all(self) -> None:
        """Start all loaded plugins in their own daemon threads."""
        for plugin in self.plugins:
            try:
                thread = threading.Thread(target=plugin.start, daemon=True)
                thread.start()
                logger.info(f"Started plugin {plugin.__class__.__name__}")
            except Exception as exc:
                logger.exception(f"Failed to start plugin {plugin}: {exc}")
