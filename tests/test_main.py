"""測試主程式模組"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from main import AudioSwitcherApp


class TestAudioSwitcherApp:
    """測試 AudioSwitcherApp 類別"""

    @pytest.fixture
    def mock_tk_root(self):
        """建立模擬的 Tk 根視窗"""
        with patch('main.tk.Tk') as mock_tk:
            root = Mock()
            mock_tk.return_value = root
            yield root

    @pytest.fixture
    def mock_components(self):
        """建立所有必要的模擬元件"""
        with patch('main.AudioManager') as mock_audio, \
             patch('main.ConfigManager') as mock_config, \
             patch('main.RSSManager') as mock_rss, \
             patch('main.ClipboardMonitor') as mock_clipboard, \
             patch('main.MusicManager') as mock_music, \
             patch('main.tk.Tk'):

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
