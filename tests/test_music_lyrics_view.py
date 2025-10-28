"""測試音樂歌詞視圖模組"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
import customtkinter as ctk
from src.music.views.music_lyrics_view import MusicLyricsView


class TestMusicLyricsView(unittest.TestCase):
    """測試 MusicLyricsView 類別"""

    def setUp(self):
        """測試前準備"""
        # 創建測試用的 Tk 根視窗
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏窗口
        self.parent_frame = tk.Frame(self.root)

        # 創建回調
        self.on_lyric_click = Mock()

        # 創建 MusicLyricsView 實例
        self.view = MusicLyricsView(
            parent_frame=self.parent_frame,
            on_lyric_click=self.on_lyric_click
        )

    def tearDown(self):
        """測試後清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_init(self):
        """測試初始化"""
        self.assertIsNotNone(self.view)
        self.assertEqual(self.view.parent_frame, self.parent_frame)
        self.assertEqual(self.view.on_lyric_click, self.on_lyric_click)
        self.assertIsNone(self.view.lyrics_text)
        self.assertEqual(self.view.current_lyrics, [])
        self.assertEqual(self.view.current_index, -1)

    def test_create_view(self):
        """測試建立歌詞視圖"""
        self.view.create_view()

        self.assertIsNotNone(self.view.lyrics_text)
        self.assertIsInstance(self.view.lyrics_text, ctk.CTkTextbox)

    def test_set_lyrics(self):
        """測試設定歌詞"""
        self.view.create_view()

        lyrics = [
            {'time': 10.0, 'text': '第一句歌詞'},
            {'time': 20.0, 'text': '第二句歌詞'},
            {'time': 30.0, 'text': '第三句歌詞'}
        ]

        self.view.set_lyrics(lyrics)

        self.assertEqual(self.view.current_lyrics, lyrics)
        # 檢查文字框內容
        content = self.view.lyrics_text.get("1.0", "end-1c")
        self.assertIn('第一句歌詞', content)
        self.assertIn('第二句歌詞', content)
        self.assertIn('第三句歌詞', content)

    def test_set_empty_lyrics(self):
        """測試設定空歌詞"""
        self.view.create_view()

        self.view.set_lyrics([])

        self.assertEqual(self.view.current_lyrics, [])
        content = self.view.lyrics_text.get("1.0", "end-1c")
        self.assertIn('暫無歌詞', content)

    def test_update_current_time(self):
        """測試更新當前時間"""
        self.view.create_view()

        lyrics = [
            {'time': 10.0, 'text': '第一句歌詞'},
            {'time': 20.0, 'text': '第二句歌詞'},
            {'time': 30.0, 'text': '第三句歌詞'}
        ]

        self.view.set_lyrics(lyrics)

        # 更新到第二句 (25 秒)
        self.view.update_current_time(25.0)

        self.assertEqual(self.view.current_index, 1)

    def test_update_current_time_no_lyrics(self):
        """測試在沒有歌詞時更新時間"""
        self.view.create_view()

        # 不應該拋出異常
        self.view.update_current_time(10.0)

        self.assertEqual(self.view.current_index, -1)

    def test_clear_lyrics(self):
        """測試清除歌詞"""
        self.view.create_view()

        lyrics = [
            {'time': 10.0, 'text': '第一句歌詞'}
        ]

        self.view.set_lyrics(lyrics)
        self.view.clear()

        self.assertEqual(self.view.current_lyrics, [])
        self.assertEqual(self.view.current_index, -1)
        content = self.view.lyrics_text.get("1.0", "end-1c")
        self.assertEqual(content.strip(), '')

    @unittest.skip("CTkTextbox 不支援 tag，高亮功能暫時禁用")
    def test_highlight_current_lyric(self):
        """測試高亮當前歌詞"""
        self.view.create_view()

        lyrics = [
            {'time': 10.0, 'text': '第一句歌詞'},
            {'time': 20.0, 'text': '第二句歌詞'},
            {'time': 30.0, 'text': '第三句歌詞'}
        ]

        self.view.set_lyrics(lyrics)
        self.view.update_current_time(25.0)

        # 檢查是否添加了高亮標籤
        tags = self.view.lyrics_text.tag_names()
        self.assertIn('highlight', tags)

    def test_show_no_lyrics_message(self):
        """測試顯示無歌詞訊息"""
        self.view.create_view()

        self.view.show_no_lyrics_message()

        content = self.view.lyrics_text.get("1.0", "end-1c")
        self.assertIn('暫無歌詞', content)

    def test_toggle_visibility(self):
        """測試切換顯示/隱藏"""
        self.view.create_view()

        # 初始應該是可見的
        self.assertTrue(self.view.is_visible())

        # 切換到隱藏
        self.view.toggle_visibility()
        self.assertFalse(self.view.is_visible())

        # 再切換回可見
        self.view.toggle_visibility()
        self.assertTrue(self.view.is_visible())

    def test_set_visible(self):
        """測試設定可見性"""
        self.view.create_view()

        self.view.set_visible(False)
        self.assertFalse(self.view.is_visible())

        self.view.set_visible(True)
        self.assertTrue(self.view.is_visible())

    def test_auto_scroll_enabled(self):
        """測試自動滾動啟用/停用"""
        self.view.create_view()

        # 初始應該啟用自動滾動
        self.assertTrue(self.view.is_auto_scroll_enabled())

        # 停用自動滾動
        self.view.set_auto_scroll(False)
        self.assertFalse(self.view.is_auto_scroll_enabled())

        # 啟用自動滾動
        self.view.set_auto_scroll(True)
        self.assertTrue(self.view.is_auto_scroll_enabled())

    def test_lyric_click_callback(self):
        """測試點擊歌詞的回調"""
        self.view.create_view()

        lyrics = [
            {'time': 10.0, 'text': '第一句歌詞'},
            {'time': 20.0, 'text': '第二句歌詞'}
        ]

        self.view.set_lyrics(lyrics)

        # 模擬點擊第一句歌詞
        # 這需要模擬 Text widget 的點擊事件
        # 由於 tkinter 事件較複雜,這裡簡化測試
        # 直接調用內部方法
        self.view._on_lyric_line_click(0)

        # 應該觸發回調,傳遞時間 10.0
        self.on_lyric_click.assert_called_once_with(10.0)

    def test_get_lyric_lines_count(self):
        """測試獲取歌詞行數"""
        self.view.create_view()

        lyrics = [
            {'time': 10.0, 'text': '第一句歌詞'},
            {'time': 20.0, 'text': '第二句歌詞'},
            {'time': 30.0, 'text': '第三句歌詞'}
        ]

        self.view.set_lyrics(lyrics)

        self.assertEqual(self.view.get_lyric_lines_count(), 3)

    def test_scroll_to_line(self):
        """測試滾動到指定行"""
        self.view.create_view()

        lyrics = [
            {'time': i * 10.0, 'text': f'第 {i+1} 句歌詞'}
            for i in range(20)  # 創建 20 句歌詞
        ]

        self.view.set_lyrics(lyrics)

        # 滾動到第 10 行
        self.view.scroll_to_line(10)

        # 由於 tkinter 的滾動較難測試,這裡只確保不拋出異常
        # 實際滾動效果需要手動測試

    def test_update_current_time_auto_scroll(self):
        """測試自動滾動功能"""
        self.view.create_view()

        lyrics = [
            {'time': i * 10.0, 'text': f'第 {i+1} 句歌詞'}
            for i in range(20)
        ]

        self.view.set_lyrics(lyrics)
        self.view.set_auto_scroll(True)

        # 更新到第 10 句
        self.view.update_current_time(95.0)

        # 應該自動滾動到第 10 句附近
        self.assertEqual(self.view.current_index, 9)


if __name__ == '__main__':
    unittest.main()
