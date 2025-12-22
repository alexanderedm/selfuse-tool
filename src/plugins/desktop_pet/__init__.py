"""
Desktop pet plugin for selfuse-tool.

This plugin displays a small animated character (a "desktop pet") on
screen using the Tkinter GUI toolkit. The character idles with a
looping animation and reacts to basic mouse interactions: hover, click,
and drag. Animation frames are loaded from PNG files in the adjacent
``assets`` directory. You can replace these images with your own
Live2D exports if you convert them into a sequence of PNG frames.

To use this plugin, drop the ``desktop_pet`` directory inside
``src/plugins``. The plugin loader will automatically detect it.
"""

from .desktop_pet import Plugin  # noqa: F401
