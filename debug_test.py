
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Mock modules before import
import sys
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.mixer'] = MagicMock()
sys.modules['pystray'] = MagicMock()
sys.modules['customtkinter'] = MagicMock()

# Import the test class - NEED TO FIX IMPORT PATH
# Since we are running from root, we need to make sure we can import src
sys.path.insert(0, os.getcwd())

from tests.test_music_window import TestMusicWindowTreeview

if __name__ == '__main__':
    # Fix import in test_music_window potentially relying on relative path
    suite = unittest.TestSuite()
    suite.addTest(TestMusicWindowTreeview('test_display_songs_inserts_correct_data'))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
