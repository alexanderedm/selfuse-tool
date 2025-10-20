"""測試音樂播放歷史對話框模組"""
import pytest
import tkinter as tk
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from src.music.dialogs.music_history_dialog import MusicHistoryDialog


@pytest.fixture
def mock_window():
    """建立 mock 的主視窗"""
    window = Mock()
    return window


@pytest.fixture
def mock_play_history_manager():
    """建立 mock 的播放歷史管理器"""
    manager = Mock()
    manager.get_total_plays.return_value = 100
    manager.get_recent_plays.return_value = [
        {
            'title': 'Test Song 1',
            'artist': 'Test Artist 1',
            'category': 'Test Category',
            'played_at': '2025-01-15T10:30:00'
        },
        {
            'title': 'Test Song 2',
            'artist': 'Test Artist 2',
            'category': 'Pop',
            'played_at': '2025-01-15T11:00:00'
        }
    ]
    manager.get_most_played.return_value = [
        {
            'song_id': 'song1',
            'play_count': 10
        },
        {
            'song_id': 'song2',
            'play_count': 5
        }
    ]
    manager.clear_history.return_value = None
    return manager


@pytest.fixture
def mock_music_manager():
    """建立 mock 的音樂管理器"""
    manager = Mock()
    manager.get_song_by_id.side_effect = lambda song_id: {
        'song1': {
            'title': 'Most Played Song 1',
            'uploader': 'Artist 1',
            'category': 'Rock'
        },
        'song2': {
            'title': 'Most Played Song 2',
            'uploader': 'Artist 2',
            'category': 'Pop'
        }
    }.get(song_id)
    return manager


@pytest.fixture
def dialog(mock_window, mock_play_history_manager, mock_music_manager):
    """建立 MusicHistoryDialog 實例"""
    return MusicHistoryDialog(
        parent=mock_window,
        play_history_manager=mock_play_history_manager,
        music_manager=mock_music_manager
    )


class TestMusicHistoryDialog:
    """測試 MusicHistoryDialog 類別"""

    def test_init(self, dialog, mock_play_history_manager, mock_music_manager):
        """測試初始化"""
        assert dialog.play_history_manager == mock_play_history_manager
        assert dialog.music_manager == mock_music_manager
        assert dialog.parent is not None

    @patch('src.music.dialogs.music_history_dialog.ttk.Treeview')
    @patch('src.music.dialogs.music_history_dialog.tk.Button')
    @patch('src.music.dialogs.music_history_dialog.tk.Label')
    @patch('src.music.dialogs.music_history_dialog.tk.Frame')
    @patch('src.music.dialogs.music_history_dialog.tk.Scrollbar')
    @patch('src.music.dialogs.music_history_dialog.tk.Toplevel')
    def test_show_play_history_creates_dialog(self, mock_toplevel, mock_scrollbar, mock_frame, mock_label, mock_button, mock_treeview, dialog):
        """測試顯示播放歷史對話框建立"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog

        history_dialog = dialog.show_play_history()

        # 驗證 Toplevel 被建立
        mock_toplevel.assert_called_once_with(dialog.parent)
        assert history_dialog is not None

    @patch('src.music.dialogs.music_history_dialog.ttk.Treeview')
    @patch('src.music.dialogs.music_history_dialog.tk.Button')
    @patch('src.music.dialogs.music_history_dialog.tk.Label')
    @patch('src.music.dialogs.music_history_dialog.tk.Frame')
    @patch('src.music.dialogs.music_history_dialog.tk.Scrollbar')
    @patch('src.music.dialogs.music_history_dialog.tk.Toplevel')
    def test_show_play_history_title(self, mock_toplevel, mock_scrollbar, mock_frame, mock_label, mock_button, mock_treeview, dialog):
        """測試播放歷史對話框標題"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog

        dialog.show_play_history()

        # 驗證標題被設定
        mock_dialog.title.assert_called_once_with("📜 播放歷史")

    @patch('src.music.dialogs.music_history_dialog.ttk.Treeview')
    @patch('src.music.dialogs.music_history_dialog.tk.Button')
    @patch('src.music.dialogs.music_history_dialog.tk.Label')
    @patch('src.music.dialogs.music_history_dialog.tk.Frame')
    @patch('src.music.dialogs.music_history_dialog.tk.Scrollbar')
    @patch('src.music.dialogs.music_history_dialog.tk.Toplevel')
    def test_show_play_history_displays_total_plays(self, mock_toplevel, mock_scrollbar, mock_frame, mock_label, mock_button, mock_treeview, dialog, mock_play_history_manager):
        """測試顯示總播放次數"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog
        mock_play_history_manager.get_total_plays.return_value = 150

        dialog.show_play_history()

        # 驗證 get_total_plays 被調用
        mock_play_history_manager.get_total_plays.assert_called_once()

    @patch('src.music.dialogs.music_history_dialog.ttk.Treeview')
    @patch('src.music.dialogs.music_history_dialog.tk.Button')
    @patch('src.music.dialogs.music_history_dialog.tk.Label')
    @patch('src.music.dialogs.music_history_dialog.tk.Frame')
    @patch('src.music.dialogs.music_history_dialog.tk.Scrollbar')
    @patch('src.music.dialogs.music_history_dialog.tk.Toplevel')
    def test_show_play_history_loads_recent_plays(self, mock_toplevel, mock_scrollbar, mock_frame, mock_label, mock_button, mock_treeview, dialog, mock_play_history_manager):
        """測試載入最近播放記錄"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog

        dialog.show_play_history()

        # 驗證 get_recent_plays 被調用
        mock_play_history_manager.get_recent_plays.assert_called_once_with(limit=50)

    @patch('src.music.dialogs.music_history_dialog.ttk.Treeview')
    @patch('src.music.dialogs.music_history_dialog.tk.Button')
    @patch('src.music.dialogs.music_history_dialog.tk.Label')
    @patch('src.music.dialogs.music_history_dialog.tk.Frame')
    @patch('src.music.dialogs.music_history_dialog.tk.Scrollbar')
    @patch('src.music.dialogs.music_history_dialog.tk.Toplevel')
    def test_show_most_played_creates_dialog(self, mock_toplevel, mock_scrollbar, mock_frame, mock_label, mock_button, mock_treeview, dialog):
        """測試顯示最常播放對話框建立"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog

        most_played_dialog = dialog.show_most_played()

        # 驗證 Toplevel 被建立
        mock_toplevel.assert_called_once_with(dialog.parent)
        assert most_played_dialog is not None

    @patch('src.music.dialogs.music_history_dialog.ttk.Treeview')
    @patch('src.music.dialogs.music_history_dialog.tk.Button')
    @patch('src.music.dialogs.music_history_dialog.tk.Label')
    @patch('src.music.dialogs.music_history_dialog.tk.Frame')
    @patch('src.music.dialogs.music_history_dialog.tk.Scrollbar')
    @patch('src.music.dialogs.music_history_dialog.tk.Toplevel')
    def test_show_most_played_title(self, mock_toplevel, mock_scrollbar, mock_frame, mock_label, mock_button, mock_treeview, dialog):
        """測試最常播放對話框標題"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog

        dialog.show_most_played()

        # 驗證標題被設定
        mock_dialog.title.assert_called_once_with("🏆 最常播放")

    @patch('src.music.dialogs.music_history_dialog.ttk.Treeview')
    @patch('src.music.dialogs.music_history_dialog.tk.Button')
    @patch('src.music.dialogs.music_history_dialog.tk.Label')
    @patch('src.music.dialogs.music_history_dialog.tk.Frame')
    @patch('src.music.dialogs.music_history_dialog.tk.Scrollbar')
    @patch('src.music.dialogs.music_history_dialog.tk.Toplevel')
    def test_show_most_played_loads_data(self, mock_toplevel, mock_scrollbar, mock_frame, mock_label, mock_button, mock_treeview, dialog, mock_play_history_manager):
        """測試載入最常播放資料"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog

        dialog.show_most_played()

        # 驗證 get_most_played 被調用
        mock_play_history_manager.get_most_played.assert_called_once_with(limit=50)

    @patch('src.music.dialogs.music_history_dialog.ttk.Treeview')
    @patch('src.music.dialogs.music_history_dialog.tk.Button')
    @patch('src.music.dialogs.music_history_dialog.tk.Label')
    @patch('src.music.dialogs.music_history_dialog.tk.Frame')
    @patch('src.music.dialogs.music_history_dialog.tk.Scrollbar')
    @patch('src.music.dialogs.music_history_dialog.tk.Toplevel')
    def test_show_most_played_queries_song_details(self, mock_toplevel, mock_scrollbar, mock_frame, mock_label, mock_button, mock_treeview, dialog, mock_music_manager):
        """測試查詢歌曲詳細資訊"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog

        dialog.show_most_played()

        # 驗證 get_song_by_id 被調用
        assert mock_music_manager.get_song_by_id.call_count >= 2

    @patch('src.music.dialogs.music_history_dialog.messagebox.askyesno')
    @patch('src.music.dialogs.music_history_dialog.messagebox.showinfo')
    def test_clear_play_history_with_confirmation(self, mock_showinfo, mock_askyesno, dialog, mock_play_history_manager):
        """測試清除播放歷史(確認)"""
        mock_askyesno.return_value = True
        mock_dialog = Mock()

        dialog._clear_play_history(mock_dialog)

        # 驗證確認對話框被顯示
        mock_askyesno.assert_called_once()
        # 驗證清除方法被調用
        mock_play_history_manager.clear_history.assert_called_once()
        # 驗證成功訊息被顯示
        mock_showinfo.assert_called_once()

    @patch('src.music.dialogs.music_history_dialog.messagebox.askyesno')
    def test_clear_play_history_with_cancel(self, mock_askyesno, dialog, mock_play_history_manager):
        """測試清除播放歷史(取消)"""
        mock_askyesno.return_value = False
        mock_dialog = Mock()

        dialog._clear_play_history(mock_dialog)

        # 驗證確認對話框被顯示
        mock_askyesno.assert_called_once()
        # 驗證清除方法不被調用
        mock_play_history_manager.clear_history.assert_not_called()

    def test_format_play_time(self, dialog):
        """測試播放時間格式化"""
        from datetime import datetime
        test_time = '2025-01-15T10:30:00'
        formatted = dialog._format_play_time(test_time)
        assert '2025-01-15' in formatted
        assert '10:30' in formatted

    def test_get_rank_emoji(self, dialog):
        """測試排名表情符號"""
        assert dialog._get_rank_emoji(1) == "🥇"
        assert dialog._get_rank_emoji(2) == "🥈"
        assert dialog._get_rank_emoji(3) == "🥉"
        assert dialog._get_rank_emoji(4) == "4"
        assert dialog._get_rank_emoji(10) == "10"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
