"""RSS 閱讀視窗模組"""
import customtkinter as ctk
from tkinter import messagebox, simpledialog
import threading
from src.core.logger import logger
from src.rss.rss_feed_list_view import RSSFeedListView
from src.rss.rss_filter_manager import RSSFilterManager
from src.rss.rss_entry_list_view import RSSEntryListView
from src.rss.rss_preview_view import RSSPreviewView


class RSSWindow:
    """RSS 閱讀視窗類別"""

    def __init__(self, rss_manager, tk_root=None):
        self.rss_manager = rss_manager
        self.window = None
        self.tk_root = tk_root  # 使用共用的根視窗
        self.current_feed_url = None
        self.loading_label = None

        # 子視圖實例
        self.feed_list_view = None
        self.filter_manager = None
        self.entry_list_view = None
        self.preview_view = None

    def show(self):
        """顯示 RSS 視窗"""
        logger.info("RSS視窗 show() 方法被呼叫")

        if self.window is not None:
            logger.info("RSS視窗已存在,嘗試顯示")
            try:
                self.window.lift()
                self.window.focus_force()
            except:
                logger.warning("無法顯示現有RSS視窗,將重新建立")
                self.window = None
                self.show()
            return

        logger.info("建立新的 RSS 視窗")
        # 使用共用的根視窗建立 Toplevel 視窗
        if self.tk_root:
            self.window = ctk.CTkToplevel(self.tk_root)
            self.window.transient(self.tk_root)
        else:
            # 如果沒有提供根視窗,建立獨立的視窗
            self.window = ctk.CTk()

        self.window.title("📰 RSS 訂閱管理")
        self.window.geometry("1200x700")
        self.window.resizable(True, True)

        # 自動置頂並聚焦
        self.window.lift()
        self.window.focus_force()

        # 設定深色主題顏色
        bg_color = "#1e1e1e"  # 深灰背景
        card_bg = "#2d2d2d"  # 卡片背景
        text_color = "#e0e0e0"  # 淺色文字
        text_secondary = "#a0a0a0"  # 次要文字

        # 建立主框架
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # === 頂部標題列 ===
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))

        title_label = ctk.CTkLabel(
            title_frame,
            text="📰 RSS 訂閱管理",
            font=("Microsoft JhengHei UI", 18, "bold"),
            text_color=text_color
        )
        title_label.pack(side="left")

        # 按鈕框架
        button_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        button_frame.pack(side="right")

        add_button = ctk.CTkButton(
            button_frame,
            text="➕ 新增訂閱",
            command=self._add_feed_manual,
            corner_radius=10,
            height=38,
            font=("Microsoft JhengHei UI", 10)
        )
        add_button.pack(side="left", padx=5)

        refresh_button = ctk.CTkButton(
            button_frame,
            text="🔄 重新整理",
            command=self._refresh_feeds,
            corner_radius=10,
            height=38,
            font=("Microsoft JhengHei UI", 10)
        )
        refresh_button.pack(side="left", padx=5)

        # === 主要內容區 (三欄式佈局) ===
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # 初始化篩選管理器
        self.filter_manager = RSSFilterManager(self.rss_manager)

        # 左側:訂閱列表 - 使用 RSSFeedListView 模組
        self.feed_list_view = RSSFeedListView(
            content_frame,
            self.rss_manager,
            on_feed_select_callback=self._on_feed_selected
        )

        # 中間:文章列表 - 使用 RSSEntryListView 模組
        self.entry_list_view = RSSEntryListView(
            content_frame,
            self.rss_manager,
            self.filter_manager,
            on_entry_select_callback=self._on_entry_selected
        )

        # 右側:內文預覽 - 使用 RSSPreviewView 模組
        self.preview_view = RSSPreviewView(content_frame)

        # 載入中標籤(初始隱藏) - 放在預覽區域
        self.loading_label = ctk.CTkLabel(
            content_frame,
            text="⏳ 載入中...",
            font=("Microsoft JhengHei UI", 11),
            text_color=text_secondary
        )

        # 關閉視窗時的處理
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        # 載入訂閱列表
        self.feed_list_view.load_feeds()

        logger.info("RSS視窗初始化完成")
        # 不需要 mainloop,因為共用主執行緒的事件循環

    def _on_feed_selected(self, feed_url):
        """訂閱選擇回調

        Args:
            feed_url (str): 選中的 RSS feed URL
        """
        self.current_feed_url = feed_url
        self._load_entries(feed_url)

    def _load_entries(self, feed_url):
        """載入文章列表

        Args:
            feed_url (str): RSS feed URL
        """
        # 清空文章列表和預覽
        self.entry_list_view.clear()
        self.preview_view.clear_preview()

        # 顯示載入中
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.window.update()

        # 在背景執行緒中載入
        def load_thread():
            entries = self.rss_manager.fetch_feed_entries(feed_url)
            # 在主執行緒中更新 UI
            self.window.after(0, lambda: self._update_entries_ui(entries))

        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()

    def _update_entries_ui(self, entries):
        """更新文章列表 UI

        Args:
            entries (list): 文章列表
        """
        # 隱藏載入中
        self.loading_label.place_forget()

        # 更新篩選管理器的文章列表
        self.filter_manager.set_entries(entries)

        # 顯示文章
        self.entry_list_view.display_entries(entries)

    def _on_entry_selected(self, entry):
        """文章選擇回調

        Args:
            entry (dict): 選中的文章資料
        """
        # 顯示預覽
        self.preview_view.show_preview(entry)

    def _add_feed_manual(self):
        """手動新增訂閱"""
        url = simpledialog.askstring("新增訂閱", "請輸入 RSS feed URL:")

        if not url:
            return

        url = url.strip()

        # 驗證並新增
        result = self.rss_manager.add_feed(url)

        if result['success']:
            messagebox.showinfo("成功", result['message'])
            self.feed_list_view.load_feeds()
        else:
            messagebox.showerror("錯誤", result['message'])

    def _refresh_feeds(self):
        """重新整理"""
        # 清除快取
        self.rss_manager.clear_cache()

        # 如果有選擇的訂閱,重新載入
        if self.current_feed_url:
            self._load_entries(self.current_feed_url)
        else:
            messagebox.showinfo("完成", "已清除快取,請選擇訂閱以重新載入")

    def _close_window(self):
        """關閉視窗"""
        if self.window:
            self.window.destroy()
            self.window = None
        # 不要銷毀共用的根視窗
