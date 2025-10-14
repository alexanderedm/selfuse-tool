"""使用統計視窗模組"""
import tkinter as tk
from tkinter import ttk


class StatsWindow:
    """使用統計視窗類別"""

    def __init__(self, config_manager, tk_root=None):
        self.config_manager = config_manager
        self.window = None
        self.tk_root = tk_root  # 使用共用的根視窗

    def show(self):
        """顯示統計視窗"""
        if self._try_raise_existing_window():
            return

        self._initialize_window()
        colors = self._get_theme_colors()
        main_frame = self._create_main_frame(colors)
        self._create_title_section(main_frame, colors)
        stats_container = self._create_stats_container(main_frame, colors)
        self._populate_stats_content(stats_container, colors)

        self.window.protocol("WM_DELETE_WINDOW", self._close_window)
        self.window.mainloop()

    def _try_raise_existing_window(self):
        """嘗試提升已存在的視窗

        Returns:
            bool: 如果視窗已存在則返回 True
        """
        if self.window is not None:
            self.window.lift()
            self.window.focus_force()
            return True
        return False

    def _initialize_window(self):
        """初始化視窗"""
        if self.tk_root:
            self.window = tk.Toplevel(self.tk_root)
        else:
            self.window = tk.Tk()
        self.window.title("📊 使用統計")
        self.window.geometry("700x500")
        self.window.resizable(True, True)

    def _get_theme_colors(self):
        """取得主題顏色配置

        Returns:
            dict: 包含所有顏色配置的字典
        """
        return {
            'bg': "#1e1e1e",
            'card_bg': "#2d2d2d",
            'card_light': "#353535",
            'text': "#e0e0e0",
            'text_secondary': "#a0a0a0",
            'accent': "#4fc3f7"
        }

    def _create_main_frame(self, colors):
        """建立主框架

        Args:
            colors (dict): 顏色配置

        Returns:
            tk.Frame: 主框架
        """
        self.window.configure(bg=colors['bg'])
        main_frame = tk.Frame(self.window, bg=colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        return main_frame

    def _create_title_section(self, main_frame, colors):
        """建立標題區域

        Args:
            main_frame (tk.Frame): 主框架
            colors (dict): 顏色配置
        """
        title_label = tk.Label(
            main_frame,
            text="📊 裝置使用統計",
            font=("Microsoft JhengHei UI", 18, "bold"),
            bg=colors['bg'],
            fg=colors['text']
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = tk.Label(
            main_frame,
            text="查看您的音訊裝置使用情況",
            font=("Microsoft JhengHei UI", 10),
            bg=colors['bg'],
            fg=colors['text_secondary']
        )
        subtitle_label.pack(pady=(0, 25))

    def _create_stats_container(self, main_frame, colors):
        """建立統計內容容器

        Args:
            main_frame (tk.Frame): 主框架
            colors (dict): 顏色配置

        Returns:
            tk.Frame: 統計容器
        """
        stats_container = tk.Frame(main_frame, bg=colors['card_bg'], relief=tk.RIDGE, bd=1)
        stats_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        return stats_container

    def _populate_stats_content(self, stats_container, colors):
        """填充統計內容

        Args:
            stats_container (tk.Frame): 統計容器
            colors (dict): 顏色配置
        """
        stats = self.config_manager.get_usage_stats()

        if not stats:
            self._show_no_data_message(stats_container, colors)
        else:
            self._show_device_stats(stats_container, stats, colors)

    def _show_no_data_message(self, container, colors):
        """顯示無資料訊息

        Args:
            container (tk.Frame): 容器框架
            colors (dict): 顏色配置
        """
        no_data_frame = tk.Frame(container, bg=colors['card_bg'])
        no_data_frame.pack(expand=True)

        no_data_icon = tk.Label(
            no_data_frame,
            text="📭",
            font=("Segoe UI Emoji", 48),
            bg=colors['card_bg'],
            fg=colors['text_secondary']
        )
        no_data_icon.pack(pady=20)

        no_data_label = tk.Label(
            no_data_frame,
            text="目前尚無使用統計資料",
            font=("Microsoft JhengHei UI", 12),
            bg=colors['card_bg'],
            fg=colors['text_secondary']
        )
        no_data_label.pack()

    def _show_device_stats(self, container, stats, colors):
        """顯示裝置統計資料

        Args:
            container (tk.Frame): 容器框架
            stats (dict): 統計資料
            colors (dict): 顏色配置
        """
        stats_inner = tk.Frame(container, bg=colors['card_bg'])
        stats_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        sorted_stats = sorted(stats.items(), key=lambda x: x[1]['total_seconds'], reverse=True)
        total_seconds = sum(data['total_seconds'] for _, data in sorted_stats)

        for idx, (device_id, data) in enumerate(sorted_stats):
            self._create_device_card(stats_inner, idx, data, total_seconds, colors)

    def _create_device_card(self, parent, idx, data, total_seconds, colors):
        """建立裝置統計卡片

        Args:
            parent (tk.Frame): 父框架
            idx (int): 裝置索引
            data (dict): 裝置資料
            total_seconds (float): 總使用秒數
            colors (dict): 顏色配置
        """
        card = tk.Frame(parent, bg=colors['card_light'], relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, pady=8, padx=5)

        card_inner = tk.Frame(card, bg=colors['card_light'])
        card_inner.pack(fill=tk.X, padx=15, pady=15)

        self._create_device_info_section(card_inner, idx, data, colors)
        self._create_device_stats_section(card_inner, data, total_seconds, colors)
        self._create_progress_bar(card_inner, data, total_seconds, colors)

    def _create_device_info_section(self, card_inner, idx, data, colors):
        """建立裝置資訊區域（圖示和名稱）

        Args:
            card_inner (tk.Frame): 卡片內框架
            idx (int): 裝置索引
            data (dict): 裝置資料
            colors (dict): 顏色配置
        """
        left_frame = tk.Frame(card_inner, bg=colors['card_light'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        icon = "🥇" if idx == 0 else "🥈" if idx == 1 else "🎵"

        device_icon = tk.Label(
            left_frame,
            text=icon,
            font=("Segoe UI Emoji", 24),
            bg=colors['card_light']
        )
        device_icon.pack(side=tk.LEFT, padx=(0, 15))

        name_frame = tk.Frame(left_frame, bg=colors['card_light'])
        name_frame.pack(side=tk.LEFT)

        device_name = tk.Label(
            name_frame,
            text=data['name'],
            font=("Microsoft JhengHei UI", 12, "bold"),
            bg=colors['card_light'],
            fg=colors['text'],
            anchor=tk.W
        )
        device_name.pack(anchor=tk.W)

    def _create_device_stats_section(self, card_inner, data, total_seconds, colors):
        """建立裝置統計數據區域

        Args:
            card_inner (tk.Frame): 卡片內框架
            data (dict): 裝置資料
            total_seconds (float): 總使用秒數
            colors (dict): 顏色配置
        """
        right_frame = tk.Frame(card_inner, bg=colors['card_light'])
        right_frame.pack(side=tk.RIGHT)

        time_str = self._format_time(data['total_seconds'])
        time_label = tk.Label(
            right_frame,
            text=f"⏱ {time_str}",
            font=("Microsoft JhengHei UI", 11),
            bg=colors['card_light'],
            fg=colors['accent']
        )
        time_label.pack(anchor=tk.E)

        count_label = tk.Label(
            right_frame,
            text=f"🔄 切換 {data['switch_count']} 次",
            font=("Microsoft JhengHei UI", 10),
            bg=colors['card_light'],
            fg=colors['text_secondary']
        )
        count_label.pack(anchor=tk.E, pady=(3, 0))

        if total_seconds > 0:
            percentage = (data['total_seconds'] / total_seconds) * 100
            percentage_label = tk.Label(
                right_frame,
                text=f"📊 占比 {percentage:.1f}%",
                font=("Microsoft JhengHei UI", 9),
                bg=colors['card_light'],
                fg=colors['text_secondary']
            )
            percentage_label.pack(anchor=tk.E, pady=(3, 0))

    def _create_progress_bar(self, card_inner, data, total_seconds, colors):
        """建立進度條

        Args:
            card_inner (tk.Frame): 卡片內框架
            data (dict): 裝置資料
            total_seconds (float): 總使用秒數
            colors (dict): 顏色配置
        """
        progress_frame = tk.Frame(card_inner, bg=colors['card_light'])
        progress_frame.pack(fill=tk.X, pady=(10, 0))

        if total_seconds > 0:
            percentage = (data['total_seconds'] / total_seconds) * 100
            progress_bar = ttk.Progressbar(
                progress_frame,
                length=600,
                mode='determinate',
                value=percentage
            )
            progress_bar.pack(fill=tk.X)

    def _format_time(self, seconds):
        """將秒數轉換為易讀格式

        Args:
            seconds (float): 秒數

        Returns:
            str: 格式化的時間字串
        """
        if seconds < 60:
            return f"{int(seconds)} 秒"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes} 分 {secs} 秒"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            if hours < 24:
                return f"{hours} 小時 {minutes} 分"
            else:
                days = int(hours / 24)
                remaining_hours = hours % 24
                return f"{days} 天 {remaining_hours} 小時"

    def _close_window(self):
        """關閉視窗"""
        if self.window:
            self.window.destroy()
            self.window = None
        # 不要銷毀共用的根視窗
