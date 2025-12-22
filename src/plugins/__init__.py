"""
Plugin package for selfuse-tool.

The plugins package allows extending the selfuse-tool application by
placing additional Python files into this directory. Each plugin module
should define a subclass of :class:`Plugin` (defined in
``plugin_base.py``) and implement the :meth:`Plugin.start` method.

Plugins are discovered and loaded automatically at runtime via the
``PluginLoader`` defined in ``plugin_loader.py``.
"""
