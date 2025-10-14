"""音樂搜尋視圖模組 - 搜尋框和搜尋邏輯"""
import tkinter as tk
from logger import logger


class MusicSearchView:
    """音樂搜尋視圖類別 - 負責搜尋UI和搜尋邏輯"""

    def __init__(self, parent, music_manager, on_search_results=None,
                 on_search_cleared=None):
        """初始化音樂搜尋視圖

        Args:
            parent: 父視窗
            music_manager: 音樂管理器實例
            on_search_results: 搜尋結果回調函數 (接收歌曲列表)
            on_search_cleared: 搜尋清除回調函數
        """
        self.parent = parent
        self.music_manager = music_manager
        self.on_search_results = on_search_results
        self.on_search_cleared = on_search_cleared

        # 顏色主題
        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.accent_color = "#0078d4"
        self.text_color = "#e0e0e0"
        self.text_secondary = "#a0a0a0"
        self.header_bg = "#0d47a1"

        # UI 元件
        self.search_entry = None

        # 建立主框架
        self.main_frame = tk.Frame(parent, bg=self.card_bg, relief=tk.RIDGE, bd=1)
        self.main_frame.pack(fill=tk.X, pady=(0, 10))

        # 建立 UI
        self._create_ui()

    def _create_ui(self):
        """建立搜尋 UI"""
        # 標題列
        tk.Label(
            self.main_frame,
            text="🔍 搜尋音樂",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=self.header_bg,
            fg="white",
            pady=8
        ).pack(fill=tk.X)

        # 搜尋輸入框
        search_input_frame = tk.Frame(self.main_frame, bg=self.card_bg)
        search_input_frame.pack(fill=tk.X, padx=10, pady=10)

        # 搜尋圖示
        tk.Label(
            search_input_frame,
            text="🔍",
            font=("Arial", 12),
            bg=self.card_bg,
            fg=self.text_secondary
        ).pack(side=tk.LEFT, padx=(0, 5))

        # 搜尋輸入框
        self.search_entry = tk.Entry(
            search_input_frame,
            font=("Microsoft JhengHei UI", 10),
            bg="#3d3d3d",
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.search_entry.bind('<KeyRelease>', self._on_search_change)

        # 清除按鈕
        clear_search_button = tk.Button(
            search_input_frame,
            text="✖",
            font=("Arial", 10),
            bg=self.card_bg,
            fg=self.text_secondary,
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=5,
            command=self._clear_search
        )
        clear_search_button.pack(side=tk.LEFT, padx=(5, 0))

    def _on_search_change(self, event):
        """搜尋框內容改變事件"""
        keyword = self.search_entry.get().strip()

        if not keyword:
            # 搜尋框為空,觸發清除回調
            if self.on_search_cleared:
                self.on_search_cleared()
            return

        # 搜尋歌曲
        results = self.music_manager.search_songs(keyword)

        # 觸發搜尋結果回調
        if self.on_search_results:
            self.on_search_results(results)

        logger.info(f"搜尋關鍵字: '{keyword}', 找到 {len(results)} 首歌曲")

    def _clear_search(self):
        """清除搜尋"""
        self.search_entry.delete(0, tk.END)

        # 觸發清除回調
        if self.on_search_cleared:
            self.on_search_cleared()

        logger.info("搜尋已清除")

    def get_search_keyword(self):
        """取得當前搜尋關鍵字

        Returns:
            str: 搜尋關鍵字,如果搜尋框為空則回傳空字串
        """
        if self.search_entry:
            return self.search_entry.get().strip()
        return ""

    def clear(self):
        """清空搜尋框"""
        if self.search_entry:
            self.search_entry.delete(0, tk.END)

    def destroy(self):
        """銷毀視圖"""
        if self.main_frame:
            self.main_frame.destroy()
