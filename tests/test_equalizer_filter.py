"""EqualizerFilter 單元測試"""
import pytest
import numpy as np
from src.audio.equalizer_filter import EqualizerFilter


class TestEqualizerFilterInit:
    """測試初始化功能"""

    def test_init_with_defaults(self):
        """測試使用預設參數初始化"""
        eq = EqualizerFilter()
        assert eq.sample_rate == 44100
        assert eq.frequencies == EqualizerFilter.DEFAULT_FREQUENCIES
        assert eq.q_factor == EqualizerFilter.DEFAULT_Q
        assert len(eq.gains) == 10
        assert all(g == 0.0 for g in eq.gains)

    def test_init_with_custom_sample_rate(self):
        """測試自定義採樣率"""
        eq = EqualizerFilter(sample_rate=48000)
        assert eq.sample_rate == 48000

    def test_init_with_custom_frequencies(self):
        """測試自定義頻段"""
        custom_freqs = [100, 200, 300, 400, 500]
        eq = EqualizerFilter(frequencies=custom_freqs)
        assert eq.frequencies == custom_freqs
        assert len(eq.gains) == 5

    def test_init_with_custom_q_factor(self):
        """測試自定義 Q 因子"""
        eq = EqualizerFilter(q_factor=2.0)
        assert eq.q_factor == 2.0

    def test_filter_coeffs_initialized(self):
        """測試濾波器係數已初始化"""
        eq = EqualizerFilter()
        assert len(eq._filter_coeffs) == 10
        assert len(eq._filter_states) == 10


class TestGainManagement:
    """測試增益管理功能"""

    def test_set_band_gain_valid(self):
        """測試設定有效頻段增益"""
        eq = EqualizerFilter()
        result = eq.set_band_gain(0, 6.0)
        assert result is True
        assert eq.gains[0] == 6.0

    def test_set_band_gain_clamped_upper(self):
        """測試增益上限限制"""
        eq = EqualizerFilter()
        eq.set_band_gain(0, 20.0)  # 超過上限
        assert eq.gains[0] == EqualizerFilter.MAX_GAIN

    def test_set_band_gain_clamped_lower(self):
        """測試增益下限限制"""
        eq = EqualizerFilter()
        eq.set_band_gain(0, -20.0)  # 低於下限
        assert eq.gains[0] == EqualizerFilter.MIN_GAIN

    def test_set_band_gain_invalid_index(self):
        """測試無效頻段索引"""
        eq = EqualizerFilter()
        result = eq.set_band_gain(10, 6.0)  # 超出範圍
        assert result is False
        result = eq.set_band_gain(-1, 6.0)  # 負數索引
        assert result is False

    def test_set_all_gains_valid(self):
        """測試設定所有頻段增益"""
        eq = EqualizerFilter()
        gains = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = eq.set_all_gains(gains)
        assert result is True
        assert eq.gains == gains

    def test_set_all_gains_with_clamping(self):
        """測試設定所有增益時的限制"""
        eq = EqualizerFilter()
        gains = [15, -15, 0, 0, 0, 0, 0, 0, 0, 0]
        result = eq.set_all_gains(gains)
        assert result is True
        assert eq.gains[0] == EqualizerFilter.MAX_GAIN
        assert eq.gains[1] == EqualizerFilter.MIN_GAIN

    def test_set_all_gains_invalid_length(self):
        """測試無效長度的增益列表"""
        eq = EqualizerFilter()
        gains = [1, 2, 3]  # 只有 3 個元素
        result = eq.set_all_gains(gains)
        assert result is False

    def test_get_band_gain_valid(self):
        """測試取得頻段增益"""
        eq = EqualizerFilter()
        eq.set_band_gain(0, 5.0)
        gain = eq.get_band_gain(0)
        assert gain == 5.0

    def test_get_band_gain_invalid_index(self):
        """測試取得無效索引的增益"""
        eq = EqualizerFilter()
        gain = eq.get_band_gain(10)
        assert gain is None

    def test_get_all_gains(self):
        """測試取得所有增益"""
        eq = EqualizerFilter()
        gains = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        eq.set_all_gains(gains)
        retrieved = eq.get_all_gains()
        assert retrieved == gains
        # 確認返回的是副本
        retrieved[0] = 999
        assert eq.gains[0] != 999

    def test_reset(self):
        """測試重置所有增益"""
        eq = EqualizerFilter()
        eq.set_all_gains([5, 5, 5, 5, 5, 5, 5, 5, 5, 5])
        eq.reset()
        assert all(g == 0.0 for g in eq.gains)


class TestAudioProcessing:
    """測試音訊處理功能"""

    def test_process_stereo_audio(self):
        """測試處理立體聲音訊"""
        eq = EqualizerFilter()
        # 建立測試音訊 (1 秒, 44100 Hz)
        duration = 1.0
        sample_rate = 44100
        frames = int(duration * sample_rate)
        audio = np.random.randn(frames, 2).astype(np.float32) * 0.1

        output = eq.process(audio)

        assert output.shape == audio.shape
        assert output.dtype == audio.dtype

    def test_process_mono_audio(self):
        """測試處理單聲道音訊"""
        eq = EqualizerFilter()
        audio = np.random.randn(1000).astype(np.float32) * 0.1

        output = eq.process(audio)

        assert output.ndim == 2
        assert output.shape[1] == 2  # 轉換為立體聲

    def test_process_with_zero_gain(self):
        """測試增益為 0 時的處理 (應該接近無變化)"""
        eq = EqualizerFilter()
        audio = np.random.randn(1000, 2).astype(np.float32) * 0.1

        output = eq.process(audio)

        # 增益為 0 時，輸出應該接近輸入
        assert np.allclose(output, audio, atol=1e-3)

    def test_process_with_positive_gain(self):
        """測試正增益處理"""
        eq = EqualizerFilter()
        eq.set_band_gain(0, 12.0)  # 60Hz 增益 +12dB

        # 建立 60Hz 正弦波
        duration = 0.1
        sample_rate = 44100
        t = np.linspace(0, duration, int(duration * sample_rate))
        audio = np.sin(2 * np.pi * 60 * t).reshape(-1, 1).astype(np.float32) * 0.1

        output = eq.process(audio)

        # 輸出 RMS 應該大於輸入
        input_rms = np.sqrt(np.mean(audio ** 2))
        output_rms = np.sqrt(np.mean(output ** 2))
        assert output_rms > input_rms

    def test_process_with_negative_gain(self):
        """測試負增益處理"""
        eq = EqualizerFilter()
        eq.set_band_gain(0, -12.0)  # 60Hz 增益 -12dB

        # 建立 60Hz 正弦波
        duration = 0.1
        sample_rate = 44100
        t = np.linspace(0, duration, int(duration * sample_rate))
        audio = np.sin(2 * np.pi * 60 * t).reshape(-1, 1).astype(np.float32) * 0.1

        output = eq.process(audio)

        # 輸出 RMS 應該小於輸入
        input_rms = np.sqrt(np.mean(audio ** 2))
        output_rms = np.sqrt(np.mean(output ** 2))
        assert output_rms < input_rms

    def test_process_clipping_prevention(self):
        """測試削波預防"""
        eq = EqualizerFilter()
        eq.set_all_gains([12, 12, 12, 12, 12, 12, 12, 12, 12, 12])

        # 建立高振幅音訊
        audio = np.ones((1000, 2), dtype=np.float32) * 0.9

        output = eq.process(audio)

        # 確保沒有超過 [-1, 1] 範圍
        assert np.all(output >= -1.0)
        assert np.all(output <= 1.0)


class TestFilterCoefficients:
    """測試濾波器係數功能"""

    def test_filter_coeffs_updated_on_gain_change(self):
        """測試增益變化時濾波器係數更新"""
        eq = EqualizerFilter()
        old_coeffs = eq._filter_coeffs[0]

        eq.set_band_gain(0, 6.0)

        new_coeffs = eq._filter_coeffs[0]
        # 係數應該有所變化
        assert not np.array_equal(old_coeffs[0], new_coeffs[0])

    def test_filter_coeffs_no_update_on_same_gain(self):
        """測試相同增益時不更新係數 (優化)"""
        eq = EqualizerFilter()
        eq.set_band_gain(0, 6.0)

        # 再次設定相同增益
        result = eq.set_band_gain(0, 6.0)

        assert result is True  # 應該成功返回

    def test_invalid_frequency_handling(self):
        """測試無效頻率處理 (應返回單位濾波器)"""
        eq = EqualizerFilter(sample_rate=44100)

        # 測試頻率超過 Nyquist 頻率
        b, a = eq._create_peaking_filter(frequency=25000, gain_db=6.0)

        # 應該返回單位濾波器 [1, 0, 0]
        assert np.allclose(b, [1.0, 0.0, 0.0])
        assert np.allclose(a, [1.0, 0.0, 0.0])


class TestFrequencyResponse:
    """測試頻率響應功能"""

    def test_get_frequency_response_shape(self):
        """測試頻率響應輸出格式"""
        eq = EqualizerFilter()
        eq.set_band_gain(0, 6.0)

        freqs, mag_db = eq.get_frequency_response(num_points=500)

        assert len(freqs) == 500
        assert len(mag_db) == 500

    def test_frequency_response_flat_when_zero_gain(self):
        """測試增益為 0 時頻率響應接近平坦"""
        eq = EqualizerFilter()

        freqs, mag_db = eq.get_frequency_response()

        # 應該接近 0 dB (允許小誤差)
        assert np.all(np.abs(mag_db) < 0.1)

    def test_frequency_response_peak_at_target_frequency(self):
        """測試頻率響應在目標頻率處有峰值"""
        eq = EqualizerFilter()
        eq.set_band_gain(4, 12.0)  # 1kHz 增益 +12dB

        freqs, mag_db = eq.get_frequency_response()

        # 找到最接近 1kHz 的頻率索引
        target_idx = np.argmin(np.abs(freqs - 1000))

        # 該頻率處的增益應該是正的且較大
        assert mag_db[target_idx] > 6.0  # 至少 +6dB


# 執行測試時的配置
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
