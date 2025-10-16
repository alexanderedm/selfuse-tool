"""AudioProcessor 單元測試"""
import pytest
import numpy as np
from src.audio.audio_processor import AudioProcessor


class TestAudioProcessorInit:
    """測試初始化功能"""

    def test_init_with_defaults(self):
        """測試使用預設參數初始化"""
        processor = AudioProcessor()
        assert processor.sample_rate == 44100
        assert processor.volume == 1.0
        assert processor.enable_equalizer is True
        assert processor.equalizer is not None

    def test_init_with_custom_sample_rate(self):
        """測試自定義採樣率"""
        processor = AudioProcessor(sample_rate=48000)
        assert processor.sample_rate == 48000

    def test_init_without_equalizer(self):
        """測試停用等化器初始化"""
        processor = AudioProcessor(enable_equalizer=False)
        assert processor.enable_equalizer is False
        assert processor.equalizer is None

    def test_init_with_equalizer(self):
        """測試啟用等化器初始化"""
        processor = AudioProcessor(enable_equalizer=True)
        assert processor.enable_equalizer is True
        assert processor.equalizer is not None


class TestVolumeControl:
    """測試音量控制功能"""

    def test_set_volume_valid(self):
        """測試設定有效音量"""
        processor = AudioProcessor()
        processor.set_volume(0.5)
        assert processor.volume == 0.5

    def test_set_volume_clamped_upper(self):
        """測試音量上限限制"""
        processor = AudioProcessor()
        processor.set_volume(1.5)
        assert processor.volume == 1.0

    def test_set_volume_clamped_lower(self):
        """測試音量下限限制"""
        processor = AudioProcessor()
        processor.set_volume(-0.5)
        assert processor.volume == 0.0

    def test_get_volume(self):
        """測試取得音量"""
        processor = AudioProcessor()
        processor.set_volume(0.75)
        assert processor.get_volume() == 0.75


class TestEqualizerControl:
    """測試等化器控制功能"""

    def test_set_equalizer_enabled_true(self):
        """測試啟用等化器"""
        processor = AudioProcessor(enable_equalizer=False)
        processor.set_equalizer_enabled(True)
        assert processor.is_equalizer_enabled() is True
        assert processor.equalizer is not None

    def test_set_equalizer_enabled_false(self):
        """測試停用等化器"""
        processor = AudioProcessor(enable_equalizer=True)
        processor.set_equalizer_enabled(False)
        assert processor.is_equalizer_enabled() is False

    def test_get_equalizer_when_enabled(self):
        """測試取得等化器 (啟用時)"""
        processor = AudioProcessor(enable_equalizer=True)
        eq = processor.get_equalizer()
        assert eq is not None
        assert eq is processor.equalizer

    def test_get_equalizer_when_disabled(self):
        """測試取得等化器 (停用時)"""
        processor = AudioProcessor(enable_equalizer=False)
        eq = processor.get_equalizer()
        assert eq is None


class TestAudioProcessing:
    """測試音訊處理功能"""

    def test_process_stereo_audio(self):
        """測試處理立體聲音訊"""
        processor = AudioProcessor(enable_equalizer=False)
        audio = np.random.randn(1000, 2).astype(np.float32) * 0.1
        output = processor.process(audio)
        assert output.shape == audio.shape
        assert output.dtype == np.float32

    def test_process_with_volume(self):
        """測試音量調整"""
        processor = AudioProcessor(enable_equalizer=False)
        processor.set_volume(0.5)

        audio = np.ones((1000, 2), dtype=np.float32) * 0.8
        output = processor.process(audio)

        expected_amplitude = 0.8 * 0.5
        assert np.allclose(output, expected_amplitude, atol=1e-6)

    def test_process_with_zero_volume(self):
        """測試音量為 0 時的處理"""
        processor = AudioProcessor(enable_equalizer=False)
        processor.set_volume(0.0)

        audio = np.random.randn(1000, 2).astype(np.float32)
        output = processor.process(audio)

        assert np.all(output == 0.0)

    def test_process_with_equalizer(self):
        """測試等化器處理"""
        processor = AudioProcessor(enable_equalizer=True)
        eq = processor.get_equalizer()
        eq.set_band_gain(0, 12.0)  # 60Hz +12dB

        # 建立 60Hz 正弦波
        duration = 0.1
        t = np.linspace(0, duration, int(duration * 44100))
        audio = np.sin(2 * np.pi * 60 * t).reshape(-1, 1).astype(np.float32) * 0.1

        output = processor.process(audio)

        # 輸出 RMS 應該大於輸入 (因為增益為正)
        input_rms = np.sqrt(np.mean(audio ** 2))
        output_rms = np.sqrt(np.mean(output ** 2))
        assert output_rms > input_rms

    def test_process_without_equalizer(self):
        """測試停用等化器時的處理"""
        processor = AudioProcessor(enable_equalizer=False)
        audio = np.random.randn(1000, 2).astype(np.float32) * 0.1

        output = processor.process(audio)

        # 沒有等化器且音量為 1.0，輸出應該與輸入接近
        assert np.allclose(output, audio, atol=1e-6)

    def test_process_clipping_prevention(self):
        """測試削波預防"""
        processor = AudioProcessor(enable_equalizer=False)
        processor.set_volume(2.0)  # 過高的音量

        audio = np.ones((1000, 2), dtype=np.float32) * 0.8
        output = processor.process(audio)

        # 確保輸出在 [-1, 1] 範圍內
        assert np.all(output >= -1.0)
        assert np.all(output <= 1.0)

    def test_process_empty_audio(self):
        """測試處理空音訊"""
        processor = AudioProcessor()
        audio = np.array([], dtype=np.float32).reshape(0, 2)
        output = processor.process(audio)
        assert output.size == 0

    def test_process_mono_audio(self):
        """測試處理單聲道音訊"""
        processor = AudioProcessor(enable_equalizer=False)
        audio = np.random.randn(1000, 1).astype(np.float32) * 0.1
        output = processor.process(audio)
        # 應該保持單聲道或轉換為立體聲 (取決於等化器實作)
        assert output.shape[0] == 1000

    def test_process_preserves_input(self):
        """測試處理不修改原始輸入"""
        processor = AudioProcessor()
        audio = np.random.randn(1000, 2).astype(np.float32) * 0.1
        original = audio.copy()

        processor.process(audio)

        # 原始輸入不應該被修改
        assert np.array_equal(audio, original)


class TestReset:
    """測試重置功能"""

    def test_reset_volume(self):
        """測試重置音量"""
        processor = AudioProcessor()
        processor.set_volume(0.5)
        processor.reset()
        assert processor.volume == 1.0

    def test_reset_equalizer(self):
        """測試重置等化器"""
        processor = AudioProcessor(enable_equalizer=True)
        eq = processor.get_equalizer()
        eq.set_band_gain(0, 6.0)

        processor.reset()

        # 等化器應該被重置
        assert eq.get_band_gain(0) == 0.0


class TestIntegration:
    """整合測試"""

    def test_full_processing_pipeline(self):
        """測試完整的處理管線"""
        processor = AudioProcessor(enable_equalizer=True)

        # 設定音量和等化器
        processor.set_volume(0.8)
        eq = processor.get_equalizer()
        eq.set_band_gain(4, 6.0)  # 1kHz +6dB

        # 建立測試音訊 (1kHz 正弦波)
        duration = 0.1
        t = np.linspace(0, duration, int(duration * 44100))
        audio = np.sin(2 * np.pi * 1000 * t).reshape(-1, 1).astype(np.float32) * 0.5

        output = processor.process(audio)

        # 輸出應該存在且在有效範圍內
        assert output.size > 0
        assert np.all(output >= -1.0)
        assert np.all(output <= 1.0)


# 執行測試時的配置
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
