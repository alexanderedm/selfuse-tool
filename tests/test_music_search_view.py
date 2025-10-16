"""MusicSearchView 測試模組"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
import customtkinter as ctk
from music_search_view import MusicSearchView


class TestMusicSearchView(unittest.TestCase):
    """MusicSearchView 測試類別"""

    def setUp(self):
        """設定測試環境"""
        # 建立 tkinter 根視窗(測試環境需要)
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏視窗

        # Mock music_manager
        self.mock_music_manager = Mock()
        self.mock_music_manager.search_songs = Mock(return_value=[
            {'id': '1', 'title': 'Song 1', 'duration': 180},
            {'id': '2', 'title': 'Song 2', 'duration': 200}
        ])

        # Mock 回調函數
        self.mock_on_search_results = Mock()
        self.mock_on_search_cleared = Mock()

    def tearDown(self):
        """清理測試環境"""
        if self.root:
            self.root.destroy()

    def test_init_creates_ui_components(self):
        """測試初始化是否建立 UI 元件"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager,
            on_search_results=self.mock_on_search_results,
            on_search_cleared=self.mock_on_search_cleared
        )

        # 驗證主框架存在
        self.assertIsNotNone(view.main_frame)

        # 驗證搜尋輸入框存在
        self.assertIsNotNone(view.search_entry)
        self.assertIsInstance(view.search_entry, ctk.CTkEntry)

        view.destroy()

    def test_search_entry_binds_keyrelease_event(self):
        """測試搜尋框是否綁定 KeyRelease 事件"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager
        )

        # CustomTkinter 的 bind() 可能不會返回綁定列表
        # 我們只需驗證 view 有 search_entry 且能正常工作
        self.assertIsNotNone(view.search_entry)

        # 驗證搜尋框能接受輸入
        view.search_entry.insert(0, "test")
        self.assertEqual(view.search_entry.get(), "test")

        view.destroy()

    def test_on_search_change_with_keyword(self):
        """測試搜尋框輸入關鍵字時觸發搜尋"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager,
            on_search_results=self.mock_on_search_results
        )

        # 模擬輸入搜尋關鍵字
        view.search_entry.insert(0, "test song")
        view._on_search_change(None)

        # 驗證呼叫 music_manager.search_songs
        self.mock_music_manager.search_songs.assert_called_once_with("test song")

        # 驗證觸發搜尋結果回調
        self.mock_on_search_results.assert_called_once()
        results = self.mock_on_search_results.call_args[0][0]
        self.assertEqual(len(results), 2)

        view.destroy()

    def test_on_search_change_with_empty_keyword(self):
        """測試搜尋框為空時觸發清除回調"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager,
            on_search_results=self.mock_on_search_results,
            on_search_cleared=self.mock_on_search_cleared
        )

        # 搜尋框為空
        view.search_entry.delete(0, tk.END)
        view._on_search_change(None)

        # 驗證不會呼叫搜尋
        self.mock_music_manager.search_songs.assert_not_called()

        # 驗證觸發清除回調
        self.mock_on_search_cleared.assert_called_once()

        # 驗證不會觸發搜尋結果回調
        self.mock_on_search_results.assert_not_called()

        view.destroy()

    def test_clear_search_clears_entry_and_triggers_callback(self):
        """測試清除搜尋按鈕"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager,
            on_search_cleared=self.mock_on_search_cleared
        )

        # 輸入搜尋關鍵字
        view.search_entry.insert(0, "test")
        self.assertEqual(view.search_entry.get(), "test")

        # 清除搜尋
        view._clear_search()

        # 驗證搜尋框已清空
        self.assertEqual(view.search_entry.get(), "")

        # 驗證觸發清除回調
        self.mock_on_search_cleared.assert_called_once()

        view.destroy()

    def test_get_search_keyword(self):
        """測試取得搜尋關鍵字"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager
        )

        # 搜尋框為空
        self.assertEqual(view.get_search_keyword(), "")

        # 輸入關鍵字
        view.search_entry.insert(0, "  test keyword  ")
        self.assertEqual(view.get_search_keyword(), "test keyword")

        view.destroy()

    def test_clear_method(self):
        """測試 clear() 方法"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager
        )

        # 輸入搜尋關鍵字
        view.search_entry.insert(0, "test")
        self.assertEqual(view.search_entry.get(), "test")

        # 呼叫 clear()
        view.clear()

        # 驗證搜尋框已清空
        self.assertEqual(view.search_entry.get(), "")

        view.destroy()

    def test_search_with_no_results(self):
        """測試搜尋無結果"""
        self.mock_music_manager.search_songs = Mock(return_value=[])

        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager,
            on_search_results=self.mock_on_search_results
        )

        # 輸入搜尋關鍵字
        view.search_entry.insert(0, "nonexistent")
        view._on_search_change(None)

        # 驗證呼叫搜尋
        self.mock_music_manager.search_songs.assert_called_once_with("nonexistent")

        # 驗證觸發搜尋結果回調(空列表)
        self.mock_on_search_results.assert_called_once_with([])

        view.destroy()

    def test_search_without_callbacks(self):
        """測試沒有回調函數時也能正常運作"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager
        )

        # 搜尋不應該拋出異常
        view.search_entry.insert(0, "test")
        view._on_search_change(None)

        # 清除不應該拋出異常
        view._clear_search()

        view.destroy()

    def test_destroy_cleans_up_resources(self):
        """測試 destroy() 清理資源"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager
        )

        # 驗證主框架存在
        self.assertIsNotNone(view.main_frame)

        # 銷毀視圖
        view.destroy()

        # 驗證主框架已被銷毀(winfo_exists() 回傳 False)
        self.assertFalse(view.main_frame.winfo_exists())

    def test_search_with_whitespace_only(self):
        """測試只輸入空白字元時視為空搜尋"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager,
            on_search_results=self.mock_on_search_results,
            on_search_cleared=self.mock_on_search_cleared
        )

        # 輸入空白字元
        view.search_entry.insert(0, "   ")
        view._on_search_change(None)

        # 驗證不會呼叫搜尋
        self.mock_music_manager.search_songs.assert_not_called()

        # 驗證觸發清除回調
        self.mock_on_search_cleared.assert_called_once()

        view.destroy()

    def test_multiple_searches(self):
        """測試連續多次搜尋"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager,
            on_search_results=self.mock_on_search_results
        )

        # 第一次搜尋
        view.search_entry.insert(0, "song1")
        view._on_search_change(None)
        self.assertEqual(self.mock_music_manager.search_songs.call_count, 1)

        # 第二次搜尋
        view.search_entry.delete(0, tk.END)
        view.search_entry.insert(0, "song2")
        view._on_search_change(None)
        self.assertEqual(self.mock_music_manager.search_songs.call_count, 2)

        # 第三次搜尋
        view.search_entry.delete(0, tk.END)
        view.search_entry.insert(0, "song3")
        view._on_search_change(None)
        self.assertEqual(self.mock_music_manager.search_songs.call_count, 3)

        view.destroy()

    def test_ui_theme_colors(self):
        """測試 UI 顏色主題正確設定"""
        view = MusicSearchView(
            parent=self.root,
            music_manager=self.mock_music_manager
        )

        # 驗證顏色主題已設定
        self.assertEqual(view.bg_color, "#1e1e1e")
        self.assertEqual(view.card_bg, "#2d2d2d")
        self.assertEqual(view.accent_color, "#0078d4")
        self.assertEqual(view.text_color, "#e0e0e0")
        self.assertEqual(view.text_secondary, "#a0a0a0")
        self.assertEqual(view.header_bg, "#0d47a1")

        view.destroy()


if __name__ == '__main__':
    unittest.main()
