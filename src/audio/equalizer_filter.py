"""等化器濾波器模組

使用 scipy.signal 實作 10 頻段參數等化器 (Peaking EQ)。
支援即時調整增益，適用於音訊流處理。
"""
import numpy as np
from scipy import signal


class EqualizerFilter:
    """10 頻段參數等化器

    使用 IIR 濾波器實作 peaking EQ，支援即時參數調整。

    頻段配置: 60Hz, 170Hz, 310Hz, 600Hz, 1kHz, 3kHz, 6kHz, 12kHz, 14kHz, 16kHz
    增益範圍: -12dB 到 +12dB
    Q 因子: 1.0 (可調整)
    """

    # 預設頻段 (Hz)
    DEFAULT_FREQUENCIES = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000]

    # 增益範圍 (dB)
    MIN_GAIN = -12.0
    MAX_GAIN = 12.0

    # 預設 Q 因子 (頻寬參數)
    DEFAULT_Q = 1.0

    def __init__(self, sample_rate=44100, frequencies=None, q_factor=DEFAULT_Q):
        """初始化等化器濾波器

        Args:
            sample_rate (int): 採樣率 (Hz)，預設 44100
            frequencies (list): 頻段列表 (Hz)，預設使用 DEFAULT_FREQUENCIES
            q_factor (float): Q 因子，控制頻寬，預設 1.0
        """
        self.sample_rate = sample_rate
        self.frequencies = frequencies if frequencies else self.DEFAULT_FREQUENCIES
        self.q_factor = q_factor

        # 初始化每個頻段的增益 (預設 0 dB)
        self.gains = [0.0] * len(self.frequencies)

        # 濾波器係數快取 (避免重複計算)
        self._filter_coeffs = {}

        # 濾波器狀態 (用於連續處理音訊流)
        self._filter_states = {}

        # 初始化濾波器係數
        self._update_all_filters()

    def _clamp_gain(self, gain):
        """限制增益值在有效範圍內

        Args:
            gain (float): 增益值 (dB)

        Returns:
            float: 限制後的增益值
        """
        return max(self.MIN_GAIN, min(self.MAX_GAIN, float(gain)))

    def _create_peaking_filter(self, frequency, gain_db):
        """建立 peaking EQ 濾波器係數

        Args:
            frequency (float): 中心頻率 (Hz)
            gain_db (float): 增益 (dB)

        Returns:
            tuple: (b, a) 濾波器係數
        """
        # 避免無效頻率
        if frequency <= 0 or frequency >= self.sample_rate / 2:
            # 返回單位濾波器 (無效果)
            return np.array([1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])

        # 增益為 0 時，返回單位濾波器 (節省計算)
        if abs(gain_db) < 0.01:
            return np.array([1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])

        # 計算 peaking EQ 濾波器係數
        A = 10 ** (gain_db / 40.0)  # 振幅增益
        w0 = 2 * np.pi * frequency / self.sample_rate  # 數位角頻率
        alpha = np.sin(w0) / (2 * self.q_factor)  # 頻寬參數

        # 濾波器係數 (Biquad peaking EQ)
        b0 = 1 + alpha * A
        b1 = -2 * np.cos(w0)
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha / A

        # 正規化
        b = np.array([b0 / a0, b1 / a0, b2 / a0])
        a = np.array([1.0, a1 / a0, a2 / a0])

        return b, a

    def _update_all_filters(self):
        """更新所有頻段的濾波器係數"""
        self._filter_coeffs.clear()
        self._filter_states.clear()

        for i, (freq, gain) in enumerate(zip(self.frequencies, self.gains)):
            b, a = self._create_peaking_filter(freq, gain)
            self._filter_coeffs[i] = (b, a)
            # 初始化濾波器狀態 (2 個通道) - 乘以 0 避免初始暫態
            zi = signal.lfilter_zi(b, a)
            self._filter_states[i] = {
                'left': zi * 0.0,
                'right': zi * 0.0
            }

    def set_band_gain(self, band_index, gain_db):
        """設定特定頻段的增益

        Args:
            band_index (int): 頻段索引 (0-9)
            gain_db (float): 增益值 (dB)，會自動限制在 -12 到 +12 範圍

        Returns:
            bool: 設定成功返回 True，索引無效返回 False
        """
        if not 0 <= band_index < len(self.frequencies):
            return False

        # 限制增益範圍
        gain_db = self._clamp_gain(gain_db)

        # 檢查是否有變化
        if abs(self.gains[band_index] - gain_db) < 0.01:
            return True  # 無變化，跳過更新

        # 更新增益
        self.gains[band_index] = gain_db

        # 重新計算該頻段的濾波器係數
        freq = self.frequencies[band_index]
        b, a = self._create_peaking_filter(freq, gain_db)
        self._filter_coeffs[band_index] = (b, a)

        # 重置濾波器狀態 - 乘以 0 避免初始暫態
        zi = signal.lfilter_zi(b, a)
        self._filter_states[band_index] = {
            'left': zi * 0.0,
            'right': zi * 0.0
        }

        return True

    def set_all_gains(self, gains):
        """設定所有頻段的增益

        Args:
            gains (list): 增益列表 (dB)，長度必須等於頻段數量

        Returns:
            bool: 設定成功返回 True，長度不符返回 False
        """
        if len(gains) != len(self.frequencies):
            return False

        # 限制所有增益範圍
        self.gains = [self._clamp_gain(g) for g in gains]

        # 更新所有濾波器
        self._update_all_filters()

        return True

    def get_band_gain(self, band_index):
        """取得特定頻段的增益

        Args:
            band_index (int): 頻段索引 (0-9)

        Returns:
            float: 增益值 (dB)，索引無效返回 None
        """
        if not 0 <= band_index < len(self.frequencies):
            return None
        return self.gains[band_index]

    def get_all_gains(self):
        """取得所有頻段的增益

        Returns:
            list: 增益列表 (dB)
        """
        return self.gains.copy()

    def reset(self):
        """重置所有頻段增益為 0 dB"""
        self.gains = [0.0] * len(self.frequencies)
        self._update_all_filters()

    def process(self, audio_data):
        """處理音訊數據（立體聲）

        Args:
            audio_data (np.ndarray): 音訊數據，shape 為 (frames, 2) 或 (frames, 1)

        Returns:
            np.ndarray: 處理後的音訊數據，shape 與輸入相同
        """
        # 檢查輸入格式
        if audio_data.ndim == 1:
            # 單聲道，轉換為立體聲
            audio_data = audio_data.reshape(-1, 1)

        if audio_data.shape[1] == 1:
            # 單聲道，複製到兩個通道
            audio_data = np.repeat(audio_data, 2, axis=1)

        # 分離左右聲道
        left_channel = audio_data[:, 0].copy()
        right_channel = audio_data[:, 1].copy()

        # 依序應用所有頻段的濾波器
        for i in range(len(self.frequencies)):
            # 跳過增益為 0 的頻段 (優化性能)
            if abs(self.gains[i]) < 0.01:
                continue

            b, a = self._filter_coeffs[i]

            # 處理左聲道
            left_channel, self._filter_states[i]['left'] = signal.lfilter(
                b, a, left_channel, zi=self._filter_states[i]['left']
            )

            # 處理右聲道
            right_channel, self._filter_states[i]['right'] = signal.lfilter(
                b, a, right_channel, zi=self._filter_states[i]['right']
            )

        # 合併聲道
        output = np.column_stack((left_channel, right_channel))

        # 防止削波 (clipping)
        output = np.clip(output, -1.0, 1.0)

        return output

    def get_frequency_response(self, num_points=1000):
        """計算等化器的頻率響應

        Args:
            num_points (int): 頻率點數量

        Returns:
            tuple: (frequencies, magnitude_db) 頻率和增益響應
        """
        # 建立頻率範圍 (20Hz - Nyquist frequency)
        frequencies = np.logspace(
            np.log10(20),
            np.log10(self.sample_rate / 2),
            num_points
        )

        # 計算整體頻率響應 (所有濾波器的乘積)
        w = 2 * np.pi * frequencies / self.sample_rate
        H = np.ones(num_points, dtype=complex)

        for i in range(len(self.frequencies)):
            if abs(self.gains[i]) < 0.01:
                continue  # 跳過增益為 0 的頻段

            b, a = self._filter_coeffs[i]

            # 計算該濾波器的頻率響應
            H_i = (
                b[0] + b[1] * np.exp(-1j * w) + b[2] * np.exp(-2j * w)
            ) / (
                a[0] + a[1] * np.exp(-1j * w) + a[2] * np.exp(-2j * w)
            )

            H *= H_i

        # 轉換為 dB
        magnitude_db = 20 * np.log10(np.abs(H) + 1e-10)

        return frequencies, magnitude_db
