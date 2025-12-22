import unittest
from unittest.mock import MagicMock, patch
import os
import sys
from src.plugins.plugin_manager import PluginManager
from src.plugins.plugin_base import Plugin

# Mock Plugin Implementation
class MockPlugin(Plugin):
    @property
    def name(self):
        return "mock_plugin"
    @property
    def version(self):
        return "1.0.0"
    def start(self):
        pass

class TestPluginManager(unittest.TestCase):
    def setUp(self):
        self.mock_config_manager = MagicMock()
        self.mock_config_manager.get.return_value = {}
        self.plugin_manager = PluginManager(self.mock_config_manager)
        
        # Inject our MockPlugin manually into available_plugins to avoid FS scan
        self.plugin_manager.available_plugins["mock_plugin"] = MockPlugin

    def test_load_plugin(self):
        success = self.plugin_manager.load_plugin("mock_plugin")
        self.assertTrue(success)
        self.assertIn("mock_plugin", self.plugin_manager.plugins)
        self.assertTrue(self.plugin_manager.plugins["mock_plugin"]._enabled)

    def test_unload_plugin(self):
        self.plugin_manager.load_plugin("mock_plugin")
        success = self.plugin_manager.unload_plugin("mock_plugin")
        self.assertTrue(success)
        self.assertNotIn("mock_plugin", self.plugin_manager.plugins)

    def test_set_plugin_enabled(self):
        # Initial config state
        self.mock_config_manager.config = {'plugins': {}}
        
        # Enable
        self.plugin_manager.set_plugin_enabled("mock_plugin", True)
        self.mock_config_manager.config['plugins']['mock_plugin'] = True
        self.mock_config_manager._schedule_save.assert_called()
        self.assertIn("mock_plugin", self.plugin_manager.plugins)
        
        # Disable
        self.plugin_manager.set_plugin_enabled("mock_plugin", False)
        self.assertNotIn("mock_plugin", self.plugin_manager.plugins)

    def test_load_enabled_plugins(self):
        # Mock config to have plugin enabled
        self.mock_config_manager.get.return_value = {'mock_plugin': True}
        
        self.plugin_manager.load_enabled_plugins()
        self.assertIn("mock_plugin", self.plugin_manager.plugins)

    def test_default_enabled(self):
        # Mock class with default_enabled = True
        class DefaultTruePlugin(Plugin):
            @property
            def name(self): return "true_plugin"
            @property
            def default_enabled(self): return True
            def start(self): pass
            
        self.plugin_manager.available_plugins["true_plugin"] = DefaultTruePlugin
        self.mock_config_manager.get.return_value = {} # No config
        
        self.plugin_manager.load_enabled_plugins()
        self.assertIn("true_plugin", self.plugin_manager.plugins)

if __name__ == '__main__':
    unittest.main()
