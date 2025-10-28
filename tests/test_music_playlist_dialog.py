"""MusicPlaylistDialog 測試模組"""
import unittest
from unittest.mock import Mock, MagicMock, patch, call
from src.music.dialogs.music_playlist_dialog import MusicPlaylistDialog


class TestMusicPlaylistDialog(unittest.TestCase):
    """MusicPlaylistDialog 測試類"""

    def setUp(self):
        """測試前準備"""
        # Mock music_manager
        self.mock_music_manager = Mock()
        self.mock_music_manager.get_song_by_id.return_value = {
            'id': 'test_id',
            'title': 'Test Song',
            'uploader': 'Test Artist',
            'duration': 180
        }
        self.mock_music_manager.format_duration.return_value = "3:00"

        # Mock playlist_manager
        self.mock_playlist_manager = Mock()
        self.mock_playlist_manager.get_all_playlists.return_value = [
            {'name': 'Playlist 1', 'song_count': 5, 'description': 'Test playlist 1'},
            {'name': 'Playlist 2', 'song_count': 3, 'description': 'Test playlist 2'}
        ]
        self.mock_playlist_manager.get_playlist.return_value = {
            'name': 'Playlist 1',
            'song_count': 2,
            'description': 'Test description',
            'songs': ['song1', 'song2']
        }

        # Mock parent window
        self.mock_parent = Mock()

    def tearDown(self):
        """測試後清理"""
        pass

    def test_init(self):
        """測試初始化"""
        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.parent_window, self.mock_parent)
        self.assertEqual(dialog.playlist_manager, self.mock_playlist_manager)
        self.assertEqual(dialog.music_manager, self.mock_music_manager)

    @patch('music_playlist_dialog.ttk.Style')
    @patch('music_playlist_dialog.ttk.Treeview')
    @patch('music_playlist_dialog.ctk.CTkScrollbar')
    @patch('music_playlist_dialog.ctk.CTkButton')
    @patch('music_playlist_dialog.ctk.CTkLabel')
    @patch('music_playlist_dialog.ctk.CTkFrame')
    @patch('music_playlist_dialog.ctk.CTkToplevel')
    def test_show_playlists(self, mock_toplevel, mock_frame, mock_label,
                           mock_button, mock_scrollbar, mock_treeview, mock_style):
        """測試顯示播放列表對話框"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        result = dialog.show_playlists()

        self.assertIsNotNone(result)
        mock_toplevel.assert_called_once()
        self.mock_playlist_manager.get_all_playlists.assert_called_once()

    @patch('music_playlist_dialog.MusicPlaylistDialog.show_playlists')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.messagebox.showinfo')
    def test_create_playlist_success(self, mock_showinfo, mock_askstring, mock_show_playlists):
        """測試成功建立播放列表"""
        mock_askstring.side_effect = ['New Playlist', 'Test Description']
        self.mock_playlist_manager.create_playlist.return_value = True

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        mock_parent_dialog = Mock()
        dialog.create_playlist(mock_parent_dialog)

        self.mock_playlist_manager.create_playlist.assert_called_once_with(
            'New Playlist',
            'Test Description'
        )
        mock_showinfo.assert_called_once()
        mock_parent_dialog.destroy.assert_called_once()

    @patch('tkinter.simpledialog.askstring')
    def test_create_playlist_empty_name(self, mock_askstring):
        """測試建立播放列表時輸入空白名稱"""
        mock_askstring.return_value = ''

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        mock_parent_dialog = Mock()
        dialog.create_playlist(mock_parent_dialog)

        self.mock_playlist_manager.create_playlist.assert_not_called()

    @patch('tkinter.simpledialog.askstring')
    def test_create_playlist_cancelled(self, mock_askstring):
        """測試取消建立播放列表"""
        mock_askstring.return_value = None

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        mock_parent_dialog = Mock()
        dialog.create_playlist(mock_parent_dialog)

        self.mock_playlist_manager.create_playlist.assert_not_called()

    @patch('music_playlist_dialog.MusicPlaylistDialog.show_playlists')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.messagebox.showinfo')
    def test_delete_playlist_success(self, mock_showinfo, mock_askyesno, mock_show_playlists):
        """測試成功刪除播放列表"""
        mock_askyesno.return_value = True
        self.mock_playlist_manager.delete_playlist.return_value = True

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        mock_parent_dialog = Mock()
        dialog.delete_playlist('Test Playlist', mock_parent_dialog)

        self.mock_playlist_manager.delete_playlist.assert_called_once_with('Test Playlist')
        mock_showinfo.assert_called_once()
        mock_parent_dialog.destroy.assert_called_once()

    @patch('tkinter.messagebox.askyesno')
    def test_delete_playlist_cancelled(self, mock_askyesno):
        """測試取消刪除播放列表"""
        mock_askyesno.return_value = False

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        mock_parent_dialog = Mock()
        dialog.delete_playlist('Test Playlist', mock_parent_dialog)

        self.mock_playlist_manager.delete_playlist.assert_not_called()

    @patch('music_playlist_dialog.MusicPlaylistDialog.show_playlists')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.messagebox.showinfo')
    def test_rename_playlist_success(self, mock_showinfo, mock_askstring, mock_show_playlists):
        """測試成功重新命名播放列表"""
        mock_askstring.return_value = 'New Name'
        self.mock_playlist_manager.rename_playlist.return_value = True

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        mock_parent_dialog = Mock()
        dialog.rename_playlist('Old Name', mock_parent_dialog)

        self.mock_playlist_manager.rename_playlist.assert_called_once_with('Old Name', 'New Name')
        mock_showinfo.assert_called_once()
        mock_parent_dialog.destroy.assert_called_once()

    @patch('tkinter.simpledialog.askstring')
    def test_rename_playlist_same_name(self, mock_askstring):
        """測試重新命名播放列表為相同名稱"""
        mock_askstring.return_value = 'Old Name'

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        mock_parent_dialog = Mock()
        dialog.rename_playlist('Old Name', mock_parent_dialog)

        self.mock_playlist_manager.rename_playlist.assert_not_called()

    @patch('music_playlist_dialog.MusicPlaylistDialog.show_playlists')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.messagebox.showinfo')
    def test_edit_description_success(self, mock_showinfo, mock_askstring, mock_show_playlists):
        """測試成功編輯播放列表描述"""
        mock_askstring.return_value = 'New Description'
        self.mock_playlist_manager.update_description.return_value = True

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        mock_parent_dialog = Mock()
        dialog.edit_description('Test Playlist', mock_parent_dialog)

        self.mock_playlist_manager.update_description.assert_called_once_with(
            'Test Playlist',
            'New Description'
        )
        mock_showinfo.assert_called_once()
        mock_parent_dialog.destroy.assert_called_once()

    @patch('tkinter.simpledialog.askstring')
    def test_edit_description_cancelled(self, mock_askstring):
        """測試取消編輯播放列表描述"""
        mock_askstring.return_value = None

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        mock_parent_dialog = Mock()
        dialog.edit_description('Test Playlist', mock_parent_dialog)

        self.mock_playlist_manager.update_description.assert_not_called()

    @patch('music_playlist_dialog.ctk.CTkScrollbar')
    @patch('music_playlist_dialog.ctk.CTkButton')
    @patch('music_playlist_dialog.tk.Listbox')
    @patch('music_playlist_dialog.ctk.CTkLabel')
    @patch('music_playlist_dialog.ctk.CTkFrame')
    @patch('music_playlist_dialog.ctk.CTkToplevel')
    def test_add_song_to_playlist_success(self, mock_toplevel, mock_frame, mock_label,
                                         mock_listbox, mock_button, mock_scrollbar):
        """測試成功加入歌曲到播放列表"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        test_song = {'id': 'song123', 'title': 'Test Song'}
        result = dialog.add_song_to_playlist(test_song)

        self.assertIsNotNone(result)
        mock_toplevel.assert_called_once()

    @patch('tkinter.messagebox.askyesno')
    def test_add_song_no_playlists(self, mock_askyesno):
        """測試加入歌曲時沒有播放列表"""
        mock_askyesno.return_value = False
        self.mock_playlist_manager.get_all_playlists.return_value = []

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        test_song = {'id': 'song123', 'title': 'Test Song'}
        dialog.add_song_to_playlist(test_song)

        mock_askyesno.assert_called_once()

    @patch('music_playlist_dialog.ttk.Style')
    @patch('music_playlist_dialog.ttk.Treeview')
    @patch('music_playlist_dialog.ctk.CTkScrollbar')
    @patch('music_playlist_dialog.ctk.CTkButton')
    @patch('music_playlist_dialog.ctk.CTkLabel')
    @patch('music_playlist_dialog.ctk.CTkFrame')
    @patch('music_playlist_dialog.ctk.CTkToplevel')
    def test_show_playlist_detail(self, mock_toplevel, mock_frame, mock_label,
                                  mock_button, mock_scrollbar, mock_treeview, mock_style):
        """測試顯示播放列表詳情"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        result = dialog.show_playlist_detail('Test Playlist')

        self.assertIsNotNone(result)
        mock_toplevel.assert_called_once()
        self.mock_playlist_manager.get_playlist.assert_called_once_with('Test Playlist')

    @patch('tkinter.messagebox.showerror')
    def test_show_playlist_detail_not_exist(self, mock_showerror):
        """測試顯示不存在的播放列表詳情"""
        self.mock_playlist_manager.get_playlist.return_value = None

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager
        )

        result = dialog.show_playlist_detail('NonExistent')

        self.assertIsNone(result)
        mock_showerror.assert_called_once()

    def test_play_playlist_callback(self):
        """測試播放播放列表回調"""
        mock_callback = Mock()

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager,
            on_play_playlist=mock_callback
        )

        dialog.play_playlist('Test Playlist')

        mock_callback.assert_called_once_with('Test Playlist')

    def test_play_song_callback(self):
        """測試播放歌曲回調"""
        mock_callback = Mock()

        dialog = MusicPlaylistDialog(
            self.mock_parent,
            self.mock_playlist_manager,
            self.mock_music_manager,
            on_play_song=mock_callback
        )

        test_song = {'id': 'song123', 'title': 'Test Song'}
        test_playlist_songs = [test_song]

        dialog.play_song(test_song, test_playlist_songs, 0)

        mock_callback.assert_called_once_with(test_song, test_playlist_songs, 0)


if __name__ == '__main__':
    unittest.main()
