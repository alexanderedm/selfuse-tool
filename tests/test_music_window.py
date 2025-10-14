"""音樂播放器視窗 UI 測試模組"""
import unittest
from unittest.mock import Mock, patch, MagicMock, call
import tkinter as tk
from tkinter import ttk
import sys
import os

# 將父目錄加入路徑以便導入模組
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from music_window import MusicWindow


class TestMusicWindowTreeview(unittest.TestCase):
    """測試 MusicWindow 的 Treeview 功能"""

    def setUp(self):
        """測試前準備"""
        # Mock pygame
        self.pygame_mock = MagicMock()
        self.pygame_mock.mixer = MagicMock()
        self.pygame_mock.mixer.init = MagicMock()
        self.pygame_mock.mixer.music = MagicMock()

        # Mock config_manager
        self.config_manager_mock = Mock()
        self.config_manager_mock.get_music_volume = Mock(return_value=70)
        self.config_manager_mock.set_music_volume = Mock()
        self.config_manager_mock.config = {}

        # Mock music_manager
        self.music_manager_mock = Mock()
        self.music_manager_mock.config_manager = self.config_manager_mock
        self.music_manager_mock.music_root_path = "/test/music"
        self.music_manager_mock.format_duration = Mock(side_effect=lambda s: f"{s//60:02d}:{s%60:02d}")

        # 建立測試用的歌曲資料
        self.test_songs = [
            {
                'id': 'song1',
                'title': 'Test Song 1',
                'duration': 180,  # 3 分鐘
                'category': 'Rock',
                'uploader': 'Artist 1',
                'audio_path': '/test/song1.mp3',
                'json_path': '/test/song1.json'
            },
            {
                'id': 'song2',
                'title': 'Test Song 2',
                'duration': 240,  # 4 分鐘
                'category': 'Pop',
                'uploader': 'Artist 2',
                'audio_path': '/test/song2.mp3',
                'json_path': '/test/song2.json'
            },
            {
                'id': 'song3',
                'title': 'Very Long Song Title That Should Be Displayed Properly',
                'duration': 65,  # 1 分 5 秒
                'category': 'Jazz',
                'uploader': 'Artist 3',
                'audio_path': '/test/song3.mp3',
                'json_path': '/test/song3.json'
            }
        ]

    @patch('music_window.pygame', new_callable=lambda: MagicMock())
    @patch('music_window.YouTubeDownloader')
    def test_display_songs_clears_tree(self, mock_downloader, mock_pygame):
        """測試 _display_songs 清空現有項目"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            # 建立 MusicWindow 實例
            window = MusicWindow(self.music_manager_mock, root)

            # 手動建立 song_tree 用於測試
            window.song_tree = ttk.Treeview(root, columns=('title', 'duration'))

            # 先插入一些項目
            window.song_tree.insert('', 'end', values=('Old Song', '03:00'))
            window.song_tree.insert('', 'end', values=('Another Old Song', '04:00'))

            # 確認有 2 個項目
            self.assertEqual(len(window.song_tree.get_children()), 2)

            # 呼叫 _display_songs
            window._display_songs(self.test_songs)

            # 確認舊項目被清除,新項目被插入
            children = window.song_tree.get_children()
            self.assertEqual(len(children), 3)

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('music_window.pygame', new_callable=lambda: MagicMock())
    @patch('music_window.YouTubeDownloader')
    def test_display_songs_inserts_correct_data(self, mock_downloader, mock_pygame):
        """測試 _display_songs 插入正確的歌曲資料"""
        try:

            root = tk.Tk()

        except tk.TclError:

            self.skipTest("Tkinter environment not properly configured")

            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.song_tree = ttk.Treeview(root, columns=('title', 'duration'))

            # 呼叫 _display_songs
            window._display_songs(self.test_songs)

            # 檢查插入的項目
            children = window.song_tree.get_children()
            self.assertEqual(len(children), 3)

            # 檢查第一首歌
            item1_values = window.song_tree.item(children[0], 'values')
            self.assertEqual(item1_values[0], 'Test Song 1')
            self.assertEqual(item1_values[1], '03:00')

            # 檢查第二首歌
            item2_values = window.song_tree.item(children[1], 'values')
            self.assertEqual(item2_values[0], 'Test Song 2')
            self.assertEqual(item2_values[1], '04:00')

            # 檢查第三首歌(長標題)
            item3_values = window.song_tree.item(children[2], 'values')
            self.assertEqual(item3_values[0], 'Very Long Song Title That Should Be Displayed Properly')
            self.assertEqual(item3_values[1], '01:05')

        finally:


            try:


                root.destroy()


            except:


                pass

    @patch('music_window.pygame', new_callable=lambda: MagicMock())
    @patch('music_window.YouTubeDownloader')
    def test_display_songs_updates_playlist(self, mock_downloader, mock_pygame):
        """測試 _display_songs 更新播放列表"""
        try:

            root = tk.Tk()

        except tk.TclError:

            self.skipTest("Tkinter environment not properly configured")

            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.song_tree = ttk.Treeview(root, columns=('title', 'duration'))

            # 初始播放列表應該是空的
            self.assertEqual(window.playlist, [])

            # 呼叫 _display_songs
            window._display_songs(self.test_songs)

            # 確認播放列表已更新
            self.assertEqual(window.playlist, self.test_songs)
            self.assertEqual(len(window.playlist), 3)

        finally:


            try:


                root.destroy()


            except:


                pass

    @patch('music_window.pygame', new_callable=lambda: MagicMock())
    @patch('music_window.YouTubeDownloader')
    def test_display_songs_empty_list(self, mock_downloader, mock_pygame):
        """測試 _display_songs 處理空列表"""
        try:

            root = tk.Tk()

        except tk.TclError:

            self.skipTest("Tkinter environment not properly configured")

            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.song_tree = ttk.Treeview(root, columns=('title', 'duration'))

            # 先插入一些項目
            window.song_tree.insert('', 'end', values=('Song', '03:00'))

            # 呼叫 _display_songs 傳入空列表
            window._display_songs([])

            # 確認樹狀結構被清空
            self.assertEqual(len(window.song_tree.get_children()), 0)
            self.assertEqual(window.playlist, [])

        finally:


            try:


                root.destroy()


            except:


                pass

    @patch('music_window.pygame', new_callable=lambda: MagicMock())
    @patch('music_window.YouTubeDownloader')
    def test_format_duration_called_correctly(self, mock_downloader, mock_pygame):
        """測試時長格式化函數被正確呼叫"""
        try:

            root = tk.Tk()

        except tk.TclError:

            self.skipTest("Tkinter environment not properly configured")

            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.song_tree = ttk.Treeview(root, columns=('title', 'duration'))

            # 重置 mock
            self.music_manager_mock.format_duration.reset_mock()

            # 呼叫 _display_songs
            window._display_songs(self.test_songs)

            # 確認 format_duration 被呼叫了 3 次(每首歌一次)
            self.assertEqual(self.music_manager_mock.format_duration.call_count, 3)

            # 確認傳入的參數正確
            expected_calls = [
                call(180),  # Test Song 1
                call(240),  # Test Song 2
                call(65),   # Test Song 3
            ]
            self.music_manager_mock.format_duration.assert_has_calls(expected_calls)

        finally:


            try:


                root.destroy()


            except:


                pass


if __name__ == '__main__':
    unittest.main()
