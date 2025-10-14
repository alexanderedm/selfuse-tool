"""MusicSongActions 測試模組"""
import unittest
from unittest.mock import Mock, MagicMock, patch, call
import tkinter as tk
from music_song_actions import MusicSongActions


class TestMusicSongActions(unittest.TestCase):
    """MusicSongActions 測試類別"""

    def setUp(self):
        """設定測試環境"""
        # 建立 tkinter 根視窗(測試環境需要)
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏視窗

        # Mock music_manager
        self.mock_music_manager = Mock()
        self.mock_music_manager.music_root_path = "E:\\Music"
        self.mock_music_manager.get_songs_by_category = Mock(return_value=[
            {'id': '1', 'title': 'Song 1', 'category': 'Pop'},
            {'id': '2', 'title': 'Song 2', 'category': 'Pop'},
            {'id': '3', 'title': 'Song 3', 'category': 'Pop'}
        ])
        self.mock_music_manager.get_all_categories = Mock(return_value=['Pop', 'Rock', 'Jazz'])

        # Mock file_manager
        self.mock_file_manager = Mock()
        self.mock_file_manager.delete_song = Mock(return_value=True)
        self.mock_file_manager.move_song = Mock(return_value=True)

        # Mock 回調函數
        self.mock_on_play_song = Mock()
        self.mock_on_reload_library = Mock()

    def tearDown(self):
        """清理測試環境"""
        if self.root:
            self.root.destroy()

    def test_init_creates_instance(self):
        """測試初始化建立實例"""
        actions = MusicSongActions(
            parent_window=self.root,
            music_manager=self.mock_music_manager,
            file_manager=self.mock_file_manager,
            on_play_song=self.mock_on_play_song,
            on_reload_library=self.mock_on_reload_library
        )

        self.assertIsNotNone(actions)
        self.assertEqual(actions.parent_window, self.root)
        self.assertEqual(actions.music_manager, self.mock_music_manager)
        self.assertEqual(actions.file_manager, self.mock_file_manager)

    def test_play_song_from_tree_with_category(self):
        """測試從樹狀結構播放歌曲(有分類)"""
        actions = MusicSongActions(
            parent_window=self.root,
            music_manager=self.mock_music_manager,
            file_manager=self.mock_file_manager,
            on_play_song=self.mock_on_play_song
        )

        song = {'id': '2', 'title': 'Song 2', 'category': 'Pop'}
        actions.play_song_from_tree(song)

        # 驗證呼叫 music_manager.get_songs_by_category
        self.mock_music_manager.get_songs_by_category.assert_called_once_with('Pop')

        # 驗證觸發播放回調
        self.mock_on_play_song.assert_called_once()
        args = self.mock_on_play_song.call_args[0]
        self.assertEqual(args[0], song)  # song
        self.assertEqual(len(args[1]), 3)  # playlist
        self.assertEqual(args[2], 1)  # index (Song 2 在索引 1)

    def test_play_song_from_tree_without_category(self):
        """測試從樹狀結構播放歌曲(無分類)"""
        actions = MusicSongActions(
            parent_window=self.root,
            music_manager=self.mock_music_manager,
            file_manager=self.mock_file_manager,
            on_play_song=self.mock_on_play_song
        )

        song = {'id': '1', 'title': 'Song 1'}  # 沒有 category
        actions.play_song_from_tree(song)

        # 驗證不會呼叫 get_songs_by_category
        self.mock_music_manager.get_songs_by_category.assert_not_called()

        # 驗證觸發播放回調(空播放列表)
        self.mock_on_play_song.assert_called_once()
        args = self.mock_on_play_song.call_args[0]
        self.assertEqual(args[0], song)  # song
        self.assertEqual(args[1], [])  # playlist 為空
        self.assertEqual(args[2], 0)  # index

    def test_play_song_from_tree_without_callback(self):
        """測試沒有回調函數時也能正常運作"""
        actions = MusicSongActions(
            parent_window=self.root,
            music_manager=self.mock_music_manager,
            file_manager=self.mock_file_manager
        )

        song = {'id': '1', 'title': 'Song 1', 'category': 'Pop'}
        # 應該不會拋出異常
        actions.play_song_from_tree(song)

    @patch('music_song_actions.messagebox')
    def test_delete_song_success(self, mock_messagebox):
        """測試刪除歌曲成功"""
        # Mock 確認對話框回傳 True
        mock_messagebox.askyesno.return_value = True

        actions = MusicSongActions(
            parent_window=self.root,
            music_manager=self.mock_music_manager,
            file_manager=self.mock_file_manager,
            on_reload_library=self.mock_on_reload_library
        )

        song = {'id': '1', 'title': 'Song 1', 'audio_path': 'E:\\Music\\Pop\\song1.mp3'}
        result = actions.delete_song(song)

        # 驗證結果
        self.assertTrue(result)

        # 驗證呼叫確認對話框
        mock_messagebox.askyesno.assert_called_once()

        # 驗證呼叫 file_manager.delete_song
        self.mock_file_manager.delete_song.assert_called_once_with(song)

        # 驗證觸發重新載入回調
        self.mock_on_reload_library.assert_called_once()

        # 驗證顯示成功訊息
        mock_messagebox.showinfo.assert_called_once()

    @patch('music_song_actions.messagebox')
    def test_delete_song_cancelled(self, mock_messagebox):
        """測試取消刪除歌曲"""
        # Mock 確認對話框回傳 False
        mock_messagebox.askyesno.return_value = False

        actions = MusicSongActions(
            parent_window=self.root,
            music_manager=self.mock_music_manager,
            file_manager=self.mock_file_manager,
            on_reload_library=self.mock_on_reload_library
        )

        song = {'id': '1', 'title': 'Song 1', 'audio_path': 'E:\\Music\\Pop\\song1.mp3'}
        result = actions.delete_song(song)

        # 驗證結果
        self.assertFalse(result)

        # 驗證不會呼叫 delete_song
        self.mock_file_manager.delete_song.assert_not_called()

        # 驗證不會觸發重新載入回調
        self.mock_on_reload_library.assert_not_called()

    @patch('music_song_actions.messagebox')
    def test_delete_song_failed(self, mock_messagebox):
        """測試刪除歌曲失敗"""
        # Mock 確認對話框回傳 True,但刪除失敗
        mock_messagebox.askyesno.return_value = True
        self.mock_file_manager.delete_song = Mock(return_value=False)

        actions = MusicSongActions(
            parent_window=self.root,
            music_manager=self.mock_music_manager,
            file_manager=self.mock_file_manager,
            on_reload_library=self.mock_on_reload_library
        )

        song = {'id': '1', 'title': 'Song 1', 'audio_path': 'E:\\Music\\Pop\\song1.mp3'}
        result = actions.delete_song(song)

        # 驗證結果
        self.assertFalse(result)

        # 驗證呼叫 delete_song
        self.mock_file_manager.delete_song.assert_called_once_with(song)

        # 驗證不會觸發重新載入回調
        self.mock_on_reload_library.assert_not_called()

        # 驗證顯示錯誤訊息
        mock_messagebox.showerror.assert_called_once()

    @patch('music_song_actions.messagebox')
    def test_move_song_to_category_no_categories(self, mock_messagebox):
        """測試移動歌曲 - 沒有可用分類"""
        self.mock_music_manager.get_all_categories = Mock(return_value=[])

        actions = MusicSongActions(
            parent_window=self.root,
            music_manager=self.mock_music_manager,
            file_manager=self.mock_file_manager
        )

        song = {'id': '1', 'title': 'Song 1', 'category': 'Pop'}
        actions.move_song_to_category(song)

        # 驗證顯示警告訊息
        mock_messagebox.showwarning.assert_called_once()

    @patch('music_song_actions.messagebox')
    def test_move_song_to_category_no_other_categories(self, mock_messagebox):
        """測試移動歌曲 - 沒有其他分類可移動"""
        self.mock_music_manager.get_all_categories = Mock(return_value=['Pop'])

        actions = MusicSongActions(
            parent_window=self.root,
            music_manager=self.mock_music_manager,
            file_manager=self.mock_file_manager
        )

        song = {'id': '1', 'title': 'Song 1', 'category': 'Pop'}
        actions.move_song_to_category(song)

        # 驗證顯示提示訊息
        mock_messagebox.showinfo.assert_called_once()

    @patch('music_song_actions.messagebox')
    @patch('music_song_actions.tk.Toplevel')
    def test_move_song_to_category_shows_dialog(self, mock_toplevel, mock_messagebox):
        """測試移動歌曲 - 顯示對話框"""
        actions = MusicSongActions(
            parent_window=self.root,
            music_manager=self.mock_music_manager,
            file_manager=self.mock_file_manager
        )

        song = {'id': '1', 'title': 'Song 1', 'category': 'Pop'}
        actions.move_song_to_category(song)

        # 驗證建立 Toplevel 視窗
        mock_toplevel.assert_called_once_with(self.root)

    def test_ui_theme_colors(self):
        """測試 UI 顏色主題正確設定"""
        actions = MusicSongActions(
            parent_window=self.root,
            music_manager=self.mock_music_manager,
            file_manager=self.mock_file_manager
        )

        # 驗證顏色主題已設定
        self.assertEqual(actions.bg_color, "#1e1e1e")
        self.assertEqual(actions.card_bg, "#2d2d2d")
        self.assertEqual(actions.accent_color, "#0078d4")
        self.assertEqual(actions.text_color, "#e0e0e0")
        self.assertEqual(actions.text_secondary, "#a0a0a0")


if __name__ == '__main__':
    unittest.main()
