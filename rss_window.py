"""RSS 閱讀視窗模組"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from logger import logger
from rss_feed_list_view import RSSFeedListView
from rss_filter_manager import RSSFilterManager
from rss_entry_list_view import RSSEntryListView
from rss_preview_view import RSSPreviewView


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
            self.window = tk.Toplevel(self.tk_root)
        else:
            # 如果沒有提供根視窗,建立獨立的視窗
            self.window = tk.Tk()
        self.window.title("📰 RSS 訂閱管理")
        self.window.geometry("1200x700")
        self.window.resizable(True, True)

        # 設定深色主題顏色
        bg_color = "#1e1e1e"  # 深灰背景
        card_bg = "#2d2d2d"  # 卡片背景
        accent_color = "#0078d4"  # 藍色強調
        text_color = "#e0e0e0"  # 淺色文字
        text_secondary = "#a0a0a0"  # 次要文字
        header_bg = "#0d47a1"  # 深藍標題
        self.window.configure(bg=bg_color)

        # 建立主框架
        main_frame = tk.Frame(self.window, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # === 頂部標題列 ===
        title_frame = tk.Frame(main_frame, bg=bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        title_label = tk.Label(
            title_frame,
            text="📰 RSS 訂閱管理",
            font=("Microsoft JhengHei UI", 18, "bold"),
            bg=bg_color,
            fg=text_color
        )
        title_label.pack(side=tk.LEFT)

        # 按鈕框架
        button_frame = tk.Frame(title_frame, bg=bg_color)
        button_frame.pack(side=tk.RIGHT)

        # 自訂深色主題樣式 - 綁定到此視窗
        style = ttk.Style(self.window)
        style.theme_use('clam')  # 使用 clam 主題以便自訂

        # 按鈕樣式
        style.configure("Accent.TButton",
                       font=("Microsoft JhengHei UI", 9),
                       background="#0078d4",
                       foreground="white",
                       borderwidth=0,
                       relief="flat")
        style.map("Accent.TButton",
                 background=[('active', '#005a9e')],
                 relief=[('pressed', 'flat')])

        # TreeView 深色樣式
        style.configure("Treeview",
                       background=card_bg,
                       foreground=text_color,
                       fieldbackground=card_bg,
                       borderwidth=0,
                       rowheight=30,
                       font=("Microsoft JhengHei UI", 9))
        style.configure("Treeview.Heading",
                       background=header_bg,
                       foreground="white",
                       borderwidth=0,
                       relief="flat",
                       font=("Microsoft JhengHei UI", 10, "bold"))
        style.map("Treeview",
                 background=[('selected', accent_color)],
                 foreground=[('selected', 'white')])
        style.map("Treeview.Heading",
                 background=[('active', header_bg)])

        add_button = ttk.Button(
            button_frame,
            text="➕ 新增訂閱",
            command=self._add_feed_manual,
            style="Accent.TButton"
        )
        add_button.pack(side=tk.LEFT, padx=5)

        refresh_button = ttk.Button(
            button_frame,
            text="🔄 重新整理",
            command=self._refresh_feeds,
            style="Accent.TButton"
        )
        refresh_button.pack(side=tk.LEFT, padx=5)

        # === 主要內容區 (三欄式佈局) ===
        content_frame = tk.Frame(main_frame, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)

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
        self.loading_label = tk.Label(
            content_frame,
            text="⏳ 載入中...",
            font=("Microsoft JhengHei UI", 11),
            bg=card_bg,
            fg=text_secondary
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
        self.loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
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
