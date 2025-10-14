"""音樂等化器模組

提供 10 頻段等化器設定管理，支援多種預設模式。
注意: 當前版本僅實現設定管理，音訊效果應用功能待未來整合音訊處理庫實現。
"""
import copy


class MusicEqualizer:
    """音樂等化器類別

    管理 10 頻段等化器設定，包含預設模式和自定義設定。
    增益範圍: -12dB 到 +12dB
    預設頻段: 60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000 Hz
    """

    # 預設頻段 (Hz)
    DEFAULT_FREQUENCIES = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000]

    # 增益範圍 (dB)
    MIN_GAIN = -12.0
    MAX_GAIN = 12.0

    # 預設模式定義
    PRESETS = {
        'flat': {
            'name': '平坦',
            'gains': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        'pop': {
            'name': '流行',
            'gains': [4, 3, 2, 0, -1, -1, 2, 3, 4, 5]
        },
        'rock': {
            'name': '搖滾',
            'gains': [5, 4, 3, 2, -1, 0, 2, 4, 5, 6]
        },
        'classical': {
            'name': '古典',
            'gains': [0, 0, 0, 0, 0, 1, 2, 3, 3, 2]
        },
        'jazz': {
            'name': '爵士',
            'gains': [2, 2, 1, 1, 2, 3, 4, 4, 3, 2]
        },
        'vocal': {
            'name': '人聲',
            'gains': [-2, -1, 0, 2, 4, 5, 4, 2, 0, -1]
        },
        'bass_boost': {
            'name': '重低音',
            'gains': [9, 8, 7, 5, 2, 0, -1, -1, 0, 1]
        },
        'soft': {
            'name': '柔和',
            'gains': [-2, -2, -1, -1, -1, -1, -1, -2, -2, -3]
        },
        'custom': {
            'name': '自定義',
            'gains': None  # 使用當前設定
        }
    }

    def __init__(self, config_manager):
        """初始化等化器

        Args:
            config_manager: ConfigManager 實例，用於保存和載入設定
        """
        self.config_manager = config_manager
        self.enabled = False
        self.current_preset = 'flat'

        # 初始化頻段（預設增益為 0）
        self.bands = [
            {'frequency': freq, 'gain': 0.0}
            for freq in self.DEFAULT_FREQUENCIES
        ]

        # 從設定檔載入
        self._load_from_config()

    def _load_from_config(self):
        """從 ConfigManager 載入等化器設定"""
        try:
            settings = self.config_manager.get('music_equalizer')
            if settings and isinstance(settings, dict):
                self.enabled = settings.get('enabled', False)
                self.current_preset = settings.get('preset', 'flat')

                # 載入頻段設定
                saved_bands = settings.get('bands', [])
                if saved_bands and len(saved_bands) == len(self.bands):
                    for i, saved_band in enumerate(saved_bands):
                        if isinstance(saved_band, dict):
                            gain = saved_band.get('gain', 0.0)
                            self.bands[i]['gain'] = self._clamp_gain(gain)
        except Exception:
            # 載入失敗時使用預設值
            pass

    def get_band(self, frequency):
        """根據頻率取得頻段資訊

        Args:
            frequency (int): 頻率 (Hz)

        Returns:
            dict: 頻段資訊 {'frequency': int, 'gain': float} 或 None
        """
        for band in self.bands:
            if band['frequency'] == frequency:
                return band
        return None

    def set_band_gain(self, frequency, gain):
        """設定特定頻段的增益

        Args:
            frequency (int): 頻率 (Hz)
            gain (float): 增益值 (dB)，會自動限制在 -12 到 +12 範圍

        Returns:
            bool: 設定成功返回 True，頻率無效返回 False
        """
        band = self.get_band(frequency)
        if band is None:
            return False

        band['gain'] = self._clamp_gain(gain)

        # 手動修改後，預設模式變為自定義
        if self.current_preset != 'custom':
            # 檢查是否還符合當前預設
            if not self._matches_preset(self.current_preset):
                self.current_preset = 'custom'

        return True

    def _clamp_gain(self, gain):
        """限制增益值在有效範圍內

        Args:
            gain (float): 增益值

        Returns:
            float: 限制後的增益值
        """
        return max(self.MIN_GAIN, min(self.MAX_GAIN, float(gain)))

    def _matches_preset(self, preset_name):
        """檢查當前設定是否符合特定預設

        Args:
            preset_name (str): 預設名稱

        Returns:
            bool: 符合返回 True
        """
        if preset_name not in self.PRESETS:
            return False

        preset = self.PRESETS[preset_name]
        if preset['gains'] is None:  # custom
            return True

        for i, gain in enumerate(preset['gains']):
            if abs(self.bands[i]['gain'] - gain) > 0.1:
                return False

        return True

    def set_enabled(self, enabled):
        """設定等化器啟用狀態

        Args:
            enabled (bool): True 啟用，False 停用
        """
        self.enabled = bool(enabled)

    def is_enabled(self):
        """取得等化器啟用狀態

        Returns:
            bool: 啟用狀態
        """
        return self.enabled

    def reset(self):
        """重置等化器（所有增益設為 0）"""
        for band in self.bands:
            band['gain'] = 0.0
        self.current_preset = 'flat'

    def load_preset(self, preset_name):
        """載入預設 EQ 模式

        Args:
            preset_name (str): 預設名稱
                ('flat', 'pop', 'rock', 'classical', 'jazz',
                 'vocal', 'bass_boost', 'soft', 'custom')

        Returns:
            bool: 載入成功返回 True，無效預設返回 False
        """
        if preset_name not in self.PRESETS:
            return False

        preset = self.PRESETS[preset_name]

        if preset['gains'] is not None:
            # 套用預設的增益值
            for i, gain in enumerate(preset['gains']):
                self.bands[i]['gain'] = float(gain)

        # custom 模式保持當前設定不變

        self.current_preset = preset_name
        return True

    def get_current_preset(self):
        """取得當前預設名稱

        Returns:
            str: 預設名稱
        """
        return self.current_preset

    def get_preset_names(self):
        """取得所有可用的預設名稱

        Returns:
            list: 預設名稱列表
        """
        return ['flat', 'pop', 'rock', 'classical', 'jazz',
                'vocal', 'bass_boost', 'soft', 'custom']

    def get_preset_display_name(self, preset_name):
        """取得預設的顯示名稱

        Args:
            preset_name (str): 預設名稱

        Returns:
            str: 顯示名稱
        """
        if preset_name in self.PRESETS:
            return self.PRESETS[preset_name]['name']
        return preset_name

    def get_bands(self):
        """取得所有頻段資訊

        Returns:
            list: 頻段列表（副本）
        """
        return copy.deepcopy(self.bands)

    def save_settings(self):
        """儲存設定到 ConfigManager"""
        settings = self.to_dict()
        self.config_manager.set('music_equalizer', settings)

    def to_dict(self):
        """轉換為字典格式

        Returns:
            dict: 設定字典
        """
        return {
            'enabled': self.enabled,
            'preset': self.current_preset,
            'bands': [
                {'frequency': band['frequency'], 'gain': band['gain']}
                for band in self.bands
            ]
        }
