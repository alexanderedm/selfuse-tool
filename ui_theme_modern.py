"""現代化 UI 主題模組（使用 ttkbootstrap）

提供統一的現代化視覺風格，包括圓角按鈕、精緻配色等。
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ModernUITheme:
    """現代化 UI 主題類別

    使用 ttkbootstrap 提供圓角按鈕、現代配色和精緻視覺效果。
    """

    def __init__(self, theme_name='darkly'):
        """初始化現代化 UI 主題

        Args:
            theme_name (str): ttkbootstrap 主題名稱
                可選: darkly, cyborg, superhero, solar, vapor等
        """
        self.theme_name = theme_name
        self._init_theme()

    def _init_theme(self):
        """初始化主題配色"""
        # ttkbootstrap 主題配色（會根據主題自動調整）
        if self.theme_name == 'darkly':
            # Spotify 風格深色主題
            self.bg_color = "#1a1a1a"
            self.fg_color = "#ffffff"
            self.accent_color = "#1db954"  # Spotify 綠
            self.secondary_color = "#535353"
            self.success_color = "#1db954"
            self.danger_color = "#e22134"
            self.warning_color = "#ffa500"
            self.info_color = "#17a2b8"
        elif self.theme_name == 'cyborg':
            # 科技感深色主題
            self.bg_color = "#060606"
            self.fg_color = "#ffffff"
            self.accent_color = "#2a9fd6"
            self.secondary_color = "#555555"
            self.success_color = "#77b300"
            self.danger_color = "#cc0000"
            self.warning_color = "#ff8800"
            self.info_color = "#33b5e5"
        else:
            # 預設深色主題
            self.bg_color = "#222222"
            self.fg_color = "#ffffff"
            self.accent_color = "#0d6efd"
            self.secondary_color = "#6c757d"
            self.success_color = "#198754"
            self.danger_color = "#dc3545"
            self.warning_color = "#ffc107"
            self.info_color = "#0dcaf0"

    def get_button_style(self, button_type='primary'):
        """取得按鈕樣式（ttkbootstrap 風格）

        Args:
            button_type (str): 按鈕類型
                'primary', 'secondary', 'success', 'danger', 'warning', 'info'

        Returns:
            str: ttkbootstrap 樣式字串
        """
        style_map = {
            'primary': PRIMARY,
            'secondary': SECONDARY,
            'success': SUCCESS,
            'danger': DANGER,
            'warning': WARNING,
            'info': INFO,
            'light': LIGHT,
            'dark': DARK
        }
        return style_map.get(button_type, PRIMARY)

    def create_rounded_button(self, parent, text, command=None, style='primary', **kwargs):
        """創建圓角按鈕

        Args:
            parent: 父容器
            text (str): 按鈕文字
            command: 點擊回調函數
            style (str): 按鈕樣式
            **kwargs: 其他參數

        Returns:
            ttk.Button: 圓角按鈕元件
        """
        bootstyle = self.get_button_style(style)
        button = ttk.Button(
            parent,
            text=text,
            command=command,
            bootstyle=bootstyle,
            **kwargs
        )
        return button

    def create_card_frame(self, parent, **kwargs):
        """創建卡片容器

        Args:
            parent: 父容器
            **kwargs: 其他參數

        Returns:
            ttk.Frame: 卡片容器
        """
        frame = ttk.Frame(parent, bootstyle="dark", **kwargs)
        return frame

    def create_label(self, parent, text, style='default', **kwargs):
        """創建標籤

        Args:
            parent: 父容器
            text (str): 標籤文字
            style (str): 標籤樣式 ('default', 'inverse', 'primary', 'secondary')
            **kwargs: 其他參數

        Returns:
            ttk.Label: 標籤元件
        """
        bootstyle_map = {
            'default': None,
            'inverse': INVERSE,
            'primary': PRIMARY,
            'secondary': SECONDARY,
            'success': SUCCESS,
            'danger': DANGER
        }
        bootstyle = bootstyle_map.get(style)

        label = ttk.Label(parent, text=text, **kwargs)
        if bootstyle:
            label.configure(bootstyle=bootstyle)
        return label

    def create_progress_bar(self, parent, **kwargs):
        """創建進度條

        Args:
            parent: 父容器
            **kwargs: 其他參數

        Returns:
            ttk.Progressbar: 進度條元件
        """
        progressbar = ttk.Progressbar(
            parent,
            bootstyle=f"{SUCCESS}-striped",
            **kwargs
        )
        return progressbar

    def create_scale(self, parent, from_=0, to=100, **kwargs):
        """創建滑桿

        Args:
            parent: 父容器
            from_: 最小值
            to: 最大值
            **kwargs: 其他參數

        Returns:
            ttk.Scale: 滑桿元件
        """
        scale = ttk.Scale(
            parent,
            from_=from_,
            to=to,
            bootstyle=SUCCESS,
            **kwargs
        )
        return scale

    def create_entry(self, parent, **kwargs):
        """創建輸入框

        Args:
            parent: 父容器
            **kwargs: 其他參數

        Returns:
            ttk.Entry: 輸入框元件
        """
        entry = ttk.Entry(parent, **kwargs)
        return entry

    def create_separator(self, parent, **kwargs):
        """創建分隔線

        Args:
            parent: 父容器
            **kwargs: 其他參數

        Returns:
            ttk.Separator: 分隔線元件
        """
        separator = ttk.Separator(parent, **kwargs)
        return separator

    @staticmethod
    def get_available_themes():
        """取得所有可用的主題

        Returns:
            list: 主題名稱列表
        """
        return [
            'darkly',      # 深色主題（類似 Spotify）
            'cyborg',      # 科技感深色主題
            'superhero',   # 超級英雄主題
            'solar',       # 太陽能主題
            'vapor',       # 蒸汽波主題
            'cosmo',       # 宇宙主題
            'flatly',      # 扁平化主題
            'journal',     # 日記主題
            'litera',      # 文學主題
            'lumen',       # 光明主題
            'minty',       # 薄荷主題
            'pulse',       # 脈衝主題
            'sandstone',   # 砂岩主題
            'united',      # 團結主題
            'yeti',        # 雪人主題
            'morph',       # 變形主題
            'quartz',      # 石英主題
            'zephyr',      # 微風主題
        ]
