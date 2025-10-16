"""RSS Feed List View 模組 - 訂閱列表視圖"""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from logger import logger


class RSSFeedListView:
    """RSS 訂閱列表視圖類別"""

    def __init__(self, parent, rss_manager, on_feed_select_callback=None):
        """初始化訂閱列表視圖

        Args:
            parent: 父容器
            rss_manager: RSS 管理器實例
            on_feed_select_callback: 選擇訂閱時的回調函數 (feed_url)
        """
        self.parent = parent
        self.rss_manager = rss_manager
        self.on_feed_select_callback = on_feed_select_callback
        self.feeds_tree = None

        self._create_ui()

    def _create_ui(self):
        """建立訂閱列表 UI"""
        # 深色主題顏色
        card_bg = "#2d2d2d"
        header_bg = "#0d47a1"

        # 左側容器（圓角框架）
        left_container = ctk.CTkFrame(
            self.parent,
            corner_radius=15,
            fg_color=card_bg,
            width=240
        )
        left_container.pack(side="left", fill="both", expand=False, padx=(0, 10))

        # 標題
        feeds_header = ctk.CTkLabel(
            left_container,
            text="📑 訂閱列表",
            font=("Microsoft JhengHei UI", 12, "bold"),
            fg_color=header_bg,
            text_color="white",
            corner_radius=12,
            height=40
        )
        feeds_header.pack(fill="x", padx=5, pady=(5, 0))

        # 訂閱列表 TreeView（包在圓角框架中）
        feeds_frame = ctk.CTkFrame(left_container, fg_color="transparent")
        feeds_frame.pack(fill="both", expand=True, padx=5, pady=5)

        feeds_scrollbar = ttk.Scrollbar(feeds_frame)
        feeds_scrollbar.pack(side="right", fill="y")

        self.feeds_tree = ttk.Treeview(
            feeds_frame,
            columns=('title',),
            show='tree',
            yscrollcommand=feeds_scrollbar.set
        )
        self.feeds_tree.pack(side="left", fill="both", expand=True)
        feeds_scrollbar.config(command=self.feeds_tree.yview)

        # 綁定事件
        self.feeds_tree.bind('<<TreeviewSelect>>', self._on_feed_select)
        self.feeds_tree.bind('<Button-3>', self._on_feed_right_click)

    def load_feeds(self):
        """載入訂閱列表"""
        # 清空列表
        for item in self.feeds_tree.get_children():
            self.feeds_tree.delete(item)

        # 取得所有訂閱
        feeds = self.rss_manager.get_all_feeds()

        if not feeds:
            self.feeds_tree.insert('', 'end', text='📭 尚無訂閱')
            return

        # 加入訂閱列表
        for url, feed_info in feeds.items():
            self.feeds_tree.insert('', 'end', text=f"📰 {feed_info['title']}", values=(url,), tags=(url,))

    def _on_feed_select(self, event):
        """訂閱選擇事件

        Args:
            event: Tkinter event
        """
        selection = self.feeds_tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.feeds_tree.item(item, 'values')

        if not values:
            return

        feed_url = values[0]

        # 呼叫回調函數
        if self.on_feed_select_callback:
            self.on_feed_select_callback(feed_url)

    def _on_feed_right_click(self, event):
        """訂閱右鍵選單

        Args:
            event: Tkinter event
        """
        # 選擇點擊的項目
        item = self.feeds_tree.identify_row(event.y)
        if not item:
            return

        self.feeds_tree.selection_set(item)
        values = self.feeds_tree.item(item, 'values')

        if not values:
            return

        feed_url = values[0]

        # 建立右鍵選單（使用 tkinter Menu）
        menu = tk.Menu(self.parent, tearoff=0)
        menu.add_command(label="🗑 移除此訂閱", command=lambda: self.remove_feed(feed_url))
        menu.add_command(label="🌐 在瀏覽器中開啟", command=lambda: webbrowser.open(feed_url))

        menu.post(event.x_root, event.y_root)

    def remove_feed(self, feed_url):
        """移除訂閱

        Args:
            feed_url (str): RSS feed URL
        """
        if messagebox.askyesno("確認", "確定要移除此訂閱嗎?"):
            self.rss_manager.remove_feed(feed_url)
            self.load_feeds()
            logger.info(f"已移除訂閱: {feed_url}")

    def clear(self):
        """清空訂閱列表"""
        for item in self.feeds_tree.get_children():
            self.feeds_tree.delete(item)
