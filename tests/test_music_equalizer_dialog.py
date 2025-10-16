"""音樂等化器對話框測試模組"""
import unittest
import customtkinter as ctk
from unittest.mock import Mock, patch, MagicMock
from music_equalizer_dialog import MusicEqualizerDialog
from music_equalizer import MusicEqualizer


class TestMusicEqualizerDialog(unittest.TestCase):
    """MusicEqualizerDialog 測試類別"""

    def setUp(self):
        """測試前設置"""
        # 設定 CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
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

        # 驗證開關存在（CustomTkinter 使用 CTkSwitch）
        self.assertIsNotNone(self.dialog.enable_switch)

        # 初始狀態應為停用
        self.assertEqual(self.dialog.enable_switch.get(), 0)

    def test_toggle_enable(self):
        """測試 - 切換啟用狀態"""
        self.dialog.show()

        # 啟用等化器
        self.dialog.enable_switch.select()
        self.dialog._on_enable_toggle()

        self.assertTrue(self.equalizer.is_enabled())

        # 停用等化器
        self.dialog.enable_switch.deselect()
        self.dialog._on_enable_toggle()

        self.assertFalse(self.equalizer.is_enabled())

    def test_create_preset_selector(self):
        """測試 - 建立預設模式選單"""
        self.dialog.show()

        # 驗證選單存在（CustomTkinter 使用 CTkOptionMenu）
        self.assertIsNotNone(self.dialog.preset_menu)

        # 驗證預設值（包含顯示名稱）
        self.assertIn('flat', self.dialog.preset_menu.get())

    def test_preset_change(self):
        """測試 - 切換預設模式"""
        self.dialog.show()

        # 切換到搖滾模式（使用顯示格式: "key - 顯示名稱"）
        self.dialog._on_preset_change('rock - 搖滾')

        # 驗證等化器設定已更新
        self.assertEqual(self.equalizer.get_current_preset(), 'rock')

        # 驗證滑桿已更新
        for i, band in enumerate(self.equalizer.get_bands()):
            slider_value = self.dialog.sliders[i]['slider'].get()
            self.assertAlmostEqual(slider_value, band['gain'], places=1)

    def test_create_band_sliders(self):
        """測試 - 建立頻段滑桿"""
        self.dialog.show()

        # 驗證有 10 個滑桿
        self.assertEqual(len(self.dialog.sliders), 10)

        # 驗證每個滑桿都有必要的元件
        for slider_info in self.dialog.sliders:
            self.assertIn('frequency', slider_info)
            self.assertIn('slider', slider_info)
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
        slider_info['slider'].set(new_gain)
        self.dialog._on_slider_change(frequency, new_gain)

        # 驗證等化器已更新
        band = self.equalizer.get_band(frequency)
        self.assertEqual(band['gain'], new_gain)

    def test_slider_change_sets_custom_preset(self):
        """測試 - 手動調整滑桿後預設變為自定義"""
        self.dialog.show()

        # 先載入一個預設
        self.dialog._on_preset_change('rock - 搖滾')

        # 修改滑桿
        self.dialog._on_slider_change(60, 10.0)

        # 驗證預設變為自定義
        self.assertEqual(self.equalizer.get_current_preset(), 'custom')
        self.assertIn('custom', self.dialog.preset_menu.get())

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
            self.assertEqual(slider_info['slider'].get(), 0.0)

        # 驗證預設為 flat
        self.assertEqual(self.equalizer.get_current_preset(), 'flat')
        self.assertIn('flat', self.dialog.preset_menu.get())

    def test_no_apply_button_exists(self):
        """測試 - 確認沒有套用按鈕（即時生效）"""
        self.dialog.show()

        # 確認對話框沒有 _on_apply 方法被使用
        # 或確認不存在套用按鈕
        self.assertFalse(hasattr(self.dialog, 'apply_button'))

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
        self.assertEqual(dialog.enable_switch.get(), 1)
        self.assertIn('custom', dialog.preset_menu.get())  # 因為修改了增益

        # 驗證滑桿值
        for i, band in enumerate(self.equalizer.get_bands()):
            slider_value = dialog.sliders[i]['slider'].get()
            self.assertAlmostEqual(slider_value, band['gain'], places=1)

        # 清理對話框
        if dialog.dialog:
            dialog.dialog.destroy()
            dialog.dialog = None

    def test_preset_display_names(self):
        """測試 - 預設模式顯示中文名稱"""
        self.dialog.show()

        # 驗證 option menu 的值包含中文名稱
        values = self.dialog.preset_menu.cget('values')
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
            slider = slider_info['slider']
            self.assertEqual(slider.cget('from_'), -12.0)
            self.assertEqual(slider.cget('to'), 12.0)

    def test_note_about_realtime_effect(self):
        """測試 - 顯示即時生效提示說明"""
        self.dialog.show()

        # 驗證對話框包含說明文字
        self.assertTrue(hasattr(self.dialog, 'note_label'))
        note_text = self.dialog.note_label.cget('text')

        # 驗證說明內容（即時生效，無需套用）
        self.assertIn('即時生效', note_text)
        self.assertIn('無需按套用', note_text)

    def test_slider_change_triggers_realtime_sync(self):
        """測試 - 滑桿改變會觸發即時同步到 AudioProcessor"""
        # 建立 mock 回調函數
        sync_callback = Mock()
        self.dialog.on_equalizer_change = sync_callback

        self.dialog.show()

        # 修改滑桿
        frequency = 1000
        new_gain = 5.0
        self.dialog._on_slider_change(frequency, new_gain)

        # 驗證回調被呼叫
        sync_callback.assert_called_once()

    def test_preset_change_triggers_realtime_sync(self):
        """測試 - 預設變更會觸發即時同步到 AudioProcessor"""
        # 建立 mock 回調函數
        sync_callback = Mock()
        self.dialog.on_equalizer_change = sync_callback

        self.dialog.show()

        # 切換預設
        self.dialog._on_preset_change('rock - 搖滾')

        # 驗證回調被呼叫
        sync_callback.assert_called_once()

    def test_enable_toggle_triggers_realtime_sync(self):
        """測試 - 啟用/停用切換會觸發即時同步到 AudioProcessor"""
        # 建立 mock 回調函數
        sync_callback = Mock()
        self.dialog.on_equalizer_change = sync_callback

        self.dialog.show()

        # 切換啟用狀態
        self.dialog.enable_switch.select()
        self.dialog._on_enable_toggle()

        # 驗證回調被呼叫
        sync_callback.assert_called_once()

    def test_reset_triggers_realtime_sync(self):
        """測試 - 重置會觸發即時同步到 AudioProcessor"""
        # 建立 mock 回調函數
        sync_callback = Mock()
        self.dialog.on_equalizer_change = sync_callback

        self.dialog.show()

        # 先設定一些增益
        self.equalizer.set_band_gain(1000, 6.0)

        # 重置計數器
        sync_callback.reset_mock()

        # 點擊重置
        self.dialog._on_reset()

        # 驗證回調被呼叫
        sync_callback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
