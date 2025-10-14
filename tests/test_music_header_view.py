"""MusicHeaderView 模組的測試"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
from music_header_view import MusicHeaderView


class TestMusicHeaderView(unittest.TestCase):
    """測試 MusicHeaderView 類別"""

    def setUp(self):
        """設定測試環境"""
        self.root = tk.Tk()
        self.parent = tk.Frame(self.root)
        self.on_download_click = Mock()
        self.on_playlist_click = Mock()
        self.on_history_click = Mock()
        self.on_most_played_click = Mock()

    def tearDown(self):
        """清理測試環境"""
        try:
            self.root.destroy()
        except:
            pass

    def test_init_creates_header_view(self):
        """測試初始化建立 MusicHeaderView"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        self.assertIsNotNone(view)
        self.assertEqual(view.parent, self.parent)

    def test_creates_header_frame(self):
        """測試建立 header_frame"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        self.assertIsNotNone(view.header_frame)
        self.assertIsInstance(view.header_frame, tk.Frame)

    def test_creates_title_label(self):
        """測試建立標題標籤"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        self.assertIsNotNone(view.title_label)
        self.assertIsInstance(view.title_label, tk.Label)
        self.assertIn("音樂播放器", view.title_label.cget("text"))

    def test_creates_download_button(self):
        """測試建立下載按鈕"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        self.assertIsNotNone(view.download_button)
        self.assertIsInstance(view.download_button, tk.Button)
        self.assertIn("下載", view.download_button.cget("text"))

    def test_creates_most_played_button(self):
        """測試建立最常播放按鈕"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        self.assertIsNotNone(view.most_played_button)
        self.assertIsInstance(view.most_played_button, tk.Button)
        self.assertIn("最常播放", view.most_played_button.cget("text"))

    def test_creates_playlist_button(self):
        """測試建立播放列表按鈕"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        self.assertIsNotNone(view.playlist_button)
        self.assertIsInstance(view.playlist_button, tk.Button)
        self.assertIn("播放列表", view.playlist_button.cget("text"))

    def test_creates_history_button(self):
        """測試建立播放歷史按鈕"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        self.assertIsNotNone(view.history_button)
        self.assertIsInstance(view.history_button, tk.Button)
        self.assertIn("播放歷史", view.history_button.cget("text"))

    def test_download_button_triggers_callback(self):
        """測試下載按鈕觸發回調"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        # 觸發按鈕點擊
        view.download_button.invoke()
        # 驗證回調被呼叫
        self.on_download_click.assert_called_once()

    def test_most_played_button_triggers_callback(self):
        """測試最常播放按鈕觸發回調"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        # 觸發按鈕點擊
        view.most_played_button.invoke()
        # 驗證回調被呼叫
        self.on_most_played_click.assert_called_once()

    def test_playlist_button_triggers_callback(self):
        """測試播放列表按鈕觸發回調"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        # 觸發按鈕點擊
        view.playlist_button.invoke()
        # 驗證回調被呼叫
        self.on_playlist_click.assert_called_once()

    def test_history_button_triggers_callback(self):
        """測試播放歷史按鈕觸發回調"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        # 觸發按鈕點擊
        view.history_button.invoke()
        # 驗證回調被呼叫
        self.on_history_click.assert_called_once()

    def test_header_frame_packs_correctly(self):
        """測試 header_frame 正確打包"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        # 獲取 pack_info
        pack_info = view.header_frame.pack_info()
        self.assertEqual(pack_info['fill'], 'x')

    def test_destroy_cleans_up_resources(self):
        """測試 destroy 方法清理資源"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        # 確保元件存在
        self.assertTrue(view.header_frame.winfo_exists())
        # 呼叫 destroy
        view.destroy()
        # 驗證元件引用已被清空
        self.assertIsNone(view.header_frame)
        self.assertIsNone(view.title_label)
        self.assertIsNone(view.download_button)
        self.assertIsNone(view.most_played_button)
        self.assertIsNone(view.playlist_button)
        self.assertIsNone(view.history_button)

    def test_callbacks_are_optional(self):
        """測試回調參數是可選的"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=None,
            on_playlist_click=None,
            on_history_click=None,
            on_most_played_click=None
        )
        self.assertIsNotNone(view)
        # 按鈕應該存在但不執行任何操作
        view.download_button.invoke()  # 不應該拋出異常

    def test_button_styling_is_consistent(self):
        """測試按鈕樣式一致性"""
        view = MusicHeaderView(
            self.parent,
            on_download_click=self.on_download_click,
            on_playlist_click=self.on_playlist_click,
            on_history_click=self.on_history_click,
            on_most_played_click=self.on_most_played_click
        )
        # 檢查所有按鈕都有 borderwidth=0
        self.assertEqual(view.download_button.cget("borderwidth"), 0)
        self.assertEqual(view.most_played_button.cget("borderwidth"), 0)
        self.assertEqual(view.playlist_button.cget("borderwidth"), 0)
        self.assertEqual(view.history_button.cget("borderwidth"), 0)


if __name__ == '__main__':
    unittest.main()
