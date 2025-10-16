"""UI 主題模組測試"""
import unittest
from src.utils.ui_theme import UITheme


class TestUITheme(unittest.TestCase):
    """UITheme 類別測試"""

    def test_init_with_default_theme(self):
        """測試使用預設主題初始化"""
        theme = UITheme()
        self.assertIsNotNone(theme.bg_color)
        self.assertIsNotNone(theme.card_bg)
        self.assertIsNotNone(theme.accent_color)
        self.assertIsNotNone(theme.text_color)

    def test_dark_theme_colors(self):
        """測試深色主題配色"""
        theme = UITheme(theme_name='dark')
        self.assertEqual(theme.bg_color, "#0f0f0f")
        self.assertEqual(theme.card_bg, "#1a1a1a")
        self.assertEqual(theme.accent_color, "#1db954")
        self.assertEqual(theme.text_color, "#ffffff")
        self.assertEqual(theme.text_secondary, "#b3b3b3")
        self.assertEqual(theme.header_bg, "#282828")

    def test_get_button_style(self):
        """測試取得按鈕樣式"""
        theme = UITheme()
        style = theme.get_button_style('primary')
        self.assertIn('bg', style)
        self.assertIn('fg', style)
        self.assertIn('activebackground', style)
        self.assertIn('activeforeground', style)

    def test_get_button_style_hover_effect(self):
        """測試按鈕懸停效果"""
        theme = UITheme()
        style = theme.get_button_style('primary')
        # 驗證懸停顏色比預設顏色更亮或更暗
        self.assertNotEqual(style['bg'], style['activebackground'])

    def test_get_card_style(self):
        """測試取得卡片樣式"""
        theme = UITheme()
        style = theme.get_card_style()
        self.assertIn('bg', style)
        self.assertIn('relief', style)
        self.assertIn('bd', style)

    def test_get_label_style(self):
        """測試取得標籤樣式"""
        theme = UITheme()
        style = theme.get_label_style('primary')
        self.assertIn('bg', style)
        self.assertIn('fg', style)
        self.assertIn('font', style)

    def test_get_rounded_button_style(self):
        """測試取得圓角按鈕樣式"""
        theme = UITheme()
        style = theme.get_rounded_button_style()
        self.assertIn('borderwidth', style)
        self.assertIn('relief', style)
        self.assertEqual(style['borderwidth'], 0)
        self.assertEqual(style['relief'], 'flat')

    def test_get_shadow_style(self):
        """測試取得陰影樣式"""
        theme = UITheme()
        style = theme.get_shadow_style()
        self.assertIn('relief', style)
        self.assertIn('bd', style)
        self.assertGreater(style['bd'], 0)

    def test_apply_hover_effect(self):
        """測試應用懸停效果"""
        theme = UITheme()
        # 模擬懸停效果
        hover_color = theme.apply_hover_effect("#1db954")
        self.assertIsNotNone(hover_color)
        self.assertNotEqual(hover_color, "#1db954")

    def test_get_progress_bar_style(self):
        """測試取得進度條樣式"""
        theme = UITheme()
        style = theme.get_progress_bar_style()
        self.assertIn('troughcolor', style)
        self.assertIn('background', style)

    def test_get_slider_style(self):
        """測試取得滑桿樣式"""
        theme = UITheme()
        style = theme.get_slider_style()
        self.assertIn('bg', style)
        self.assertIn('fg', style)
        self.assertIn('troughcolor', style)
        self.assertIn('activebackground', style)

    def test_theme_consistency(self):
        """測試主題一致性"""
        theme = UITheme()
        # 檢查所有顏色都是有效的十六進位顏色碼
        colors = [
            theme.bg_color,
            theme.card_bg,
            theme.accent_color,
            theme.text_color,
            theme.text_secondary,
            theme.header_bg
        ]
        for color in colors:
            self.assertTrue(color.startswith('#'))
            self.assertTrue(len(color) == 7 or len(color) == 9)


if __name__ == '__main__':
    unittest.main()
