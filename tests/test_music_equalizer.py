"""音樂等化器測試模組"""
import unittest
import json
import os
from unittest.mock import Mock, patch
from music_equalizer import MusicEqualizer


class TestMusicEqualizer(unittest.TestCase):
    """MusicEqualizer 測試類別"""

    def setUp(self):
        """測試前設置"""
        self.config_manager = Mock()
        self.config_manager.get.return_value = None
        self.equalizer = MusicEqualizer(self.config_manager)

    def test_init_with_default_settings(self):
        """測試 - 使用預設設定初始化"""
        self.assertIsNotNone(self.equalizer.config_manager)
        self.assertFalse(self.equalizer.enabled)
        self.assertEqual(len(self.equalizer.bands), 10)
        # 預設所有頻段增益為 0
        for band in self.equalizer.bands:
            self.assertEqual(band['gain'], 0.0)

    def test_default_frequency_bands(self):
        """測試 - 預設頻段配置"""
        expected_frequencies = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000]
        actual_frequencies = [band['frequency'] for band in self.equalizer.bands]
        self.assertEqual(actual_frequencies, expected_frequencies)

    def test_get_band_by_frequency(self):
        """測試 - 根據頻率取得頻段"""
        band = self.equalizer.get_band(1000)
        self.assertIsNotNone(band)
        self.assertEqual(band['frequency'], 1000)
        self.assertEqual(band['gain'], 0.0)

    def test_get_band_invalid_frequency(self):
        """測試 - 取得無效頻段返回 None"""
        band = self.equalizer.get_band(9999)
        self.assertIsNone(band)

    def test_set_band_gain_valid(self):
        """測試 - 設定有效的頻段增益"""
        result = self.equalizer.set_band_gain(1000, 6.0)
        self.assertTrue(result)
        band = self.equalizer.get_band(1000)
        self.assertEqual(band['gain'], 6.0)

    def test_set_band_gain_clamp_max(self):
        """測試 - 設定增益超過最大值會被限制"""
        result = self.equalizer.set_band_gain(1000, 15.0)
        self.assertTrue(result)
        band = self.equalizer.get_band(1000)
        self.assertEqual(band['gain'], 12.0)  # 最大值 12dB

    def test_set_band_gain_clamp_min(self):
        """測試 - 設定增益低於最小值會被限制"""
        result = self.equalizer.set_band_gain(1000, -15.0)
        self.assertTrue(result)
        band = self.equalizer.get_band(1000)
        self.assertEqual(band['gain'], -12.0)  # 最小值 -12dB

    def test_set_band_gain_invalid_frequency(self):
        """測試 - 設定無效頻段返回 False"""
        result = self.equalizer.set_band_gain(9999, 6.0)
        self.assertFalse(result)

    def test_enable_equalizer(self):
        """測試 - 啟用等化器"""
        self.equalizer.set_enabled(True)
        self.assertTrue(self.equalizer.enabled)

    def test_disable_equalizer(self):
        """測試 - 停用等化器"""
        self.equalizer.set_enabled(True)
        self.equalizer.set_enabled(False)
        self.assertFalse(self.equalizer.enabled)

    def test_reset_to_flat(self):
        """測試 - 重置為平坦（所有增益為 0）"""
        # 先設定一些增益
        self.equalizer.set_band_gain(1000, 6.0)
        self.equalizer.set_band_gain(3000, -3.0)

        # 重置
        self.equalizer.reset()

        # 驗證所有增益為 0
        for band in self.equalizer.bands:
            self.assertEqual(band['gain'], 0.0)

    def test_load_preset_pop(self):
        """測試 - 載入流行音樂預設"""
        self.equalizer.load_preset('pop')

        # 驗證低音和高音增強
        low_band = self.equalizer.get_band(60)
        high_band = self.equalizer.get_band(12000)
        self.assertGreater(low_band['gain'], 0)
        self.assertGreater(high_band['gain'], 0)

    def test_load_preset_rock(self):
        """測試 - 載入搖滾預設"""
        self.equalizer.load_preset('rock')

        # 驗證中低音和高音增強
        mid_low_band = self.equalizer.get_band(310)
        high_band = self.equalizer.get_band(6000)
        self.assertGreater(mid_low_band['gain'], 0)
        self.assertGreater(high_band['gain'], 0)

    def test_load_preset_classical(self):
        """測試 - 載入古典預設"""
        self.equalizer.load_preset('classical')

        # 驗證中高音略微增強
        mid_high_band = self.equalizer.get_band(3000)
        self.assertGreaterEqual(mid_high_band['gain'], 0)

    def test_load_preset_jazz(self):
        """測試 - 載入爵士預設"""
        self.equalizer.load_preset('jazz')

        # 驗證中音和高音增強
        mid_band = self.equalizer.get_band(1000)
        high_band = self.equalizer.get_band(6000)
        self.assertGreater(mid_band['gain'], 0)
        self.assertGreater(high_band['gain'], 0)

    def test_load_preset_vocal(self):
        """測試 - 載入人聲預設"""
        self.equalizer.load_preset('vocal')

        # 驗證中音頻段增強
        mid_band1 = self.equalizer.get_band(1000)
        mid_band2 = self.equalizer.get_band(3000)
        self.assertGreater(mid_band1['gain'], 0)
        self.assertGreater(mid_band2['gain'], 0)

    def test_load_preset_bass_boost(self):
        """測試 - 載入重低音預設"""
        self.equalizer.load_preset('bass_boost')

        # 驗證低音大幅增強
        low_band1 = self.equalizer.get_band(60)
        low_band2 = self.equalizer.get_band(170)
        self.assertGreater(low_band1['gain'], 6.0)
        self.assertGreater(low_band2['gain'], 6.0)

    def test_load_preset_soft(self):
        """測試 - 載入柔和預設"""
        self.equalizer.load_preset('soft')

        # 驗證所有頻段輕微減弱
        for band in self.equalizer.bands:
            self.assertLessEqual(band['gain'], 0)

    def test_load_preset_custom_keeps_current(self):
        """測試 - 載入自定義預設保持當前設定"""
        # 先設定一些增益
        self.equalizer.set_band_gain(1000, 6.0)
        original_gain = self.equalizer.get_band(1000)['gain']

        # 載入自定義預設
        self.equalizer.load_preset('custom')

        # 驗證設定未改變
        self.assertEqual(self.equalizer.get_band(1000)['gain'], original_gain)

    def test_load_preset_invalid(self):
        """測試 - 載入無效預設返回 False"""
        result = self.equalizer.load_preset('invalid_preset')
        self.assertFalse(result)

    def test_get_current_preset_after_load(self):
        """測試 - 載入預設後取得當前預設名稱"""
        self.equalizer.load_preset('rock')
        self.assertEqual(self.equalizer.get_current_preset(), 'rock')

    def test_get_current_preset_after_manual_change(self):
        """測試 - 手動修改增益後預設變為 custom"""
        self.equalizer.load_preset('rock')
        self.equalizer.set_band_gain(1000, 3.0)
        self.assertEqual(self.equalizer.get_current_preset(), 'custom')

    def test_save_settings(self):
        """測試 - 儲存設定到 ConfigManager"""
        self.equalizer.set_enabled(True)
        self.equalizer.set_band_gain(1000, 6.0)
        self.equalizer.load_preset('rock')

        self.equalizer.save_settings()

        # 驗證 config_manager.set 被呼叫
        self.config_manager.set.assert_called_once()
        args = self.config_manager.set.call_args[0]
        self.assertEqual(args[0], 'music_equalizer')

        # 驗證儲存的資料結構
        saved_data = args[1]
        self.assertTrue(saved_data['enabled'])
        self.assertEqual(saved_data['preset'], 'rock')
        self.assertEqual(len(saved_data['bands']), 10)

    def test_load_settings_from_config(self):
        """測試 - 從 ConfigManager 載入設定"""
        saved_settings = {
            'enabled': True,
            'preset': 'jazz',
            'bands': [
                {'frequency': 60, 'gain': 2.0},
                {'frequency': 170, 'gain': 3.0},
                {'frequency': 310, 'gain': 4.0},
                {'frequency': 600, 'gain': 5.0},
                {'frequency': 1000, 'gain': 6.0},
                {'frequency': 3000, 'gain': 7.0},
                {'frequency': 6000, 'gain': 8.0},
                {'frequency': 12000, 'gain': 9.0},
                {'frequency': 14000, 'gain': 10.0},
                {'frequency': 16000, 'gain': 11.0},
            ]
        }

        self.config_manager.get.return_value = saved_settings

        # 重新建立 equalizer 以載入設定
        equalizer = MusicEqualizer(self.config_manager)

        # 驗證設定已載入
        self.assertTrue(equalizer.enabled)
        self.assertEqual(equalizer.get_current_preset(), 'jazz')
        self.assertEqual(equalizer.get_band(1000)['gain'], 6.0)

    def test_load_settings_with_invalid_data(self):
        """測試 - 載入無效設定時使用預設值"""
        self.config_manager.get.return_value = {'invalid': 'data'}

        # 重新建立 equalizer
        equalizer = MusicEqualizer(self.config_manager)

        # 驗證使用預設設定
        self.assertFalse(equalizer.enabled)
        self.assertEqual(equalizer.get_current_preset(), 'flat')

    def test_get_all_preset_names(self):
        """測試 - 取得所有預設名稱"""
        presets = self.equalizer.get_preset_names()
        expected = ['flat', 'pop', 'rock', 'classical', 'jazz',
                    'vocal', 'bass_boost', 'soft', 'custom']
        self.assertEqual(presets, expected)

    def test_get_bands_returns_copy(self):
        """測試 - get_bands 返回副本而非原始資料"""
        bands = self.equalizer.get_bands()
        bands[0]['gain'] = 999.0

        # 驗證原始資料未被修改
        self.assertNotEqual(self.equalizer.bands[0]['gain'], 999.0)

    def test_to_dict(self):
        """測試 - 轉換為字典格式"""
        self.equalizer.set_enabled(True)
        self.equalizer.load_preset('rock')

        data = self.equalizer.to_dict()

        self.assertTrue(data['enabled'])
        self.assertEqual(data['preset'], 'rock')
        self.assertEqual(len(data['bands']), 10)
        self.assertIn('frequency', data['bands'][0])
        self.assertIn('gain', data['bands'][0])


if __name__ == '__main__':
    unittest.main()
