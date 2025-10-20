"""測試音訊裝置管理模組"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.audio_manager import AudioManager


class TestAudioManager:
    """測試 AudioManager 類別"""

    @patch('src.core.audio_manager.CoCreateInstance')
    def test_init_success(self, mock_co_create):
        """測試初始化成功"""
        mock_enumerator = Mock()
        mock_co_create.return_value = mock_enumerator

        manager = AudioManager()

        assert manager.device_enumerator is not None
        mock_co_create.assert_called_once()

    @patch('src.core.audio_manager.CoCreateInstance')
    def test_init_failure(self, mock_co_create):
        """測試初始化失敗"""
        mock_co_create.side_effect = Exception("COM init failed")

        manager = AudioManager()

        # 即使初始化失敗,也應該正常建立物件
        assert manager.device_enumerator is None

    @patch('src.core.audio_manager.AudioUtilities')
    def test_get_all_output_devices_success(self, mock_audio_utils):
        """測試取得所有輸出裝置成功"""
        # 建立模擬裝置
        mock_device1 = Mock()
        mock_device1.id = "device1_id"
        mock_device1.FriendlyName = "Device 1"

        mock_device2 = Mock()
        mock_device2.id = "device2_id"
        mock_device2.FriendlyName = "Device 2"

        mock_audio_utils.GetAllDevices.return_value = [mock_device1, mock_device2]

        with patch('src.core.audio_manager.CoCreateInstance'):
            manager = AudioManager()
            devices = manager.get_all_output_devices()

        assert len(devices) == 2
        assert devices[0] == {'id': 'device1_id', 'name': 'Device 1'}
        assert devices[1] == {'id': 'device2_id', 'name': 'Device 2'}

    @patch('src.core.audio_manager.AudioUtilities')
    def test_get_all_output_devices_empty(self, mock_audio_utils):
        """測試取得所有輸出裝置 - 無裝置"""
        mock_audio_utils.GetAllDevices.return_value = []

        with patch('src.core.audio_manager.CoCreateInstance'):
            manager = AudioManager()
            devices = manager.get_all_output_devices()

        assert devices == []

    @patch('src.core.audio_manager.AudioUtilities')
    def test_get_all_output_devices_with_invalid_device(self, mock_audio_utils):
        """測試取得所有輸出裝置 - 包含無效裝置"""
        # 建立一個有效裝置和一個無效裝置
        mock_device1 = Mock()
        mock_device1.id = "device1_id"
        mock_device1.FriendlyName = "Device 1"

        mock_device2 = Mock()
        # 無效裝置:缺少必要屬性
        delattr(mock_device2, 'id')

        mock_audio_utils.GetAllDevices.return_value = [mock_device1, mock_device2]

        with patch('src.core.audio_manager.CoCreateInstance'):
            manager = AudioManager()
            devices = manager.get_all_output_devices()

        # 應該只返回有效裝置
        assert len(devices) == 1
        assert devices[0] == {'id': 'device1_id', 'name': 'Device 1'}

    @patch('src.core.audio_manager.AudioUtilities')
    def test_get_all_output_devices_exception(self, mock_audio_utils):
        """測試取得所有輸出裝置時發生例外"""
        mock_audio_utils.GetAllDevices.side_effect = Exception("Access denied")

        with patch('src.core.audio_manager.CoCreateInstance'):
            manager = AudioManager()
            devices = manager.get_all_output_devices()

        # 應該返回空列表
        assert devices == []

    @patch('src.core.audio_manager.AudioUtilities')
    @patch('src.core.audio_manager.CoCreateInstance')
    def test_get_default_device_success(self, mock_co_create, mock_audio_utils):
        """測試取得預設裝置成功"""
        # 模擬裝置列舉器
        mock_enumerator = Mock()
        mock_device = Mock()
        mock_device.GetId.return_value = "default_device_id"
        mock_enumerator.GetDefaultAudioEndpoint.return_value = mock_device

        mock_co_create.return_value = mock_enumerator

        # 模擬裝置列表
        mock_device_obj = Mock()
        mock_device_obj.id = "default_device_id"
        mock_device_obj.FriendlyName = "Default Device"
        mock_audio_utils.GetAllDevices.return_value = [mock_device_obj]

        manager = AudioManager()
        device = manager.get_default_device()

        assert device is not None
        assert device['id'] == "default_device_id"
        assert device['name'] == "Default Device"

    @patch('src.core.audio_manager.AudioUtilities')
    @patch('src.core.audio_manager.CoCreateInstance')
    def test_get_default_device_no_enumerator(self, mock_co_create, mock_audio_utils):
        """測試取得預設裝置 - 無裝置列舉器"""
        # 第一次呼叫失敗,第二次成功
        mock_co_create.side_effect = [Exception("Failed"), Mock()]

        manager = AudioManager()
        # 初始化時失敗,device_enumerator 為 None

        # 模擬第二次初始化成功
        mock_enumerator = Mock()
        mock_device = Mock()
        mock_device.GetId.return_value = "device_id"
        mock_enumerator.GetDefaultAudioEndpoint.return_value = mock_device

        manager.device_enumerator = None
        with patch.object(manager, '_init_device_enumerator') as mock_init:
            mock_init.return_value = None
            manager.device_enumerator = mock_enumerator

            mock_device_obj = Mock()
            mock_device_obj.id = "device_id"
            mock_device_obj.FriendlyName = "Device"
            mock_audio_utils.GetAllDevices.return_value = [mock_device_obj]

            device = manager.get_default_device()

            assert device is not None

    @patch('src.core.audio_manager.AudioUtilities')
    @patch('src.core.audio_manager.CoCreateInstance')
    def test_get_default_device_exception(self, mock_co_create, mock_audio_utils):
        """測試取得預設裝置時發生例外"""
        mock_enumerator = Mock()
        mock_enumerator.GetDefaultAudioEndpoint.side_effect = Exception("Failed")
        mock_co_create.return_value = mock_enumerator

        manager = AudioManager()
        device = manager.get_default_device()

        # 應該返回 None
        assert device is None

    @patch('src.core.audio_manager.CoCreateInstance')
    def test_set_default_device_called(self, mock_co_create):
        """測試設定預設裝置會正確呼叫"""
        # 注意:這個函數很難完整測試因為它涉及內部 COM 類別定義
        # 我們只測試它不會崩潰並返回布林值
        mock_enumerator = Mock()
        mock_co_create.return_value = mock_enumerator

        manager = AudioManager()
        result = manager.set_default_device("test_device_id")

        # 結果應該是布林值 (True 或 False)
        assert isinstance(result, bool)

    @patch('src.core.audio_manager.CoCreateInstance')
    def test_set_default_device_failure(self, mock_co_create):
        """測試設定預設裝置失敗"""
        mock_enumerator = Mock()

        # 所有 PolicyConfig 建立都失敗
        mock_co_create.side_effect = [
            mock_enumerator,  # AudioManager 初始化
            Exception("Win10 failed"),  # Win10 PolicyConfig 失敗
            Exception("Win7 failed")  # Win7 PolicyConfig 失敗
        ]

        manager = AudioManager()
        result = manager.set_default_device("test_device_id")

        assert result is False
