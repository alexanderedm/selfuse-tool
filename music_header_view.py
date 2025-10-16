"""音樂播放器頂部標題和按鈕視圖模組"""
import customtkinter as ctk


class MusicHeaderView:
    """音樂播放器頂部標題和功能按鈕視圖"""

    def __init__(
        self,
        parent,
        on_download_click=None,
        on_playlist_click=None,
        on_history_click=None,
        on_most_played_click=None,
        on_equalizer_click=None
    ):
        """初始化 MusicHeaderView

        Args:
            parent: 父容器
            on_download_click: 下載按鈕點擊回調
            on_playlist_click: 播放列表按鈕點擊回調
            on_history_click: 播放歷史按鈕點擊回調
            on_most_played_click: 最常播放按鈕點擊回調
            on_equalizer_click: 等化器按鈕點擊回調
        """
        self.parent = parent
        self.on_download_click = on_download_click
        self.on_playlist_click = on_playlist_click
        self.on_history_click = on_history_click
        self.on_most_played_click = on_most_played_click
        self.on_equalizer_click = on_equalizer_click

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
        self.equalizer_button = None

        # 建立 UI
        self._create_ui()

    def _create_ui(self):
        """建立 UI 元件"""
        # === 頂部標題和功能按鈕 ===
        self.header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 15))

        # 標題標籤
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🎵 本地音樂播放器",
            font=("Microsoft JhengHei UI", 18, "bold")
        )
        self.title_label.pack(side="left")

        # 右側按鈕區域
        button_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        button_frame.pack(side="right")

        # YouTube 下載按鈕（更大的圓角按鈕）
        self.download_button = ctk.CTkButton(
            button_frame,
            text="📥 下載",
            font=("Microsoft JhengHei UI", 13),
            width=100,
            height=40,
            corner_radius=12,
            fg_color="#0078d4",
            hover_color="#005a9e",
            command=self._on_download_button_click
        )
        self.download_button.pack(side="right", padx=(8, 0))

        # 最常播放按鈕（更大的圓角按鈕）
        self.most_played_button = ctk.CTkButton(
            button_frame,
            text="🏆 最常播放",
            font=("Microsoft JhengHei UI", 13),
            width=120,
            height=40,
            corner_radius=12,
            command=self._on_most_played_button_click
        )
        self.most_played_button.pack(side="right", padx=(8, 0))

        # 播放列表按鈕（更大的圓角按鈕）
        self.playlist_button = ctk.CTkButton(
            button_frame,
            text="📋 播放列表",
            font=("Microsoft JhengHei UI", 13),
            width=120,
            height=40,
            corner_radius=12,
            command=self._on_playlist_button_click
        )
        self.playlist_button.pack(side="right", padx=(8, 0))

        # 播放歷史按鈕（更大的圓角按鈕）
        self.history_button = ctk.CTkButton(
            button_frame,
            text="📜 播放歷史",
            font=("Microsoft JhengHei UI", 13),
            width=120,
            height=40,
            corner_radius=12,
            command=self._on_history_button_click
        )
        self.history_button.pack(side="right", padx=(8, 0))

        # 等化器按鈕（更大的圓角按鈕）
        self.equalizer_button = ctk.CTkButton(
            button_frame,
            text="🎚️ 等化器設定",
            font=("Microsoft JhengHei UI", 13),
            width=140,
            height=40,
            corner_radius=12,
            command=self._on_equalizer_button_click
        )
        self.equalizer_button.pack(side="right", padx=(8, 0))

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

    def _on_equalizer_button_click(self):
        """等化器按鈕點擊處理"""
        if self.on_equalizer_click:
            self.on_equalizer_click()

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
        self.equalizer_button = None
