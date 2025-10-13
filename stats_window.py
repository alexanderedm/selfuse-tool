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
        if self.window is not None:
            self.window.lift()
            self.window.focus_force()
            return

        # 使用共用的根視窗建立 Toplevel 視窗
        if self.tk_root:
            self.window = tk.Toplevel(self.tk_root)
        else:
            # 如果沒有提供根視窗,建立獨立的視窗
            self.window = tk.Tk()
        self.window.title("📊 使用統計")
        self.window.geometry("700x500")
        self.window.resizable(True, True)

        # 設定深色主題顏色
        bg_color = "#1e1e1e"
        card_bg = "#2d2d2d"
        card_light = "#353535"
        text_color = "#e0e0e0"
        text_secondary = "#a0a0a0"
        accent_color = "#4fc3f7"
        self.window.configure(bg=bg_color)

        # 建立主框架
        main_frame = tk.Frame(self.window, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # === 標題 ===
        title_label = tk.Label(
            main_frame,
            text="📊 裝置使用統計",
            font=("Microsoft JhengHei UI", 18, "bold"),
            bg=bg_color,
            fg=text_color
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = tk.Label(
            main_frame,
            text="查看您的音訊裝置使用情況",
            font=("Microsoft JhengHei UI", 10),
            bg=bg_color,
            fg=text_secondary
        )
        subtitle_label.pack(pady=(0, 25))

        # === 統計內容區 ===
        stats_container = tk.Frame(main_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        stats_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # 取得統計資料
        stats = self.config_manager.get_usage_stats()

        if not stats:
            # 沒有統計資料
            no_data_frame = tk.Frame(stats_container, bg=card_bg)
            no_data_frame.pack(expand=True)

            no_data_icon = tk.Label(
                no_data_frame,
                text="📭",
                font=("Segoe UI Emoji", 48),
                bg=card_bg,
                fg=text_secondary
            )
            no_data_icon.pack(pady=20)

            no_data_label = tk.Label(
                no_data_frame,
                text="目前尚無使用統計資料",
                font=("Microsoft JhengHei UI", 12),
                bg=card_bg,
                fg=text_secondary
            )
            no_data_label.pack()
        else:
            # 有統計資料 - 建立卡片式顯示
            stats_inner = tk.Frame(stats_container, bg=card_bg)
            stats_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # 按使用時間排序
            sorted_stats = sorted(stats.items(), key=lambda x: x[1]['total_seconds'], reverse=True)

            # 計算總使用時間
            total_seconds = sum(data['total_seconds'] for _, data in sorted_stats)

            # 顯示每個裝置的統計卡片
            for idx, (device_id, data) in enumerate(sorted_stats):
                # 建立卡片
                card = tk.Frame(stats_inner, bg=card_light, relief=tk.RAISED, bd=1)
                card.pack(fill=tk.X, pady=8, padx=5)

                card_inner = tk.Frame(card, bg=card_light)
                card_inner.pack(fill=tk.X, padx=15, pady=15)

                # 左側:裝置圖示和名稱
                left_frame = tk.Frame(card_inner, bg=card_light)
                left_frame.pack(side=tk.LEFT, fill=tk.Y)

                # 裝置圖示 (根據排名)
                if idx == 0:
                    icon = "🥇"  # 金牌
                elif idx == 1:
                    icon = "🥈"  # 銀牌
                else:
                    icon = "🎵"  # 音符

                device_icon = tk.Label(
                    left_frame,
                    text=icon,
                    font=("Segoe UI Emoji", 24),
                    bg=card_light
                )
                device_icon.pack(side=tk.LEFT, padx=(0, 15))

                # 裝置名稱
                name_frame = tk.Frame(left_frame, bg=card_light)
                name_frame.pack(side=tk.LEFT)

                device_name = tk.Label(
                    name_frame,
                    text=data['name'],
                    font=("Microsoft JhengHei UI", 12, "bold"),
                    bg=card_light,
                    fg=text_color,
                    anchor=tk.W
                )
                device_name.pack(anchor=tk.W)

                # 右側:統計數據
                right_frame = tk.Frame(card_inner, bg=card_light)
                right_frame.pack(side=tk.RIGHT)

                # 使用時間
                time_str = self._format_time(data['total_seconds'])
                time_label = tk.Label(
                    right_frame,
                    text=f"⏱ {time_str}",
                    font=("Microsoft JhengHei UI", 11),
                    bg=card_light,
                    fg=accent_color
                )
                time_label.pack(anchor=tk.E)

                # 切換次數
                count_label = tk.Label(
                    right_frame,
                    text=f"🔄 切換 {data['switch_count']} 次",
                    font=("Microsoft JhengHei UI", 10),
                    bg=card_light,
                    fg=text_secondary
                )
                count_label.pack(anchor=tk.E, pady=(3, 0))

                # 使用占比
                if total_seconds > 0:
                    percentage = (data['total_seconds'] / total_seconds) * 100
                    percentage_label = tk.Label(
                        right_frame,
                        text=f"📊 占比 {percentage:.1f}%",
                        font=("Microsoft JhengHei UI", 9),
                        bg=card_light,
                        fg=text_secondary
                    )
                    percentage_label.pack(anchor=tk.E, pady=(3, 0))

                # 進度條
                progress_frame = tk.Frame(card_inner, bg=card_light)
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

        # 關閉視窗時的處理
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        self.window.mainloop()

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
