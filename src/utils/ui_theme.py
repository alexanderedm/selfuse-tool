"""UI 主題管理模組

提供統一的視覺風格設定，包括配色方案、元件樣式等。
參考 Spotify 深色主題設計。
"""


class UITheme:
    """UI 主題類別

    提供統一的配色方案和元件樣式設定。
    """

    def __init__(self, theme_name='dark'):
        """初始化 UI 主題

        Args:
            theme_name (str): 主題名稱，預設為 'dark'
        """
        self.theme_name = theme_name
        self._init_colors()

    def _init_colors(self):
        """初始化配色方案"""
        if self.theme_name == 'dark':
            # Spotify 風格深色主題
            self.bg_color = "#0f0f0f"          # 主背景色（更深）
            self.card_bg = "#1a1a1a"           # 卡片背景色
            self.accent_color = "#1db954"      # 強調色（Spotify 綠）
            self.text_color = "#ffffff"        # 主要文字色
            self.text_secondary = "#b3b3b3"    # 次要文字色
            self.header_bg = "#282828"         # 標題背景色
            self.hover_bg = "#2a2a2a"          # 懸停背景色
            self.border_color = "#333333"      # 邊框顏色
            self.shadow_color = "#000000"      # 陰影顏色
            self.error_color = "#e22134"       # 錯誤顏色
            self.success_color = "#1db954"     # 成功顏色
            self.warning_color = "#ffa500"     # 警告顏色
        else:
            # 預設深色主題（向後相容）
            self.bg_color = "#0f0f0f"
            self.card_bg = "#1a1a1a"
            self.accent_color = "#1db954"
            self.text_color = "#ffffff"
            self.text_secondary = "#b3b3b3"
            self.header_bg = "#282828"
            self.hover_bg = "#2a2a2a"
            self.border_color = "#333333"
            self.shadow_color = "#000000"
            self.error_color = "#e22134"
            self.success_color = "#1db954"
            self.warning_color = "#ffa500"

    def get_button_style(self, button_type='primary'):
        """取得按鈕樣式

        Args:
            button_type (str): 按鈕類型 ('primary', 'secondary', 'success', 'danger')

        Returns:
            dict: 按鈕樣式設定
        """
        base_style = {
            'font': ("Microsoft JhengHei UI", 10),
            'borderwidth': 0,
            'relief': 'flat',
            'cursor': 'hand2',
            'padx': 15,
            'pady': 8
        }

        if button_type == 'primary':
            return {
                **base_style,
                'bg': self.accent_color,
                'fg': '#000000',
                'activebackground': self.apply_hover_effect(self.accent_color),
                'activeforeground': '#000000'
            }
        elif button_type == 'secondary':
            return {
                **base_style,
                'bg': self.card_bg,
                'fg': self.text_color,
                'activebackground': self.hover_bg,
                'activeforeground': self.text_color
            }
        elif button_type == 'success':
            return {
                **base_style,
                'bg': self.success_color,
                'fg': '#000000',
                'activebackground': self.apply_hover_effect(self.success_color),
                'activeforeground': '#000000'
            }
        elif button_type == 'danger':
            return {
                **base_style,
                'bg': self.error_color,
                'fg': '#ffffff',
                'activebackground': self.apply_hover_effect(self.error_color),
                'activeforeground': '#ffffff'
            }
        else:
            return base_style

    def get_card_style(self):
        """取得卡片樣式

        Returns:
            dict: 卡片樣式設定
        """
        return {
            'bg': self.card_bg,
            'relief': 'flat',
            'bd': 0
        }

    def get_label_style(self, label_type='primary'):
        """取得標籤樣式

        Args:
            label_type (str): 標籤類型 ('primary', 'secondary', 'header')

        Returns:
            dict: 標籤樣式設定
        """
        if label_type == 'primary':
            return {
                'bg': self.bg_color,
                'fg': self.text_color,
                'font': ("Microsoft JhengHei UI", 10)
            }
        elif label_type == 'secondary':
            return {
                'bg': self.bg_color,
                'fg': self.text_secondary,
                'font': ("Microsoft JhengHei UI", 9)
            }
        elif label_type == 'header':
            return {
                'bg': self.header_bg,
                'fg': self.text_color,
                'font': ("Microsoft JhengHei UI", 14, "bold")
            }
        else:
            return {
                'bg': self.bg_color,
                'fg': self.text_color,
                'font': ("Microsoft JhengHei UI", 10)
            }

    def get_rounded_button_style(self):
        """取得圓角按鈕樣式

        Returns:
            dict: 圓角按鈕樣式設定
        """
        return {
            'borderwidth': 0,
            'relief': 'flat',
            'highlightthickness': 0
        }

    def get_shadow_style(self):
        """取得陰影樣式

        Returns:
            dict: 陰影樣式設定
        """
        return {
            'relief': 'raised',
            'bd': 2,
            'highlightbackground': self.shadow_color,
            'highlightthickness': 1
        }

    def apply_hover_effect(self, color):
        """應用懸停效果（調亮顏色）

        Args:
            color (str): 原始顏色（十六進位格式）

        Returns:
            str: 懸停時的顏色
        """
        # 將十六進位顏色轉換為 RGB
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))

        # 調亮顏色（增加 20%）
        factor = 1.2
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))

        # 轉換回十六進位
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_progress_bar_style(self):
        """取得進度條樣式

        Returns:
            dict: 進度條樣式設定
        """
        return {
            'troughcolor': self.card_bg,
            'background': self.accent_color,
            'borderwidth': 0,
            'relief': 'flat'
        }

    def get_slider_style(self):
        """取得滑桿樣式

        Returns:
            dict: 滑桿樣式設定
        """
        return {
            'bg': self.card_bg,
            'fg': self.text_color,
            'troughcolor': self.bg_color,
            'activebackground': self.accent_color,
            'highlightthickness': 0,
            'relief': 'flat'
        }

    def get_text_widget_style(self):
        """取得文字元件樣式

        Returns:
            dict: 文字元件樣式設定
        """
        return {
            'bg': self.bg_color,
            'fg': self.text_color,
            'insertbackground': self.text_color,
            'selectbackground': self.accent_color,
            'selectforeground': '#000000',
            'relief': 'flat',
            'borderwidth': 0
        }

    def get_entry_style(self):
        """取得輸入框樣式

        Returns:
            dict: 輸入框樣式設定
        """
        return {
            'bg': self.card_bg,
            'fg': self.text_color,
            'insertbackground': self.text_color,
            'selectbackground': self.accent_color,
            'selectforeground': '#000000',
            'relief': 'flat',
            'borderwidth': 0
        }
