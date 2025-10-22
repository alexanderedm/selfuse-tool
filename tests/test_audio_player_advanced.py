"""測試 AudioPlayer 高級功能

測試項目：
- 淡入淡出效果
- 播放速度調整
- 睡眠定時器
"""
import pytest
import time
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.audio.audio_player import AudioPlayer


class TestAudioPlayerFade:
    """測試淡入淡出功能"""

    @pytest.fixture
    def player(self):
        """創建測試用的播放器"""
        with patch('src.audio.audio_player.SOUNDDEVICE_AVAILABLE', True):
            player = AudioPlayer()
            return player

    def test_set_fade_enabled(self, player):
        """測試啟用/停用淡入淡出"""
        player.set_fade_enabled(True)
        assert player.fade_enabled is True

        player.set_fade_enabled(False)
        assert player.fade_enabled is False

    def test_set_fade_duration(self, player):
        """測試設定淡入淡出時長"""
        player.set_fade_duration(fade_in=2.0, fade_out=3.0)
        assert player.fade_in_duration == 2.0
        assert player.fade_out_duration == 3.0

        # 測試負值處理
        player.set_fade_duration(fade_in=-1.0)
        assert player.fade_in_duration == 0.0

    def test_apply_fade_in(self, player):
        """測試淡入效果"""
        # 創建測試音訊數據
        chunk = np.ones((100, 2), dtype=np.float32)
        player._fade_in_frames = 50
        player._fade_out_start_frame = 1000

        # 應用淡入
        result = player._apply_fade(chunk, 0)

        # 檢查淡入效果
        assert result[0, 0] < 1.0  # 開始時音量較小
        assert result[49, 0] > result[0, 0]  # 音量逐漸增加

    def test_apply_fade_out(self, player):
        """測試淡出效果"""
        # 創建測試音訊數據
        chunk = np.ones((100, 2), dtype=np.float32)
        player.audio_data = np.ones((1100, 2), dtype=np.float32)
        player._fade_in_frames = 50
        player._fade_out_start_frame = 1000
        player.fade_enabled = True

        # 應用淡出
        result = player._apply_fade(chunk, 1000)

        # 檢查淡出效果
        assert result[0, 0] > result[99, 0]  # 音量逐漸減小


class TestAudioPlayerSpeed:
    """測試播放速度調整功能"""

    @pytest.fixture
    def player(self):
        """創建測試用的播放器"""
        with patch('src.audio.audio_player.SOUNDDEVICE_AVAILABLE', True):
            player = AudioPlayer()
            return player

    def test_set_playback_speed(self, player):
        """測試設定播放速度"""
        player.set_playback_speed(1.5)
        assert player.playback_speed == 1.5

        # 測試邊界值
        player.set_playback_speed(0.3)  # 太小，應該被限制
        assert player.playback_speed == 0.5

        player.set_playback_speed(3.0)  # 太大，應該被限制
        assert player.playback_speed == 2.0

    def test_get_playback_speed(self, player):
        """測試取得播放速度"""
        player.set_playback_speed(1.5)
        assert player.get_playback_speed() == 1.5

    def test_enable_speed_adjustment(self, player):
        """測試啟用速度調整"""
        player.enable_speed_adjustment(True)
        assert player._speed_adjustment_enabled is True

        player.enable_speed_adjustment(False)
        assert player._speed_adjustment_enabled is False

    @patch('src.audio.audio_player.librosa')
    def test_adjust_speed(self, mock_librosa, player):
        """測試速度調整功能"""
        # 創建測試音訊數據
        audio_data = np.random.rand(1000, 2).astype(np.float32)

        # Mock librosa.effects.time_stretch
        mock_librosa.effects.time_stretch.return_value = np.random.rand(800).astype(np.float32)

        # 調整速度
        result = player._adjust_speed(audio_data, 1.25)

        # 檢查 librosa 被調用
        assert mock_librosa.effects.time_stretch.called


class TestAudioPlayerSleepTimer:
    """測試睡眠定時器功能"""

    @pytest.fixture
    def player(self):
        """創建測試用的播放器"""
        with patch('src.audio.audio_player.SOUNDDEVICE_AVAILABLE', True):
            player = AudioPlayer()
            return player

    def test_set_sleep_timer(self, player):
        """測試設定睡眠定時器"""
        # 設定 0.1 分鐘（6 秒）
        result = player.set_sleep_timer(0.1)
        assert result is True
        assert player.has_sleep_timer() is True

        # 清理
        player.cancel_sleep_timer()

    def test_cancel_sleep_timer(self, player):
        """測試取消睡眠定時器"""
        player.set_sleep_timer(0.1)
        player.cancel_sleep_timer()
        assert player.has_sleep_timer() is False

    def test_get_sleep_timer_remaining(self, player):
        """測試取得剩餘時間"""
        # 未設定時應該返回 0
        assert player.get_sleep_timer_remaining() == 0.0

        # 設定定時器
        player.set_sleep_timer(0.1)
        remaining = player.get_sleep_timer_remaining()
        assert 0 < remaining <= 0.1

        # 清理
        player.cancel_sleep_timer()

    def test_sleep_timer_auto_stop(self, player):
        """測試睡眠定時器自動停止"""
        player.stop = Mock()

        # 設定很短的時間（0.01 分鐘 = 0.6 秒）
        player.set_sleep_timer(0.01)

        # 等待定時器觸發
        time.sleep(1.0)

        # 檢查 stop 是否被調用
        player.stop.assert_called_once()

    def test_set_invalid_sleep_timer(self, player):
        """測試設定無效的睡眠定時器"""
        # 負值
        result = player.set_sleep_timer(-1)
        assert result is False

        # 零
        result = player.set_sleep_timer(0)
        assert result is False


class TestAudioPlayerIntegration:
    """整合測試"""

    @pytest.fixture
    def player(self):
        """創建測試用的播放器"""
        with patch('src.audio.audio_player.SOUNDDEVICE_AVAILABLE', True):
            player = AudioPlayer()
            return player

    def test_fade_and_speed_together(self, player):
        """測試淡入淡出和速度調整同時使用"""
        player.set_fade_enabled(True)
        player.set_fade_duration(fade_in=1.0, fade_out=1.0)
        player.enable_speed_adjustment(True)
        player.set_playback_speed(1.5)

        assert player.fade_enabled is True
        assert player._speed_adjustment_enabled is True
        assert player.playback_speed == 1.5

    def test_all_features_disabled(self, player):
        """測試所有功能停用"""
        player.set_fade_enabled(False)
        player.enable_speed_adjustment(False)

        assert player.fade_enabled is False
        assert player._speed_adjustment_enabled is False
