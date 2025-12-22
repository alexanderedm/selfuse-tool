
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

from src.core.config_manager import ConfigManager
from src.plugins.plugin_manager import PluginManager
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def test_discovery():
    cm = ConfigManager()
    pm = PluginManager(cm)
    pm.discover_plugins()
    
    print(f"Discovered {len(pm.available_plugins)} plugins:")
    for name, cls in pm.available_plugins.items():
        print(f" - {name}: {cls}")

if __name__ == "__main__":
    test_discovery()
