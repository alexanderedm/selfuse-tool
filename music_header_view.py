"""音樂播放器頂部標題和按鈕視圖模組"""
import tkinter as tk


class MusicHeaderView:
    """音樂播放器頂部標題和功能按鈕視圖"""

    def __init__(
        self,
        parent,
        on_download_click=None,
        on_playlist_click=None,
        on_history_click=None,
        on_most_played_click=None
    ):
        """初始化 MusicHeaderView

        Args:
            parent: 父容器
            on_download_click: 下載按鈕點擊回調
            on_playlist_click: 播放列表按鈕點擊回調
            on_history_click: 播放歷史按鈕點擊回調
            on_most_played_click: 最常播放按鈕點擊回調
        """
        self.parent = parent
        self.on_download_click = on_download_click
        self.on_playlist_click = on_playlist_click
        self.on_history_click = on_history_click
        self.on_most_played_click = on_most_played_click

        # 深色主題顏色
        self.bg_color = "#1e1e1e"
        self.accent_color = "#0078d4"
        self.text_color = "#e0e0e0"

        # UI 元件
        self.header_frame = None
        self.title_label = None
        self.download_button = None
        self.most_played_button = None
        self.playlist_button = None
        self.history_button = None

        # 建立 UI
        self._create_ui()

    def _create_ui(self):
        """建立 UI 元件"""
        # === 頂部標題和功能按鈕 ===
        self.header_frame = tk.Frame(self.parent, bg=self.bg_color)
        self.header_frame.pack(fill=tk.X, pady=(0, 15))

        # 標題標籤
        self.title_label = tk.Label(
            self.header_frame,
            text="🎵 本地音樂播放器",
            font=("Microsoft JhengHei UI", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        self.title_label.pack(side=tk.LEFT)

        # 右側按鈕區域
        button_frame = tk.Frame(self.header_frame, bg=self.bg_color)
        button_frame.pack(side=tk.RIGHT)

        # YouTube 下載按鈕
        self.download_button = tk.Button(
            button_frame,
            text="📥 下載",
            font=("Microsoft JhengHei UI", 10),
            bg=self.accent_color,
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self._on_download_button_click
        )
        self.download_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 最常播放按鈕
        self.most_played_button = tk.Button(
            button_frame,
            text="🏆 最常播放",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg=self.text_color,
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self._on_most_played_button_click
        )
        self.most_played_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 播放列表按鈕
        self.playlist_button = tk.Button(
            button_frame,
            text="📋 播放列表",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg=self.text_color,
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self._on_playlist_button_click
        )
        self.playlist_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 播放歷史按鈕
        self.history_button = tk.Button(
            button_frame,
            text="📜 播放歷史",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg=self.text_color,
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self._on_history_button_click
        )
        self.history_button.pack(side=tk.RIGHT, padx=(5, 0))

    def _on_download_button_click(self):
        """下載按鈕點擊處理"""
        if self.on_download_click:
            self.on_download_click()

    def _on_most_played_button_click(self):
        """最常播放按鈕點擊處理"""
        if self.on_most_played_click:
            self.on_most_played_click()

    def _on_playlist_button_click(self):
        """播放列表按鈕點擊處理"""
        if self.on_playlist_click:
            self.on_playlist_click()

    def _on_history_button_click(self):
        """播放歷史按鈕點擊處理"""
        if self.on_history_click:
            self.on_history_click()

    def destroy(self):
        """清理資源"""
        if self.header_frame:
            self.header_frame.destroy()
            self.header_frame = None
        self.title_label = None
        self.download_button = None
        self.most_played_button = None
        self.playlist_button = None
        self.history_button = None
