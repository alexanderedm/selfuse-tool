"""MusicPlaybackView 模組的單元測試"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from music_playback_view import MusicPlaybackView


class TestMusicPlaybackView(unittest.TestCase):
    """測試 MusicPlaybackView 類別"""

    def setUp(self):
        """測試前的設定"""
        # 建立 Tk 根視窗
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("tkinter 環境設定問題")

        # 建立模擬的回調函數
        self.on_play_pause_mock = Mock()
        self.on_previous_mock = Mock()
        self.on_next_mock = Mock()
        self.on_volume_change_mock = Mock()
        self.on_mode_change_mock = Mock()

        # 建立模擬的音樂管理器
        self.music_manager_mock = Mock()
        self.music_manager_mock.config_manager = Mock()
        self.music_manager_mock.config_manager.get_music_volume = Mock(return_value=50)

        # 建立父框架
        self.parent_frame = tk.Frame(self.root)

        # 建立 MusicPlaybackView 實例
        self.view = MusicPlaybackView(
            parent_frame=self.parent_frame,
            music_manager=self.music_manager_mock,
            on_play_pause=self.on_play_pause_mock,
            on_play_previous=self.on_previous_mock,
            on_play_next=self.on_next_mock,
            on_volume_change=self.on_volume_change_mock,
            on_cycle_play_mode=self.on_mode_change_mock
        )

        # 建立視圖
        self.view.create_view()

        # 更新所有待處理的事件
        self.root.update()

    def tearDown(self):
        """測試後的清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_initialization(self):
        """測試初始化"""
        self.assertIsNotNone(self.view.album_cover_label)
        self.assertIsNotNone(self.view.current_song_label)
        self.assertIsNotNone(self.view.artist_label)
        self.assertIsNotNone(self.view.time_label)
        self.assertIsNotNone(self.view.progress_bar)
        self.assertIsNotNone(self.view.play_pause_button)
        self.assertIsNotNone(self.view.play_mode_button)
        self.assertIsNotNone(self.view.volume_scale)

    def test_initial_state(self):
        """測試初始狀態"""
        self.assertEqual(self.view.current_song_label.cget('text'), '未播放')
        self.assertEqual(self.view.artist_label.cget('text'), '')
        self.assertEqual(self.view.time_label.cget('text'), '00:00 / 00:00')
        self.assertEqual(self.view.play_pause_button.cget('text'), '▶')
        self.assertEqual(self.view.get_volume(), 50)

    def test_play_pause_button_click(self):
        """測試播放/暫停按鈕點擊"""
        self.view.play_pause_button.invoke()
        self.on_play_pause_mock.assert_called_once()

    def test_volume_change(self):
        """測試音量改變"""
        # 模擬用戶拖動音量滑桿
        # 需要觸發 Scale 的 command 回調
        self.view.volume_scale.set(75)
        # 手動觸發 command 回調
        self.view.on_volume_change("75")
        # 音量改變回調應該被呼叫
        self.on_volume_change_mock.assert_called_with("75")

    def test_mode_button_click(self):
        """測試播放模式按鈕點擊"""
        self.view.play_mode_button.invoke()
        self.on_mode_change_mock.assert_called_once()

    def test_update_current_song(self):
        """測試更新歌曲資訊"""
        song = {
            'title': '測試歌曲',
            'uploader': '測試藝術家',
            'thumbnail': ''
        }
        self.view.update_current_song(song)
        self.assertEqual(self.view.current_song_label.cget('text'), '測試歌曲')
        self.assertEqual(self.view.artist_label.cget('text'), '🎤 測試藝術家')

    def test_update_current_song_no_uploader(self):
        """測試更新歌曲資訊（無上傳者）"""
        song = {
            'title': '測試歌曲',
            'thumbnail': ''
        }
        self.view.update_current_song(song)
        self.assertEqual(self.view.current_song_label.cget('text'), '測試歌曲')
        # 當沒有 uploader 時，artist_label 不會被更新
        # 所以應該保持原始狀態（空字串）
        self.assertEqual(self.view.artist_label.cget('text'), '')

    def test_update_play_pause_button(self):
        """測試更新播放/暫停按鈕"""
        # 設為暫停狀態（顯示播放圖示）
        self.view.update_play_pause_button(is_paused=True)
        self.assertEqual(self.view.play_pause_button.cget('text'), '▶')

        # 設為播放狀態（顯示暫停圖示）
        self.view.update_play_pause_button(is_paused=False)
        self.assertEqual(self.view.play_pause_button.cget('text'), '⏸')

    def test_update_progress(self):
        """測試更新進度"""
        self.view.update_progress(30.5)

        # 檢查進度條
        progress = self.view.progress_bar['value']
        self.assertAlmostEqual(progress, 30.5, places=1)

    def test_update_time_label(self):
        """測試更新時間標籤"""
        self.view.update_time_label("01:30 / 03:45")
        self.assertEqual(self.view.time_label.cget('text'), "01:30 / 03:45")

    def test_update_play_mode(self):
        """測試更新播放模式"""
        # 順序播放
        self.view.update_play_mode('sequential')
        self.assertEqual(self.view.play_mode_button.cget('text'), '➡️ 順序播放')

        # 列表循環
        self.view.update_play_mode('repeat_all')
        self.assertEqual(self.view.play_mode_button.cget('text'), '🔂 列表循環')

        # 單曲循環
        self.view.update_play_mode('repeat_one')
        self.assertEqual(self.view.play_mode_button.cget('text'), '🔁 單曲循環')

        # 隨機播放
        self.view.update_play_mode('shuffle')
        self.assertEqual(self.view.play_mode_button.cget('text'), '🔀 隨機播放')

    def test_get_volume(self):
        """測試獲取音量"""
        self.view.set_volume(80)
        self.assertEqual(self.view.get_volume(), 80)

    def test_set_volume(self):
        """測試設定音量"""
        self.view.set_volume(60)
        self.assertEqual(self.view.get_volume(), 60)

    def test_reset_display(self):
        """測試重置顯示"""
        # 先設定一些值
        self.view.update_current_song({'title': '測試', 'uploader': '測試', 'thumbnail': ''})
        self.view.update_progress(50)
        self.view.update_play_pause_button(is_paused=False)

        # 重置
        self.view.reset_display()

        # 檢查是否重置到初始狀態
        self.assertEqual(self.view.current_song_label.cget('text'), '未播放')
        self.assertEqual(self.view.artist_label.cget('text'), '')
        self.assertEqual(self.view.progress_bar['value'], 0)
        self.assertEqual(self.view.time_label.cget('text'), '00:00 / 00:00')
        self.assertEqual(self.view.play_pause_button.cget('text'), '▶')

    @patch('music_playback_view.Image')
    def test_get_default_cover_image(self, mock_image):
        """測試獲取預設封面"""
        # 測試預設封面生成
        default_cover = self.view._get_default_cover_image()
        # 第一次呼叫應該建立圖片
        if default_cover:
            # 第二次呼叫應該從快取返回
            default_cover_2 = self.view._get_default_cover_image()
            self.assertEqual(default_cover, default_cover_2)


if __name__ == '__main__':
    unittest.main()
