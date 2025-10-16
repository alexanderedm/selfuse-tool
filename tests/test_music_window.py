"""音樂播放器視窗 UI 測試模組"""
import unittest
from unittest.mock import Mock, patch, MagicMock, call
import tkinter as tk
from tkinter import ttk
import sys
import os

# 將父目錄加入路徑以便導入模組
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.music.windows.music_window import MusicWindow


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

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
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

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
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

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
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

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
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

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
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


class TestMusicWindowEqualizerSync(unittest.TestCase):
    """測試等化器同步功能"""

    def setUp(self):
        """測試前準備"""
        self.pygame_mock = MagicMock()
        self.pygame_mock.mixer = MagicMock()
        self.pygame_mock.mixer.init = MagicMock()

        self.config_manager_mock = Mock()
        self.config_manager_mock.get_music_volume = Mock(return_value=70)
        self.config_manager_mock.config = {}

        self.music_manager_mock = Mock()
        self.music_manager_mock.config_manager = self.config_manager_mock
        self.music_manager_mock.music_root_path = "/test/music"

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_sync_equalizer_to_processor_with_gains(self, mock_downloader, mock_pygame):
        """測試等化器同步 - 有增益值"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)

            # 模擬 audio_processor 存在
            window.use_audio_player = True
            window.audio_processor = Mock()
            window.audio_processor.equalizer = Mock()
            window.audio_processor.equalizer.frequencies = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000]

            # 模擬等化器返回增益值
            window.equalizer = Mock()
            window.equalizer.get_gains = Mock(return_value=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])

            # 執行同步
            window._sync_equalizer_to_processor()

            # 驗證 set_all_gains 被呼叫
            window.audio_processor.equalizer.set_all_gains.assert_called_once_with([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_sync_equalizer_without_audio_player(self, mock_downloader, mock_pygame):
        """測試等化器同步 - 沒有 AudioPlayer"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.use_audio_player = False

            # 執行同步（應該什麼都不做）
            window._sync_equalizer_to_processor()

            # 不應該拋出錯誤
            self.assertFalse(window.use_audio_player)

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_sync_equalizer_with_invalid_gains(self, mock_downloader, mock_pygame):
        """測試等化器同步 - 無效增益值"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.use_audio_player = True
            window.audio_processor = Mock()
            window.audio_processor.equalizer = Mock()
            window.audio_processor.equalizer.frequencies = [60, 170, 310]

            window.equalizer = Mock()
            window.equalizer.get_gains = Mock(return_value=None)

            # 執行同步（應該不呼叫 set_all_gains）
            window._sync_equalizer_to_processor()

            window.audio_processor.equalizer.set_all_gains.assert_not_called()

        finally:
            try:
                root.destroy()
            except:
                pass


class TestMusicWindowPlayMode(unittest.TestCase):
    """測試播放模式功能"""

    def setUp(self):
        """測試前準備"""
        self.pygame_mock = MagicMock()
        self.pygame_mock.mixer = MagicMock()
        self.pygame_mock.mixer.init = MagicMock()

        self.config_manager_mock = Mock()
        self.config_manager_mock.get_music_volume = Mock(return_value=70)
        self.config_manager_mock.config = {}

        self.music_manager_mock = Mock()
        self.music_manager_mock.config_manager = self.config_manager_mock
        self.music_manager_mock.music_root_path = "/test/music"
        self.music_manager_mock.format_duration = Mock(side_effect=lambda s: f"{s//60:02d}:{s%60:02d}")

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_cycle_play_mode_all_modes(self, mock_downloader, mock_pygame):
        """測試循環切換所有播放模式"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)

            # 初始模式應該是 sequential
            self.assertEqual(window.play_mode, 'sequential')

            # 切換到 repeat_all
            window._cycle_play_mode()
            self.assertEqual(window.play_mode, 'repeat_all')

            # 切換到 repeat_one
            window._cycle_play_mode()
            self.assertEqual(window.play_mode, 'repeat_one')

            # 切換到 shuffle
            window._cycle_play_mode()
            self.assertEqual(window.play_mode, 'shuffle')

            # 循環回到 sequential
            window._cycle_play_mode()
            self.assertEqual(window.play_mode, 'sequential')

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_shuffle_mode_clears_played_indices(self, mock_downloader, mock_pygame):
        """測試切換到隨機模式會清空已播放索引"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)

            # 設定一些已播放索引
            window.played_indices = [0, 1, 2]

            # 切換到 shuffle 模式
            window.play_mode = 'sequential'
            window._cycle_play_mode()  # -> repeat_all
            window._cycle_play_mode()  # -> repeat_one
            window._cycle_play_mode()  # -> shuffle

            # 驗證已播放索引被清空
            self.assertEqual(window.played_indices, [])

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_repeat_one_mode_replays_same_song(self, mock_downloader, mock_pygame):
        """測試單曲循環模式重播同一首歌"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.playlist = [
                {'id': 'song1', 'title': 'Song 1', 'audio_path': '/test/song1.mp3'},
                {'id': 'song2', 'title': 'Song 2', 'audio_path': '/test/song2.mp3'}
            ]
            window.current_index = 0
            window.play_mode = 'repeat_one'

            # 測試 _play_next_in_repeat_one_mode
            initial_index = window.current_index
            window._play_next_in_repeat_one_mode()

            # 索引應該保持不變
            self.assertEqual(window.current_index, initial_index)

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_sequential_mode_plays_in_order(self, mock_downloader, mock_pygame):
        """測試順序播放模式按順序播放"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.playlist = [
                {'id': 'song1', 'title': 'Song 1', 'audio_path': '/test/song1.mp3'},
                {'id': 'song2', 'title': 'Song 2', 'audio_path': '/test/song2.mp3'},
                {'id': 'song3', 'title': 'Song 3', 'audio_path': '/test/song3.mp3'}
            ]
            window.current_index = 0
            window.play_mode = 'sequential'

            # 測試 _play_next_in_sequential_mode
            window._play_next_in_sequential_mode()
            self.assertEqual(window.current_index, 1)

            window._play_next_in_sequential_mode()
            self.assertEqual(window.current_index, 2)

            # 應該循環回到開頭
            window._play_next_in_sequential_mode()
            self.assertEqual(window.current_index, 0)

        finally:
            try:
                root.destroy()
            except:
                pass


class TestMusicWindowVolumeControl(unittest.TestCase):
    """測試音量控制功能"""

    def setUp(self):
        """測試前準備"""
        self.pygame_mock = MagicMock()
        self.pygame_mock.mixer = MagicMock()
        self.pygame_mock.mixer.init = MagicMock()
        self.pygame_mock.mixer.music = MagicMock()

        self.config_manager_mock = Mock()
        self.config_manager_mock.get_music_volume = Mock(return_value=70)
        self.config_manager_mock.set_music_volume = Mock()
        self.config_manager_mock.config = {}

        self.music_manager_mock = Mock()
        self.music_manager_mock.config_manager = self.config_manager_mock
        self.music_manager_mock.music_root_path = "/test/music"

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_volume_change_with_audio_player(self, mock_downloader, mock_pygame):
        """測試使用 AudioPlayer 時音量變更"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.use_audio_player = True
            window.audio_player = Mock()

            # 觸發音量變更
            window._on_volume_change("80")

            # 驗證 audio_player.set_volume 被呼叫
            window.audio_player.set_volume.assert_called_once_with(0.8)

            # 驗證設定被保存
            self.config_manager_mock.set_music_volume.assert_called_once_with(80)

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame')
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_volume_change_with_pygame(self, mock_downloader, mock_pygame):
        """測試使用 pygame 時音量變更"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.use_audio_player = False

            # 觸發音量變更
            window._on_volume_change("50")

            # 驗證 pygame.mixer.music.set_volume 被呼叫
            mock_pygame.mixer.music.set_volume.assert_called_with(0.5)

            # 驗證設定被保存
            self.config_manager_mock.set_music_volume.assert_called_once_with(50)

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_volume_change_saves_to_config(self, mock_downloader, mock_pygame):
        """測試音量變更會保存到設定檔"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)

            # 觸發音量變更
            window._on_volume_change("100")

            # 驗證設定被保存
            self.config_manager_mock.set_music_volume.assert_called_with(100)

        finally:
            try:
                root.destroy()
            except:
                pass


class TestMusicWindowProgressUpdate(unittest.TestCase):
    """測試進度更新功能"""

    def setUp(self):
        """測試前準備"""
        self.pygame_mock = MagicMock()
        self.pygame_mock.mixer = MagicMock()
        self.pygame_mock.mixer.init = MagicMock()

        self.config_manager_mock = Mock()
        self.config_manager_mock.get_music_volume = Mock(return_value=70)
        self.config_manager_mock.config = {}

        self.music_manager_mock = Mock()
        self.music_manager_mock.config_manager = self.config_manager_mock
        self.music_manager_mock.music_root_path = "/test/music"
        self.music_manager_mock.format_duration = Mock(side_effect=lambda s: f"{s//60:02d}:{s%60:02d}")

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_calculate_playback_position_with_audio_player(self, mock_downloader, mock_pygame):
        """測試使用 AudioPlayer 計算播放位置"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.use_audio_player = True
            window.audio_player = Mock()
            window.audio_player.get_position = Mock(return_value=30.5)
            window.audio_player.get_duration = Mock(return_value=180.0)

            # 計算播放位置
            current_pos, total_duration = window._calculate_playback_position()

            self.assertEqual(current_pos, 30.5)
            self.assertEqual(total_duration, 180.0)

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    @patch('src.music.windows.music_window.time')
    def test_calculate_playback_position_with_pygame(self, mock_time, mock_downloader, mock_pygame):
        """測試使用 pygame 計算播放位置"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.use_audio_player = False
            window.current_song = {'duration': 240}
            window.start_time = 1000.0

            mock_time.time = Mock(return_value=1060.0)

            # 計算播放位置
            current_pos, total_duration = window._calculate_playback_position()

            self.assertEqual(current_pos, 60.0)  # 1060 - 1000
            self.assertEqual(total_duration, 240)

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_format_time_text(self, mock_downloader, mock_pygame):
        """測試時間文字格式化"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)

            # 測試格式化
            time_text = window._format_time_text(65.5, 180)

            # 驗證格式
            self.assertIn("/", time_text)
            self.music_manager_mock.format_duration.assert_any_call(65)  # int(65.5)
            self.music_manager_mock.format_duration.assert_any_call(180)

        finally:
            try:
                root.destroy()
            except:
                pass


class TestMusicWindowErrorHandling(unittest.TestCase):
    """測試錯誤處理功能"""

    def setUp(self):
        """測試前準備"""
        self.pygame_mock = MagicMock()
        self.pygame_mock.mixer = MagicMock()
        self.pygame_mock.mixer.init = MagicMock()

        self.config_manager_mock = Mock()
        self.config_manager_mock.get_music_volume = Mock(return_value=70)
        self.config_manager_mock.config = {}

        self.music_manager_mock = Mock()
        self.music_manager_mock.config_manager = self.config_manager_mock
        self.music_manager_mock.music_root_path = "/test/music"

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_is_valid_current_index_with_valid_index(self, mock_downloader, mock_pygame):
        """測試有效索引檢查 - 有效情況"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.playlist = [{'id': '1'}, {'id': '2'}, {'id': '3'}]
            window.current_index = 1

            self.assertTrue(window._is_valid_current_index())

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_is_valid_current_index_with_invalid_index(self, mock_downloader, mock_pygame):
        """測試有效索引檢查 - 無效情況"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.playlist = [{'id': '1'}, {'id': '2'}]
            window.current_index = 5

            self.assertFalse(window._is_valid_current_index())

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_start_first_song_if_available_with_empty_playlist(self, mock_downloader, mock_pygame):
        """測試播放第一首歌 - 空播放列表"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.playlist = []

            result = window._start_first_song_if_available()

            self.assertFalse(result)

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_handle_paused_state_when_paused(self, mock_downloader, mock_pygame):
        """測試暫停狀態處理 - 暫停中"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.is_paused = True

            result = window._handle_paused_state()

            self.assertTrue(result)

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_handle_paused_state_when_not_paused(self, mock_downloader, mock_pygame):
        """測試暫停狀態處理 - 未暫停"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.is_paused = False

            result = window._handle_paused_state()

            self.assertFalse(result)

        finally:
            try:
                root.destroy()
            except:
                pass


class TestMusicWindowPlaylistManagement(unittest.TestCase):
    """測試播放列表管理功能"""

    def setUp(self):
        """測試前準備"""
        self.pygame_mock = MagicMock()
        self.pygame_mock.mixer = MagicMock()
        self.pygame_mock.mixer.init = MagicMock()

        self.config_manager_mock = Mock()
        self.config_manager_mock.get_music_volume = Mock(return_value=70)
        self.config_manager_mock.config = {}

        self.music_manager_mock = Mock()
        self.music_manager_mock.config_manager = self.config_manager_mock
        self.music_manager_mock.music_root_path = "/test/music"

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_get_available_shuffle_indices_with_available_songs(self, mock_downloader, mock_pygame):
        """測試取得可用隨機索引 - 有可用歌曲"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.playlist = [{'id': '1'}, {'id': '2'}, {'id': '3'}, {'id': '4'}]
            window.played_indices = [0, 2]

            available = window._get_available_shuffle_indices()

            self.assertIn(1, available)
            self.assertIn(3, available)
            self.assertNotIn(0, available)
            self.assertNotIn(2, available)

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_get_available_shuffle_indices_all_played(self, mock_downloader, mock_pygame):
        """測試取得可用隨機索引 - 全部已播放"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.playlist = [{'id': '1'}, {'id': '2'}, {'id': '3'}]
            window.played_indices = [0, 1, 2]

            available = window._get_available_shuffle_indices()

            # 應該重置並返回所有索引
            self.assertEqual(len(available), 3)
            self.assertEqual(window.played_indices, [])

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame')
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_play_previous_wraps_around(self, mock_downloader, mock_pygame):
        """測試播放上一首會循環"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.playlist = [
                {'id': 'song1', 'audio_path': '/test/song1.mp3'},
                {'id': 'song2', 'audio_path': '/test/song2.mp3'},
                {'id': 'song3', 'audio_path': '/test/song3.mp3'}
            ]
            window.current_index = 0

            # 從第一首播放上一首應該到最後一首
            window._play_previous()

            self.assertEqual(window.current_index, 2)

        finally:
            try:
                root.destroy()
            except:
                pass


class TestMusicWindowUIIntegration(unittest.TestCase):
    """測試 UI 整合功能"""

    def setUp(self):
        """測試前準備"""
        self.pygame_mock = MagicMock()
        self.pygame_mock.mixer = MagicMock()
        self.pygame_mock.mixer.init = MagicMock()

        self.config_manager_mock = Mock()
        self.config_manager_mock.get_music_volume = Mock(return_value=70)
        self.config_manager_mock.config = {}

        self.music_manager_mock = Mock()
        self.music_manager_mock.config_manager = self.config_manager_mock
        self.music_manager_mock.music_root_path = "/test/music"

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_theme_initialization(self, mock_downloader, mock_pygame):
        """測試主題初始化"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)

            # 驗證主題物件存在
            self.assertIsNotNone(window.theme)
            self.assertEqual(window.theme.theme_name, 'dark')

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame', new_callable=lambda: MagicMock())
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_should_play_next_with_audio_player(self, mock_downloader, mock_pygame):
        """測試使用 AudioPlayer 時是否應播放下一首"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.use_audio_player = True

            result = window._should_play_next()

            # AudioPlayer 使用回調，不應該在這裡返回 True
            self.assertFalse(result)

        finally:
            try:
                root.destroy()
            except:
                pass

    @patch('src.music.windows.music_window.pygame')
    @patch('src.music.windows.music_window.YouTubeDownloader')
    def test_should_play_next_with_pygame_not_busy(self, mock_downloader, mock_pygame):
        """測試使用 pygame 且播放結束時是否應播放下一首"""
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tkinter environment not properly configured")
            return

        try:
            window = MusicWindow(self.music_manager_mock, root)
            window.use_audio_player = False
            window.is_paused = False
            mock_pygame.mixer.music.get_busy = Mock(return_value=False)

            result = window._should_play_next()

            self.assertTrue(result)

        finally:
            try:
                root.destroy()
            except:
                pass


if __name__ == '__main__':
    unittest.main()
