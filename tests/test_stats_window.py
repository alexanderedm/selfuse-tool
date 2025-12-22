"""使用統計視窗測試"""
import unittest
from unittest.mock import Mock, MagicMock, patch, call
import tkinter as tk
import customtkinter as ctk
from src.windows.stats_window import StatsWindow


class TestStatsWindow(unittest.TestCase):
    """StatsWindow 測試類別"""

    def setUp(self):
        """測試前準備"""
        self.config_manager = Mock()
        self.tk_root = None  # 在沒有 GUI 的環境下測試

    def test_init(self):
        """測試初始化"""
        window = StatsWindow(self.config_manager, self.tk_root)
        self.assertEqual(window.config_manager, self.config_manager)
        self.assertIsNone(window.window)
        self.assertIsNone(window.tk_root)

    @patch('src.windows.stats_window.tk.Tk')
    @patch('src.windows.stats_window.ctk.CTkToplevel')
    def test_show_creates_window_if_none(self, mock_toplevel, mock_tk):
        """測試當視窗不存在時建立新視窗"""
        # 準備模擬物件
        mock_window = MagicMock()
        mock_tk.return_value = mock_window

        self.config_manager.get_usage_stats.return_value = {}

        window = StatsWindow(self.config_manager)

        # 模擬 mainloop 不進入迴圈
        mock_window.mainloop = Mock()

        window.show()

        # 驗證建立了視窗
        mock_tk.assert_called_once()
        self.assertIsNotNone(window.window)

    @patch('src.windows.stats_window.ctk.CTkToplevel')
    def test_show_raises_existing_window(self, mock_toplevel):
        """測試當視窗已存在時只提升視窗"""
        mock_window = MagicMock()

        window = StatsWindow(self.config_manager, tk.Tk())
        window.window = mock_window

        window.show()

        # 驗證只呼叫 lift 和 focus_force
        mock_window.lift.assert_called_once()
        mock_window.focus_force.assert_called_once()
        # 不應該建立新視窗
        mock_toplevel.assert_not_called()

    @patch('src.windows.stats_window.tk.Tk')
    def test_show_with_no_stats(self, mock_tk):
        """測試無統計資料時的顯示"""
        mock_window = MagicMock()
        mock_tk.return_value = mock_window
        mock_window.mainloop = Mock()

        # 回傳空統計資料
        self.config_manager.get_usage_stats.return_value = {}

        window = StatsWindow(self.config_manager)
        window.show()

        # 驗證有呼叫 get_usage_stats
        self.config_manager.get_usage_stats.assert_called_once()

    @patch('src.windows.stats_window.tk.Tk')
    def test_show_with_stats(self, mock_tk):
        """測試有統計資料時的顯示"""
        mock_window = MagicMock()
        mock_tk.return_value = mock_window
        mock_window.mainloop = Mock()

        # 準備測試資料
        stats = {
            'device1': {
                'name': 'Device 1',
                'total_seconds': 3600,
                'switch_count': 10
            },
            'device2': {
                'name': 'Device 2',
                'total_seconds': 1800,
                'switch_count': 5
            }
        }
        self.config_manager.get_usage_stats.return_value = stats

        window = StatsWindow(self.config_manager)
        window.show()

        # 驗證有呼叫 get_usage_stats
        self.config_manager.get_usage_stats.assert_called_once()

    def test_format_time_seconds(self):
        """測試秒數格式化"""
        window = StatsWindow(self.config_manager)
        self.assertEqual(window._format_time(30), "30 秒")

    def test_format_time_minutes(self):
        """測試分鐘格式化"""
        window = StatsWindow(self.config_manager)
        self.assertEqual(window._format_time(90), "1 分 30 秒")
        self.assertEqual(window._format_time(3599), "59 分 59 秒")

    def test_format_time_hours(self):
        """測試小時格式化"""
        window = StatsWindow(self.config_manager)
        self.assertEqual(window._format_time(3600), "1 小時 0 分")
        self.assertEqual(window._format_time(7200), "2 小時 0 分")
        self.assertEqual(window._format_time(5400), "1 小時 30 分")

    def test_format_time_days(self):
        """測試天數格式化"""
        window = StatsWindow(self.config_manager)
        self.assertEqual(window._format_time(86400), "1 天 0 小時")
        self.assertEqual(window._format_time(90000), "1 天 1 小時")
        self.assertEqual(window._format_time(172800), "2 天 0 小時")

    def test_close_window(self):
        """測試關閉視窗"""
        mock_window = MagicMock()
        window = StatsWindow(self.config_manager)
        window.window = mock_window

        window._close_window()

        # 驗證視窗被銷毀
        mock_window.destroy.assert_called_once()
        self.assertIsNone(window.window)

    def test_close_window_when_none(self):
        """測試當視窗為 None 時關閉不出錯"""
        window = StatsWindow(self.config_manager)
        window.window = None

        # 不應該拋出異常
        window._close_window()
        self.assertIsNone(window.window)


if __name__ == '__main__':
    unittest.main()
