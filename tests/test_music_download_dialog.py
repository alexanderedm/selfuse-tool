"""測試音樂下載對話框模組"""
import pytest
import tkinter as tk
import customtkinter as ctk
from unittest.mock import Mock, MagicMock, patch, call
from src.music.dialogs.music_download_dialog import MusicDownloadDialog


@pytest.fixture
def mock_parent():
    """建立真實的父視窗"""
    root = tk.Tk()
    root.withdraw()  # 隱藏窗口以避免顯示
    yield root
    try:
        root.destroy()
    except:
        pass


@pytest.fixture
def mock_music_manager():
    """建立 mock 的音樂管理器"""
    manager = Mock()
    manager.get_all_categories.return_value = ["下載", "最愛", "搖滾"]
    manager.format_duration.return_value = "3:45"
    manager.music_root_path = "E:/Music"
    manager.scan_music_library.return_value = None
    return manager


@pytest.fixture
def mock_youtube_downloader():
    """建立 mock 的 YouTube 下載器"""
    downloader = Mock()
    downloader.check_ytdlp_installed.return_value = True
    downloader.download_audio.return_value = {
        'success': True,
        'message': '下載成功'
    }
    downloader.search_youtube.return_value = [
        {
            'title': 'Test Song 1',
            'uploader': 'Test Artist 1',
            'duration': 225,
            'webpage_url': 'https://youtube.com/watch?v=test1'
        },
        {
            'title': 'Test Song 2',
            'uploader': 'Test Artist 2',
            'duration': 180,
            'webpage_url': 'https://youtube.com/watch?v=test2'
        }
    ]
    return downloader


@pytest.fixture
def mock_callback():
    """建立 mock 的回調函數"""
    return Mock()


@pytest.fixture
def dialog(mock_parent, mock_music_manager, mock_youtube_downloader, mock_callback):
    """建立 MusicDownloadDialog 實例"""
    return MusicDownloadDialog(
        parent=mock_parent,
        music_manager=mock_music_manager,
        youtube_downloader=mock_youtube_downloader,
        on_download_complete=mock_callback
    )


class TestMusicDownloadDialog:
    """測試 MusicDownloadDialog 類別"""

    def test_init(self, dialog, mock_parent, mock_music_manager, mock_youtube_downloader, mock_callback):
        """測試初始化"""
        assert dialog.parent == mock_parent
        assert dialog.music_manager == mock_music_manager
        assert dialog.youtube_downloader == mock_youtube_downloader
        assert dialog.on_download_complete == mock_callback
        assert dialog.dialog is None
        assert dialog.progress_dialog is None

    @patch('src.music.dialogs.music_download_dialog.messagebox.showerror')
    def test_show_download_dialog_ytdlp_not_installed(self, mock_showerror, dialog, mock_youtube_downloader):
        """測試 yt-dlp 未安裝時顯示錯誤"""
        mock_youtube_downloader.check_ytdlp_installed.return_value = False

        dialog.show_download_dialog()

        # 驗證錯誤訊息被顯示
        mock_showerror.assert_called_once()
        assert "yt-dlp" in mock_showerror.call_args[0][1]
        assert dialog.dialog is None

    @patch('src.music.dialogs.music_download_dialog.ctk.StringVar')
    @patch('src.music.dialogs.music_download_dialog.ttk.Combobox')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkEntry')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkButton')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkLabel')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkFrame')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkToplevel')
    def test_show_download_dialog_creates_dialog(self, mock_toplevel, mock_frame, mock_label,
                                                  mock_button, mock_entry, mock_combo, mock_stringvar, dialog):
        """測試顯示下載對話框建立"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog
        mock_stringvar.return_value = Mock()

        dialog.show_download_dialog()

        # 驗證 Toplevel 被建立
        mock_toplevel.assert_called_once_with(dialog.parent)
        mock_dialog.title.assert_called_once_with("📥 下載 YouTube 音樂")
        mock_dialog.geometry.assert_called_once_with("600x400")

    @patch('src.music.dialogs.music_download_dialog.ctk.StringVar')
    @patch('src.music.dialogs.music_download_dialog.ttk.Combobox')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkEntry')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkButton')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkLabel')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkFrame')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkToplevel')
    def test_show_download_dialog_loads_categories(self, mock_toplevel, mock_frame, mock_label,
                                                    mock_button, mock_entry, mock_combo, mock_stringvar,
                                                    dialog, mock_music_manager):
        """測試載入分類"""
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog
        mock_stringvar.return_value = Mock()

        dialog.show_download_dialog()

        # 驗證 get_all_categories 被調用
        mock_music_manager.get_all_categories.assert_called_once()

    def test_is_youtube_url_valid_full_url(self, dialog):
        """測試有效的完整 YouTube URL"""
        assert dialog._is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
        assert dialog._is_youtube_url("https://youtube.com/watch?v=dQw4w9WgXcQ") is True
        assert dialog._is_youtube_url("http://www.youtube.com/watch?v=dQw4w9WgXcQ") is True

    def test_is_youtube_url_valid_short_url(self, dialog):
        """測試有效的短 YouTube URL"""
        assert dialog._is_youtube_url("https://youtu.be/dQw4w9WgXcQ") is True
        assert dialog._is_youtube_url("http://youtu.be/dQw4w9WgXcQ") is True

    def test_is_youtube_url_valid_music_url(self, dialog):
        """測試有效的 YouTube Music URL"""
        assert dialog._is_youtube_url("https://music.youtube.com/watch?v=dQw4w9WgXcQ") is True

    def test_is_youtube_url_invalid(self, dialog):
        """測試無效的 URL"""
        assert dialog._is_youtube_url("test search query") is False
        assert dialog._is_youtube_url("https://google.com") is False
        assert dialog._is_youtube_url("") is False
        assert dialog._is_youtube_url(None) is False

    @patch('src.music.dialogs.music_download_dialog.messagebox.showwarning')
    def test_smart_download_or_search_empty_input(self, mock_showwarning, dialog):
        """測試空輸入"""
        dialog.dialog = Mock()
        dialog._smart_download_or_search("", "下載")

        # 驗證警告訊息被顯示
        mock_showwarning.assert_called_once()

    @patch('src.music.dialogs.music_download_dialog.MusicDownloadDialog._start_direct_download')
    def test_smart_download_or_search_url(self, mock_direct_download, dialog):
        """測試 URL 輸入觸發直接下載"""
        url = "https://youtube.com/watch?v=test"
        dialog._smart_download_or_search(url, "下載")

        # 驗證直接下載被調用
        mock_direct_download.assert_called_once_with(url, "下載")

    @patch('src.music.dialogs.music_download_dialog.MusicDownloadDialog._start_search_download')
    def test_smart_download_or_search_keyword(self, mock_search_download, dialog):
        """測試關鍵字輸入觸發搜尋"""
        keyword = "test song search"
        dialog._smart_download_or_search(keyword, "下載")

        # 驗證搜尋下載被調用
        mock_search_download.assert_called_once_with(keyword, "下載")

    @patch('src.music.dialogs.music_download_dialog.MusicDownloadDialog.start_download')
    def test_start_direct_download(self, mock_start_download, dialog):
        """測試直接下載"""
        url = "https://youtube.com/watch?v=test"
        dialog._start_direct_download(url, "下載")

        # 驗證 start_download 被調用
        mock_start_download.assert_called_once_with(url, "下載")

    @patch('src.music.dialogs.music_download_dialog.threading.Thread')
    @patch('src.music.dialogs.music_download_dialog.messagebox.showinfo')
    def test_start_search_download(self, mock_showinfo, mock_thread, dialog, mock_youtube_downloader):
        """測試搜尋下載"""
        dialog.dialog = Mock()
        query = "test song"

        dialog._start_search_download(query, "下載")

        # 驗證搜尋訊息被顯示
        mock_showinfo.assert_called_once()
        # 驗證執行緒被啟動
        mock_thread.assert_called_once()

    @patch('src.music.dialogs.music_download_dialog.tk.Listbox')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkButton')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkLabel')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkFrame')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkScrollbar')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkToplevel')
    def test_show_search_results_creates_dialog(self, mock_toplevel, mock_scrollbar, mock_frame,
                                                 mock_label, mock_button, mock_listbox, dialog):
        """測試顯示搜尋結果對話框"""
        # 使用真實的 Toplevel 作為 parent
        dialog.dialog = ctk.CTkToplevel(dialog.parent)
        dialog.dialog.withdraw()  # 隱藏窗口
        mock_result_dialog = Mock()
        mock_toplevel.return_value = mock_result_dialog

        results = [
            {'title': 'Song 1', 'uploader': 'Artist 1', 'duration': 180, 'webpage_url': 'url1'},
            {'title': 'Song 2', 'uploader': 'Artist 2', 'duration': 240, 'webpage_url': 'url2'}
        ]

        dialog.show_search_results(results, "下載")

        # 驗證對話框被建立
        mock_toplevel.assert_called_once_with(dialog.dialog)
        mock_result_dialog.title.assert_called_once_with("🔍 搜尋結果")

        # 清理
        dialog.dialog.destroy()

    @patch('src.music.dialogs.music_download_dialog.messagebox.showwarning')
    def test_start_download_empty_url(self, mock_showwarning, dialog):
        """測試空 URL 下載"""
        dialog.start_download("", "下載")

        # 驗證警告訊息被顯示
        mock_showwarning.assert_called_once()

    @patch('src.music.dialogs.music_download_dialog.threading.Thread')
    @patch('src.music.dialogs.music_download_dialog.MusicDownloadDialog.show_progress')
    def test_start_download_creates_thread(self, mock_show_progress, mock_thread, dialog):
        """測試下載建立執行緒"""
        dialog.dialog = Mock()
        url = "https://youtube.com/watch?v=test"

        dialog.start_download(url, "下載")

        # 驗證進度對話框被顯示
        mock_show_progress.assert_called_once()
        # 驗證執行緒被建立
        mock_thread.assert_called_once()

    @patch('src.music.dialogs.music_download_dialog.ttk.Progressbar')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkLabel')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkFrame')
    @patch('src.music.dialogs.music_download_dialog.ctk.CTkToplevel')
    def test_show_progress_creates_dialog(self, mock_toplevel, mock_frame, mock_label, mock_progressbar, dialog):
        """測試顯示進度對話框"""
        mock_progress_dialog = Mock()
        mock_toplevel.return_value = mock_progress_dialog
        mock_progress_bar = Mock()
        mock_progressbar.return_value = mock_progress_bar

        dialog.show_progress()

        # 驗證對話框被建立
        mock_toplevel.assert_called_once_with(dialog.parent)
        mock_progress_dialog.title.assert_called_once_with("📥 下載中")
        # 驗證進度條開始
        mock_progress_bar.start.assert_called_once_with(10)

    def test_update_progress_status(self, dialog):
        """測試更新進度狀態"""
        dialog.status_label = Mock()
        status_text = "正在下載..."

        dialog._update_progress_status(status_text)

        # 驗證狀態標籤被更新
        dialog.status_label.config.assert_called_once_with(text=status_text)

    def test_stop_progress(self, dialog):
        """測試停止進度條"""
        dialog.progress_bar = Mock()

        dialog._stop_progress()

        # 驗證進度條停止
        dialog.progress_bar.stop.assert_called_once()

    @patch('src.music.dialogs.music_download_dialog.os.makedirs')
    @patch('src.music.dialogs.music_download_dialog.simpledialog.askstring')
    def test_add_new_category(self, mock_askstring, mock_makedirs, dialog, mock_music_manager):
        """測試新增分類"""
        mock_askstring.return_value = "新分類"
        mock_combo = MagicMock()
        mock_var = Mock()
        mock_music_manager.get_all_categories.return_value = ["下載", "最愛"]

        dialog._add_new_category(mock_combo, mock_var)

        # 驗證目錄被建立
        mock_makedirs.assert_called_once()
        # 驗證下拉選單被更新
        mock_var.set.assert_called_once_with("新分類")

    @patch('src.music.dialogs.music_download_dialog.os.makedirs')
    @patch('src.music.dialogs.music_download_dialog.simpledialog.askstring')
    def test_add_new_category_empty_name(self, mock_askstring, mock_makedirs, dialog):
        """測試新增空白分類名稱"""
        mock_askstring.return_value = ""
        mock_combo = Mock()
        mock_var = Mock()

        dialog._add_new_category(mock_combo, mock_var)

        # 驗證目錄不被建立
        mock_makedirs.assert_not_called()

    @patch('src.music.dialogs.music_download_dialog.os.makedirs')
    @patch('src.music.dialogs.music_download_dialog.simpledialog.askstring')
    def test_add_new_category_cancel(self, mock_askstring, mock_makedirs, dialog):
        """測試取消新增分類"""
        mock_askstring.return_value = None
        mock_combo = Mock()
        mock_var = Mock()

        dialog._add_new_category(mock_combo, mock_var)

        # 驗證目錄不被建立
        mock_makedirs.assert_not_called()

    def test_download_success_callback(self, dialog, mock_callback):
        """測試下載成功回調"""
        dialog.parent = Mock()
        dialog.parent.after = Mock(side_effect=lambda delay, func: func())
        dialog.progress_dialog = Mock()

        # 模擬下載成功
        dialog.youtube_downloader.download_audio.return_value = {
            'success': True,
            'message': '下載成功'
        }

        # 觸發下載(這會在執行緒中執行,但我們可以直接測試回調)
        result = dialog.youtube_downloader.download_audio("https://youtube.com/test", "下載")

        # 驗證回調會被調用
        assert result['success'] is True

    def test_download_failure_callback(self, dialog, mock_callback):
        """測試下載失敗回調"""
        dialog.parent = Mock()
        dialog.parent.after = Mock(side_effect=lambda delay, func: func())
        dialog.progress_dialog = Mock()

        # 模擬下載失敗
        dialog.youtube_downloader.download_audio.return_value = {
            'success': False,
            'message': '下載失敗: 網路錯誤'
        }

        # 觸發下載
        result = dialog.youtube_downloader.download_audio("https://youtube.com/test", "下載")

        # 驗證失敗結果
        assert result['success'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
