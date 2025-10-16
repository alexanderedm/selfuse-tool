"""測試主程式模組"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.main import AudioSwitcherApp


class TestAudioSwitcherApp:
    """測試 AudioSwitcherApp 類別"""

    @pytest.fixture
    def mock_tk_root(self):
        """建立模擬的 Tk 根視窗"""
        with patch('src.main.tk.Tk') as mock_tk:
            root = Mock()
            mock_tk.return_value = root
            yield root

    @pytest.fixture
    def mock_components(self):
        """建立所有必要的模擬元件"""
        with patch('src.main.AudioManager') as mock_audio, \
             patch('src.main.ConfigManager') as mock_config, \
             patch('src.main.RSSManager') as mock_rss, \
             patch('src.main.ClipboardMonitor') as mock_clipboard, \
             patch('src.main.MusicManager') as mock_music, \
             patch('src.main.tk.Tk'):

            yield {
                'audio': mock_audio,
                'config': mock_config,
                'rss': mock_rss,
                'clipboard': mock_clipboard,
                'music': mock_music
            }

    def test_create_icon_image_blue(self, mock_components):
        """測試建立藍色圖示"""
        app = AudioSwitcherApp()
        image = app.create_icon_image("blue")

        assert image is not None
        assert image.size == (64, 64)

    def test_create_icon_image_green(self, mock_components):
        """測試建立綠色圖示"""
        app = AudioSwitcherApp()
        image = app.create_icon_image("green")

        assert image is not None
        assert image.size == (64, 64)

    def test_create_icon_image_gray(self, mock_components):
        """測試建立灰色圖示"""
        app = AudioSwitcherApp()
        image = app.create_icon_image("gray")

        assert image is not None
        assert image.size == (64, 64)

    def test_get_icon_color_device_a(self, mock_components):
        """測試取得圖示顏色 - 裝置A"""
        app = AudioSwitcherApp()

        # 設定模擬回傳值
        app.audio_manager.get_default_device.return_value = {"id": "device_a_id", "name": "Device A"}
        app.config_manager.get_device_a.return_value = {"id": "device_a_id", "name": "Device A"}
        app.config_manager.get_device_b.return_value = {"id": "device_b_id", "name": "Device B"}

        color = app.get_icon_color()
        assert color == "blue"

    def test_get_icon_color_device_b(self, mock_components):
        """測試取得圖示顏色 - 裝置B"""
        app = AudioSwitcherApp()

        # 設定模擬回傳值
        app.audio_manager.get_default_device.return_value = {"id": "device_b_id", "name": "Device B"}
        app.config_manager.get_device_a.return_value = {"id": "device_a_id", "name": "Device A"}
        app.config_manager.get_device_b.return_value = {"id": "device_b_id", "name": "Device B"}

        color = app.get_icon_color()
        assert color == "green"

    def test_get_icon_color_other_device(self, mock_components):
        """測試取得圖示顏色 - 其他裝置"""
        app = AudioSwitcherApp()

        # 設定模擬回傳值
        app.audio_manager.get_default_device.return_value = {"id": "other_id", "name": "Other"}
        app.config_manager.get_device_a.return_value = {"id": "device_a_id", "name": "Device A"}
        app.config_manager.get_device_b.return_value = {"id": "device_b_id", "name": "Device B"}

        color = app.get_icon_color()
        assert color == "gray"

    def test_get_icon_color_no_device(self, mock_components):
        """測試取得圖示顏色 - 沒有裝置"""
        app = AudioSwitcherApp()

        # 設定模擬回傳值
        app.audio_manager.get_default_device.return_value = None

        color = app.get_icon_color()
        assert color == "gray"

    def test_switch_device_success(self, mock_components):
        """測試切換裝置成功"""
        app = AudioSwitcherApp()
        app.icon = Mock()  # 模擬托盤圖示

        # 設定模擬回傳值
        device_a = {"id": "device_a_id", "name": "Device A"}
        device_b = {"id": "device_b_id", "name": "Device B"}

        app.config_manager.get_device_a.return_value = device_a
        app.config_manager.get_device_b.return_value = device_b
        app.audio_manager.get_default_device.return_value = device_a
        app.audio_manager.set_default_device.return_value = True

        # 執行切換
        app.switch_device()

        # 驗證
        app.audio_manager.set_default_device.assert_called_once_with(device_b["id"])
        app.config_manager.set_current_device.assert_called_once_with(device_b)
        app.config_manager.record_device_usage.assert_called_once_with(device_b)

    def test_switch_device_no_devices_configured(self, mock_components):
        """測試切換裝置 - 未設定裝置"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        # 設定模擬回傳值 - 沒有配置裝置
        app.config_manager.get_device_a.return_value = None
        app.config_manager.get_device_b.return_value = None

        # 執行切換
        app.switch_device()

        # 驗證不會呼叫 set_default_device
        app.audio_manager.set_default_device.assert_not_called()

    def test_switch_device_failure(self, mock_components):
        """測試切換裝置失敗"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        # 設定模擬回傳值
        device_a = {"id": "device_a_id", "name": "Device A"}
        device_b = {"id": "device_b_id", "name": "Device B"}

        app.config_manager.get_device_a.return_value = device_a
        app.config_manager.get_device_b.return_value = device_b
        app.audio_manager.get_default_device.return_value = device_a
        app.audio_manager.set_default_device.return_value = False  # 切換失敗

        # 執行切換
        app.switch_device()

        # 驗證不會呼叫 set_current_device
        app.config_manager.set_current_device.assert_not_called()

    def test_show_notification_with_icon(self, mock_components):
        """測試顯示通知 - 有圖示"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        app.show_notification("測試訊息", "測試標題")
        app.icon.notify.assert_called_once_with("測試訊息", "測試標題")

    def test_show_notification_without_icon(self, mock_components):
        """測試顯示通知 - 無圖示"""
        app = AudioSwitcherApp()
        app.icon = None

        # 應該不會拋出例外
        app.show_notification("測試訊息", "測試標題")

    def test_update_icon_with_device(self, mock_components):
        """測試更新圖示 - 有當前裝置"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        # 設定模擬回傳值
        current_device = {"id": "test_id", "name": "Test Device"}
        app.audio_manager.get_default_device.return_value = current_device
        app.config_manager.get_device_a.return_value = {"id": "test_id", "name": "Test Device"}
        app.config_manager.get_device_b.return_value = {"id": "other_id", "name": "Other"}

        # 執行更新
        app.update_icon()

        # 驗證圖示被更新
        assert app.icon.icon is not None
        assert app.icon.title == "音訊切換工具 - 當前: Test Device"

    def test_update_icon_without_device(self, mock_components):
        """測試更新圖示 - 無當前裝置"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        # 設定模擬回傳值
        app.audio_manager.get_default_device.return_value = None

        # 執行更新
        app.update_icon()

        # 驗證
        assert app.icon.title == "音訊切換工具"

    def test_toggle_auto_start_enable(self, mock_components):
        """測試切換自動啟動 - 啟用"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        # 設定模擬回傳值 - 目前停用
        app.config_manager.get_auto_start.return_value = False

        # 執行切換
        app.toggle_auto_start(None, None)

        # 驗證
        app.config_manager.set_auto_start.assert_called_once_with(True)

    def test_toggle_auto_start_disable(self, mock_components):
        """測試切換自動啟動 - 停用"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        # 設定模擬回傳值 - 目前啟用
        app.config_manager.get_auto_start.return_value = True

        # 執行切換
        app.toggle_auto_start(None, None)

        # 驗證
        app.config_manager.set_auto_start.assert_called_once_with(False)

    def test_on_url_detected_valid_rss(self, mock_components):
        """測試 URL 偵測 - 有效的 RSS"""
        app = AudioSwitcherApp()

        # 設定模擬回傳值
        app.rss_manager.is_valid_rss_url.return_value = True

        with patch.object(app, 'ask_subscribe_rss') as mock_ask:
            app.on_url_detected("https://example.com/feed")
            mock_ask.assert_called_once_with("https://example.com/feed")

    def test_on_url_detected_invalid_rss(self, mock_components):
        """測試 URL 偵測 - 無效的 RSS"""
        app = AudioSwitcherApp()

        # 設定模擬回傳值
        app.rss_manager.is_valid_rss_url.return_value = False

        with patch.object(app, 'ask_subscribe_rss') as mock_ask:
            app.on_url_detected("https://example.com")
            mock_ask.assert_not_called()

    def test_quit_app(self, mock_components):
        """測試結束應用程式"""
        app = AudioSwitcherApp()
        app.icon = Mock()
        app.music_window = Mock()

        # 執行結束
        app.quit_app()

        # 驗證
        app.clipboard_monitor.stop.assert_called_once()
        app.config_manager.update_current_usage.assert_called_once()
        app.music_window.cleanup.assert_called_once()
        app.tk_root.quit.assert_called_once()
        app.icon.stop.assert_called_once()

    def test_create_menu(self, mock_components):
        """測試建立選單"""
        app = AudioSwitcherApp()

        menu = app.create_menu()

        # 驗證選單不為 None
        assert menu is not None

    # ==================== 音樂播放器測試 ====================

    @patch('src.main.MusicWindow')
    def test_open_music_player_first_time(self, mock_music_window, mock_components):
        """測試首次開啟音樂播放器"""
        app = AudioSwitcherApp()
        app.music_window = None

        # 建立 Mock 視窗實例
        mock_window_instance = Mock()
        mock_music_window.return_value = mock_window_instance

        app.open_music_player()

        # 驗證建立新視窗
        mock_music_window.assert_called_once()
        mock_window_instance.show.assert_called_once()

    @patch('src.main.MusicWindow')
    def test_open_music_player_reopen_closed_window(self, mock_music_window, mock_components):
        """測試重新開啟已關閉的音樂播放器視窗"""
        app = AudioSwitcherApp()

        # 模擬視窗已關閉（實例存在但 window 為 None）
        mock_window_instance = Mock()
        mock_window_instance.window = None
        app.music_window = mock_window_instance

        app.open_music_player()

        # 驗證呼叫 show() 重新開啟
        mock_window_instance.show.assert_called_once()

    def test_music_toggle_play_pause_with_window(self, mock_components):
        """測試切換音樂播放/暫停（視窗已開啟）"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        # 建立 Mock 音樂視窗
        mock_window = Mock()
        mock_window.current_song = {'title': 'Test Song'}
        mock_window.is_paused = False
        app.music_window = mock_window

        app.music_toggle_play_pause()

        # 驗證呼叫 _toggle_play_pause
        mock_window._toggle_play_pause.assert_called_once()

    def test_music_toggle_play_pause_no_window(self, mock_components):
        """測試切換音樂播放/暫停（視窗未開啟）"""
        app = AudioSwitcherApp()
        app.icon = Mock()
        app.music_window = None

        app.music_toggle_play_pause()

        # 驗證顯示通知
        app.icon.notify.assert_called_once()

    def test_music_play_next_with_window(self, mock_components):
        """測試播放下一首（視窗已開啟）"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        # 建立 Mock 音樂視窗
        mock_window = Mock()
        mock_window.current_song = {'title': 'Next Song'}
        app.music_window = mock_window

        app.music_play_next()

        # 驗證呼叫 _play_next
        mock_window._play_next.assert_called_once()

    def test_music_play_previous_with_window(self, mock_components):
        """測試播放上一首（視窗已開啟）"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        # 建立 Mock 音樂視窗
        mock_window = Mock()
        mock_window.current_song = {'title': 'Previous Song'}
        app.music_window = mock_window

        app.music_play_previous()

        # 驗證呼叫 _play_previous
        mock_window._play_previous.assert_called_once()

    def test_music_stop_no_window(self, mock_components):
        """測試停止音樂（視窗未開啟）"""
        app = AudioSwitcherApp()
        app.icon = Mock()
        app.music_window = None

        app.music_stop()

        # 驗證顯示通知
        app.icon.notify.assert_called_once()
        assert "沒有正在播放" in app.icon.notify.call_args[0][0]

    # ==================== RSS 視窗測試 ====================

    @patch('src.main.RSSWindow')
    def test_open_rss_viewer_first_time(self, mock_rss_window, mock_components):
        """測試首次開啟 RSS 視窗"""
        app = AudioSwitcherApp()
        app.rss_window = None

        # 建立 Mock 視窗實例
        mock_window_instance = Mock()
        mock_rss_window.return_value = mock_window_instance

        app.open_rss_viewer()

        # 驗證建立新視窗
        mock_rss_window.assert_called_once()
        mock_window_instance.show.assert_called_once()

    @patch('src.main.RSSWindow')
    def test_open_rss_viewer_bring_to_front(self, mock_rss_window, mock_components):
        """測試將 RSS 視窗帶到前景"""
        app = AudioSwitcherApp()

        # 建立已存在的視窗
        mock_window_instance = Mock()
        mock_window = Mock()
        mock_window_instance.window = mock_window
        app.rss_window = mock_window_instance

        app.open_rss_viewer()

        # 驗證將視窗帶到前景
        mock_window.lift.assert_called_once()
        mock_window.focus_force.assert_called_once()

    # ==================== 設定視窗測試 ====================

    @patch('src.main.SettingsWindow')
    def test_open_settings_first_time(self, mock_settings_window, mock_components):
        """測試首次開啟設定視窗"""
        app = AudioSwitcherApp()
        app.settings_window = None

        # 建立 Mock 視窗實例
        mock_window_instance = Mock()
        mock_settings_window.return_value = mock_window_instance

        app.open_settings()

        # 驗證建立新視窗
        mock_settings_window.assert_called_once()
        mock_window_instance.show.assert_called_once()

    # ==================== 統計視窗測試 ====================

    @patch('src.main.StatsWindow')
    def test_open_stats_first_time(self, mock_stats_window, mock_components):
        """測試首次開啟統計視窗"""
        app = AudioSwitcherApp()
        app.stats_window = None

        # 建立 Mock 視窗實例
        mock_window_instance = Mock()
        mock_stats_window.return_value = mock_window_instance

        app.open_stats()

        # 驗證更新使用統計
        app.config_manager.update_current_usage.assert_called_once()
        # 驗證建立新視窗
        mock_stats_window.assert_called_once()
        mock_window_instance.show.assert_called_once()

    # ==================== Log 檢視器測試 ====================

    @patch('src.main.os.path.exists')
    @patch('src.main.os.startfile')
    def test_open_log_viewer_success(self, mock_startfile, mock_exists, mock_components):
        """測試開啟 Log 檢視器（檔案存在）"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        # 模擬檔案存在
        mock_exists.return_value = True

        app.open_log_viewer()

        # 驗證呼叫 startfile
        mock_startfile.assert_called_once()

    @patch('src.main.os.path.exists')
    def test_open_log_viewer_file_not_found(self, mock_exists, mock_components):
        """測試開啟 Log 檢視器（檔案不存在）"""
        app = AudioSwitcherApp()
        app.icon = Mock()

        # 模擬檔案不存在
        mock_exists.return_value = False

        app.open_log_viewer()

        # 驗證顯示錯誤通知
        app.icon.notify.assert_called_once()
        assert "Log 檔案不存在" in app.icon.notify.call_args[0][0]
