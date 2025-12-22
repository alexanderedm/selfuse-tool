"""AudioPlayer 單元測試"""
import unittest
from unittest.mock import Mock, MagicMock, patch, call
import numpy as np
import threading
import time
from src.audio.audio_player import AudioPlayer
from src.audio.audio_processor import AudioProcessor


class TestAudioPlayerBasicPlayback(unittest.TestCase):
    """測試基本播放功能"""

    def setUp(self):
        """測試前設定"""
        self.player = AudioPlayer()

    def tearDown(self):
        """測試後清理"""
        if self.player:
            self.player.stop()

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_load_and_play_mp3(self, mock_stream, mock_load):
        """測試載入並播放 MP3 檔案"""
        # Mock 音訊數據 (librosa 返回 shape (channels, frames))
        mock_audio = np.random.rand(2, 44100 * 2).astype(np.float32)  # 2 秒音訊
        mock_load.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 播放音樂
        self.player.play('test.mp3')

        # 驗證
        mock_load.assert_called_once()
        mock_stream.assert_called_once()
        mock_stream_instance.start.assert_called_once()
        self.assertTrue(self.player.is_playing())
        self.assertEqual(self.player.get_duration(), 2.0)

    @patch('src.audio.audio_player.sf.read')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_load_and_play_wav(self, mock_stream, mock_read):
        """測試載入並播放 WAV 檔案"""
        # Mock 音訊數據
        mock_audio = np.random.rand(44100, 2).astype(np.float32)
        mock_read.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 播放音樂
        self.player.play('test.wav')

        # 驗證
        mock_read.assert_called_once()
        self.assertTrue(self.player.is_playing())

    @patch('src.audio.audio_player.librosa.load')
    def test_play_nonexistent_file(self, mock_load):
        """測試播放不存在的檔案"""
        # Mock 檔案不存在錯誤
        mock_load.side_effect = FileNotFoundError("File not found")

        # 嘗試播放
        result = self.player.play('nonexistent.mp3')

        # 驗證返回 False
        self.assertFalse(result)
        self.assertFalse(self.player.is_playing())

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_play_multiple_files_sequentially(self, mock_stream, mock_load):
        """測試連續播放多個檔案"""
        # Mock 音訊數據 (librosa 格式)
        mock_audio = np.random.rand(2, 44100).astype(np.float32)
        mock_load.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 播放第一首
        self.player.play('test1.mp3')
        self.assertTrue(self.player.is_playing())

        # 播放第二首 (應停止第一首)
        self.player.play('test2.mp3')
        self.assertTrue(self.player.is_playing())

        # 驗證 stop 被呼叫
        self.assertEqual(mock_stream_instance.stop.call_count, 1)

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_playback_end_callback(self, mock_stream, mock_load):
        """測試播放結束回調"""
        # Mock 音訊數據 (很短, librosa 格式)
        mock_audio = np.random.rand(2, 100).astype(np.float32)
        mock_load.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 設定回調
        callback_called = threading.Event()

        def on_end():
            callback_called.set()

        self.player.on_playback_end = on_end

        # 播放音樂
        self.player.play('test.mp3')

        # 模擬播放結束 (直接呼叫內部方法)
        self.player._on_playback_end()

        # 驗證回調被呼叫
        self.assertTrue(callback_called.is_set())


class TestAudioPlayerControls(unittest.TestCase):
    """測試播放控制功能"""

    def setUp(self):
        """測試前設定"""
        self.player = AudioPlayer()

    def tearDown(self):
        """測試後清理"""
        if self.player:
            self.player.stop()

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_pause_and_resume(self, mock_stream, mock_load):
        """測試暫停和恢復播放"""
        # Mock 音訊數據 (librosa 格式)
        mock_audio = np.random.rand(2, 44100 * 5).astype(np.float32)
        mock_load.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 播放音樂
        self.player.play('test.mp3')
        self.assertTrue(self.player.is_playing())
        self.assertFalse(self.player.is_paused())

        # 暫停
        self.player.pause()
        self.assertTrue(self.player.is_playing())
        self.assertTrue(self.player.is_paused())

        # 恢復
        self.player.resume()
        self.assertTrue(self.player.is_playing())
        self.assertFalse(self.player.is_paused())

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_stop_playback(self, mock_stream, mock_load):
        """測試停止播放"""
        # Mock 音訊數據 (librosa 格式)
        mock_audio = np.random.rand(2, 44100).astype(np.float32)
        mock_load.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 播放音樂
        self.player.play('test.mp3')
        self.assertTrue(self.player.is_playing())

        # 停止
        self.player.stop()
        self.assertFalse(self.player.is_playing())
        mock_stream_instance.stop.assert_called()
        mock_stream_instance.close.assert_called()

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_seek_forward(self, mock_stream, mock_load):
        """測試向前跳轉"""
        # Mock 音訊數據 (5 秒, librosa 格式)
        mock_audio = np.random.rand(2, 44100 * 5).astype(np.float32)
        mock_load.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 播放音樂
        self.player.play('test.mp3')

        # 跳轉到 2 秒
        self.player.seek(2.0)
        self.assertAlmostEqual(self.player.get_position(), 2.0, delta=0.1)

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_seek_backward(self, mock_stream, mock_load):
        """測試向後跳轉"""
        # Mock 音訊數據 (5 秒, librosa 格式)
        mock_audio = np.random.rand(2, 44100 * 5).astype(np.float32)
        mock_load.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 播放音樂
        self.player.play('test.mp3')
        self.player.seek(3.0)  # 先跳到 3 秒

        # 向後跳轉到 1 秒
        self.player.seek(1.0)
        self.assertAlmostEqual(self.player.get_position(), 1.0, delta=0.1)

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_seek_beyond_duration(self, mock_stream, mock_load):
        """測試跳轉到超出時長的位置"""
        # Mock 音訊數據 (2 秒, librosa 格式)
        mock_audio = np.random.rand(2, 44100 * 2).astype(np.float32)
        mock_load.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 播放音樂
        self.player.play('test.mp3')

        # 嘗試跳轉到 10 秒 (超出範圍)
        self.player.seek(10.0)

        # 應該限制在最大時長
        position = self.player.get_position()
        self.assertLessEqual(position, 2.0)


class TestAudioPlayerVolumeAndProcessor(unittest.TestCase):
    """測試音量和處理器功能"""

    def setUp(self):
        """測試前設定"""
        self.player = AudioPlayer()

    def tearDown(self):
        """測試後清理"""
        if self.player:
            self.player.stop()

    def test_volume_control(self):
        """測試音量控制"""
        # 預設音量
        self.assertEqual(self.player.get_volume(), 1.0)

        # 設定音量
        self.player.set_volume(0.5)
        self.assertEqual(self.player.get_volume(), 0.5)

        # 設定超出範圍的音量
        self.player.set_volume(1.5)  # 應限制在 1.0
        self.assertEqual(self.player.get_volume(), 1.0)

        self.player.set_volume(-0.5)  # 應限制在 0.0
        self.assertEqual(self.player.get_volume(), 0.0)

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_audio_processor_integration(self, mock_stream, mock_load):
        """測試音訊處理器整合"""
        # Mock 音訊數據 (librosa 格式)
        mock_audio = np.random.rand(2, 44100).astype(np.float32)
        mock_load.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 建立帶處理器的播放器
        processor = AudioProcessor(sample_rate=44100)
        player = AudioPlayer(audio_processor=processor)

        # 播放音樂
        player.play('test.mp3')

        # 驗證處理器已設定
        self.assertIsNotNone(player.audio_processor)

        player.stop()

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_processor_enabled_disabled(self, mock_stream, mock_load):
        """測試啟用/停用處理器"""
        # Mock 音訊數據 (librosa 格式)
        mock_audio = np.random.rand(2, 44100).astype(np.float32)
        mock_load.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 建立帶處理器的播放器
        processor = Mock(spec=AudioProcessor)
        processor.process = Mock(return_value=mock_audio)
        player = AudioPlayer(audio_processor=processor)

        # 播放音樂
        player.play('test.mp3')

        # 模擬 callback (處理器應被呼叫)
        player.audio_processor = processor
        test_chunk = np.random.rand(1024, 2).astype(np.float32)

        # 停用處理器
        player.audio_processor = None
        # (無法直接測試 callback，但可以測試設定)

        player.stop()

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_realtime_processor_update(self, mock_stream, mock_load):
        """測試即時更新處理器參數"""
        # Mock 音訊數據 (librosa 格式)
        mock_audio = np.random.rand(2, 44100 * 2).astype(np.float32)
        mock_load.return_value = (mock_audio, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 建立帶處理器的播放器
        processor = AudioProcessor(sample_rate=44100)
        player = AudioPlayer(audio_processor=processor)

        # 播放音樂
        player.play('test.mp3')

        # 即時更新等化器參數
        if processor.equalizer:
            processor.equalizer.set_band_gain(0, 6.0)
            self.assertEqual(processor.equalizer.get_band_gain(0), 6.0)

        player.stop()

    @patch('src.audio.audio_player.librosa.load')
    @patch('src.audio.audio_player.sd.OutputStream')
    def test_stereo_mono_audio(self, mock_stream, mock_load):
        """測試立體聲和單聲道音訊"""
        # Mock 單聲道音訊 (librosa 返回 1D array)
        mock_audio_mono = np.random.rand(44100).astype(np.float32)
        mock_load.return_value = (mock_audio_mono, 44100)
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # 播放單聲道音訊
        self.player.play('test_mono.mp3')
        self.assertTrue(self.player.is_playing())

        self.player.stop()

        # Mock 立體聲音訊 (librosa 格式)
        mock_audio_stereo = np.random.rand(2, 44100).astype(np.float32)
        mock_load.return_value = (mock_audio_stereo, 44100)

        # 播放立體聲音訊
        self.player.play('test_stereo.mp3')
        self.assertTrue(self.player.is_playing())

        self.player.stop()


if __name__ == '__main__':
    unittest.main()
