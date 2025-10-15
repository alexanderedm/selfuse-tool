"""音樂等化器對話框測試模組"""
import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from music_equalizer_dialog import MusicEqualizerDialog
from music_equalizer import MusicEqualizer


class TestMusicEqualizerDialog(unittest.TestCase):
    """MusicEqualizerDialog 測試類別"""

    def setUp(self):
        """測試前設置"""
        self.root = tk.Tk()
        self.root.withdraw()

        self.config_manager = Mock()
        self.config_manager.get.return_value = None
        self.equalizer = MusicEqualizer(self.config_manager)

        self.dialog = MusicEqualizerDialog(
            parent=self.root,
            equalizer=self.equalizer
        )

    def tearDown(self):
        """測試後清理"""
        try:
            if self.dialog.dialog:
                self.dialog.dialog.destroy()
        except:
            pass
        try:
            self.root.destroy()
        except:
            pass

    def test_init(self):
        """測試 - 初始化"""
        self.assertIsNotNone(self.dialog.parent)
        self.assertIsNotNone(self.dialog.equalizer)
        self.assertIsNone(self.dialog.dialog)

    def test_show_dialog_creates_window(self):
        """測試 - 顯示對話框建立視窗"""
        self.dialog.show()
        self.assertIsNotNone(self.dialog.dialog)
        self.assertTrue(self.dialog.dialog.winfo_exists())

    def test_show_dialog_twice_raises_existing(self):
        """測試 - 顯示已存在的對話框會提升視窗"""
        self.dialog.show()
        first_dialog = self.dialog.dialog

        self.dialog.show()

        # 驗證是同一個對話框
        self.assertEqual(self.dialog.dialog, first_dialog)

    def test_create_enable_toggle(self):
        """測試 - 建立啟用/停用開關"""
        self.dialog.show()

        # 驗證開關存在
        self.assertIsNotNone(self.dialog.enable_var)
        self.assertIsNotNone(self.dialog.enable_checkbox)

        # 初始狀態應為停用
        self.assertFalse(self.dialog.enable_var.get())

    def test_toggle_enable(self):
        """測試 - 切換啟用狀態"""
        self.dialog.show()

        # 啟用等化器
        self.dialog.enable_var.set(True)
        self.dialog._on_enable_toggle()

        self.assertTrue(self.equalizer.is_enabled())

        # 停用等化器
        self.dialog.enable_var.set(False)
        self.dialog._on_enable_toggle()

        self.assertFalse(self.equalizer.is_enabled())

    def test_create_preset_selector(self):
        """測試 - 建立預設模式選單"""
        self.dialog.show()

        # 驗證選單存在
        self.assertIsNotNone(self.dialog.preset_var)
        self.assertIsNotNone(self.dialog.preset_combo)

        # 驗證預設值（包含顯示名稱）
        self.assertIn('flat', self.dialog.preset_var.get())

    def test_preset_change(self):
        """測試 - 切換預設模式"""
        self.dialog.show()

        # 切換到搖滾模式（使用顯示格式: "key - 顯示名稱"）
        self.dialog.preset_var.set('rock - 搖滾')
        self.dialog._on_preset_change(None)

        # 驗證等化器設定已更新
        self.assertEqual(self.equalizer.get_current_preset(), 'rock')

        # 驗證滑桿已更新
        for i, band in enumerate(self.equalizer.get_bands()):
            slider_value = self.dialog.sliders[i]['var'].get()
            self.assertAlmostEqual(slider_value, band['gain'], places=1)

    def test_create_band_sliders(self):
        """測試 - 建立頻段滑桿"""
        self.dialog.show()

        # 驗證有 10 個滑桿
        self.assertEqual(len(self.dialog.sliders), 10)

        # 驗證每個滑桿都有必要的元件
        for slider_info in self.dialog.sliders:
            self.assertIn('frequency', slider_info)
            self.assertIn('var', slider_info)
            self.assertIn('scale', slider_info)
            self.assertIn('label', slider_info)

    def test_slider_change_updates_equalizer(self):
        """測試 - 滑桿改變更新等化器設定"""
        self.dialog.show()

        # 修改第一個滑桿（60Hz）
        frequency = 60
        new_gain = 6.0

        slider_info = None
        for s in self.dialog.sliders:
            if s['frequency'] == frequency:
                slider_info = s
                break

        self.assertIsNotNone(slider_info)

        # 設定滑桿值
        slider_info['var'].set(new_gain)
        self.dialog._on_slider_change(frequency, new_gain)

        # 驗證等化器已更新
        band = self.equalizer.get_band(frequency)
        self.assertEqual(band['gain'], new_gain)

    def test_slider_change_sets_custom_preset(self):
        """測試 - 手動調整滑桿後預設變為自定義"""
        self.dialog.show()

        # 先載入一個預設
        self.dialog.preset_var.set('rock - 搖滾')
        self.dialog._on_preset_change(None)

        # 修改滑桿
        self.dialog._on_slider_change(60, 10.0)

        # 驗證預設變為自定義
        self.assertEqual(self.equalizer.get_current_preset(), 'custom')
        self.assertIn('custom', self.dialog.preset_var.get())

    def test_reset_button(self):
        """測試 - 重置按鈕"""
        self.dialog.show()

        # 設定一些增益
        self.equalizer.set_band_gain(1000, 6.0)
        self.equalizer.set_band_gain(3000, -3.0)

        # 點擊重置
        self.dialog._on_reset()

        # 驗證所有增益為 0
        for band in self.equalizer.get_bands():
            self.assertEqual(band['gain'], 0.0)

        # 驗證滑桿已重置
        for slider_info in self.dialog.sliders:
            self.assertEqual(slider_info['var'].get(), 0.0)

        # 驗證預設為 flat
        self.assertEqual(self.equalizer.get_current_preset(), 'flat')
        self.assertIn('flat', self.dialog.preset_var.get())

    def test_apply_button_saves_settings(self):
        """測試 - 套用按鈕儲存設定"""
        self.dialog.show()

        # 修改一些設定
        self.equalizer.set_enabled(True)
        self.dialog.enable_var.set(True)
        self.equalizer.load_preset('jazz')

        # 點擊套用
        self.dialog._on_apply()

        # 驗證設定已儲存
        self.config_manager.set.assert_called_once()
        args = self.config_manager.set.call_args[0]
        self.assertEqual(args[0], 'music_equalizer')

    def test_display_gain_values(self):
        """測試 - 顯示增益數值"""
        self.dialog.show()

        # 每個滑桿旁邊應該有顯示當前增益值的標籤
        for slider_info in self.dialog.sliders:
            self.assertIsNotNone(slider_info['label'])

            # 驗證標籤顯示正確格式
            label_text = slider_info['label'].cget('text')
            self.assertIn('dB', label_text)

    def test_load_existing_settings(self):
        """測試 - 載入已存在的設定"""
        # 先設定等化器
        self.equalizer.set_enabled(True)
        self.equalizer.load_preset('rock')
        self.equalizer.set_band_gain(1000, 8.0)

        # 建立對話框
        dialog = MusicEqualizerDialog(
            parent=self.root,
            equalizer=self.equalizer
        )
        dialog.show()

        # 驗證 UI 反映等化器狀態
        self.assertTrue(dialog.enable_var.get())
        self.assertIn('custom', dialog.preset_var.get())  # 因為修改了增益

        # 驗證滑桿值
        for i, band in enumerate(self.equalizer.get_bands()):
            slider_value = dialog.sliders[i]['var'].get()
            self.assertAlmostEqual(slider_value, band['gain'], places=1)

        # 清理對話框
        if dialog.dialog:
            dialog.dialog.destroy()
            dialog.dialog = None

    def test_preset_display_names(self):
        """測試 - 預設模式顯示中文名稱"""
        self.dialog.show()

        # 驗證 combobox 的值包含中文名稱
        values = self.dialog.preset_combo['values']
        self.assertGreater(len(values), 0)

        # 驗證包含中文
        for value in values:
            # 每個值應該是 "key - 中文名稱" 格式
            self.assertIn(' - ', value)

    def test_frequency_labels(self):
        """測試 - 頻率標籤正確顯示"""
        self.dialog.show()

        expected_frequencies = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000]

        for i, slider_info in enumerate(self.dialog.sliders):
            self.assertEqual(slider_info['frequency'], expected_frequencies[i])

    def test_gain_range_limits(self):
        """測試 - 增益範圍限制"""
        self.dialog.show()

        # 驗證滑桿範圍為 -12 到 +12
        for slider_info in self.dialog.sliders:
            scale = slider_info['scale']
            self.assertEqual(scale.cget('from'), -12.0)
            self.assertEqual(scale.cget('to'), 12.0)

    def test_note_about_audio_processing(self):
        """測試 - 顯示音訊處理提示說明"""
        self.dialog.show()

        # 驗證對話框包含說明文字
        # 實際實作中應該有一個 Label 或 Text 顯示說明
        self.assertTrue(hasattr(self.dialog, 'note_label'))
        note_text = self.dialog.note_label.cget('text')

        # 驗證說明內容（新版本提示即時應用）
        self.assertIn('即時應用', note_text)


if __name__ == '__main__':
    unittest.main()
