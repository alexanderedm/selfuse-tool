"""音訊處理管線模組

整合音量、等化器等音訊效果，提供統一的音訊處理接口。
支援即時處理音訊流。
"""
import numpy as np
from typing import Optional
from src.audio.equalizer_filter import EqualizerFilter


class AudioProcessor:
    """音訊處理管線

    整合多種音訊效果（等化器、音量等），按順序處理音訊數據。
    設計為即時音訊流處理，支援 sounddevice callback。
    """

    def __init__(self, sample_rate=44100, enable_equalizer=True):
        """初始化音訊處理器

        Args:
            sample_rate (int): 採樣率 (Hz)，預設 44100
            enable_equalizer (bool): 是否啟用等化器，預設 True
        """
        self.sample_rate = sample_rate
        self.volume = 1.0  # 音量 (0.0 - 1.0)

        # 等化器
        self.enable_equalizer = enable_equalizer
        self.equalizer = None
        if self.enable_equalizer:
            self.equalizer = EqualizerFilter(sample_rate=sample_rate)

    def set_volume(self, volume):
        """設定音量

        Args:
            volume (float): 音量 (0.0 - 1.0)
        """
        self.volume = max(0.0, min(1.0, float(volume)))

    def get_volume(self):
        """取得當前音量

        Returns:
            float: 音量 (0.0 - 1.0)
        """
        return self.volume

    def set_equalizer_enabled(self, enabled):
        """啟用或停用等化器

        Args:
            enabled (bool): True 啟用，False 停用
        """
        if enabled and not self.equalizer:
            # 建立等化器
            self.equalizer = EqualizerFilter(sample_rate=self.sample_rate)
        self.enable_equalizer = bool(enabled)

    def is_equalizer_enabled(self):
        """檢查等化器是否啟用

        Returns:
            bool: 啟用狀態
        """
        return self.enable_equalizer and self.equalizer is not None

    def get_equalizer(self) -> Optional[EqualizerFilter]:
        """取得等化器實例

        Returns:
            EqualizerFilter: 等化器實例，如果未啟用則返回 None
        """
        return self.equalizer if self.is_equalizer_enabled() else None

    def process(self, audio_data):
        """處理音訊數據

        按順序應用：1. 等化器 2. 音量調整

        Args:
            audio_data (np.ndarray): 音訊數據，shape 為 (frames, 2) 或 (frames, 1)
                                     數值範圍應在 [-1.0, 1.0]

        Returns:
            np.ndarray: 處理後的音訊數據，shape 與輸入相同
        """
        # 檢查輸入
        if audio_data.size == 0:
            return audio_data

        # 確保數據類型為 float32
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # 複製數據避免修改原始輸入
        output = audio_data.copy()

        # 1. 應用等化器
        if self.is_equalizer_enabled():
            output = self.equalizer.process(output)

        # 2. 應用音量
        if abs(self.volume - 1.0) > 1e-6:  # 避免不必要的乘法
            output = output * self.volume

        # 防止削波
        output = np.clip(output, -1.0, 1.0)

        return output

    def reset(self):
        """重置處理器狀態"""
        self.volume = 1.0
        if self.equalizer:
            self.equalizer.reset()
