"""RSS 閱讀視窗模組"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import webbrowser
import threading
import html
from logger import logger


class RSSWindow:
    """RSS 閱讀視窗類別"""

    def __init__(self, rss_manager, tk_root=None):
        self.rss_manager = rss_manager
        self.window = None
        self.tk_root = tk_root  # 使用共用的根視窗
        self.current_feed_url = None
        self.feeds_tree = None
        self.entries_tree = None
        self.preview_text = None
        self.loading_label = None
        self.current_entries = []  # 儲存當前的文章列表
        self.all_entries = []  # 儲存所有未過濾的文章
        self.search_var = None  # 搜尋框變數

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

        # 左側:訂閱列表 (20%)
        left_container = tk.Frame(content_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_container.config(width=240)

        feeds_header = tk.Label(
            left_container,
            text="📑 訂閱列表",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=header_bg,
            fg="white",
            pady=8
        )
        feeds_header.pack(fill=tk.X)

        # 訂閱列表 TreeView
        feeds_frame = tk.Frame(left_container, bg=card_bg)
        feeds_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        feeds_scrollbar = ttk.Scrollbar(feeds_frame)
        feeds_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.feeds_tree = ttk.Treeview(
            feeds_frame,
            columns=('title',),
            show='tree',
            yscrollcommand=feeds_scrollbar.set
        )
        self.feeds_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        feeds_scrollbar.config(command=self.feeds_tree.yview)

        self.feeds_tree.bind('<<TreeviewSelect>>', self._on_feed_select)
        self.feeds_tree.bind('<Button-3>', self._on_feed_right_click)

        # 中間:文章列表 (40%)
        middle_container = tk.Frame(content_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        middle_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        entries_header = tk.Label(
            middle_container,
            text="📋 文章列表",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=header_bg,
            fg="white",
            pady=8
        )
        entries_header.pack(fill=tk.X)

        # 搜尋框
        search_frame = tk.Frame(middle_container, bg=card_bg)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        search_label = tk.Label(
            search_frame,
            text="🔍",
            font=("Microsoft JhengHei UI", 12),
            bg=card_bg,
            fg=text_color
        )
        search_label.pack(side=tk.LEFT, padx=(5, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._filter_entries())

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg=text_color,
            insertbackground=text_color,
            relief=tk.FLAT,
            bd=5
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # 清除搜尋按鈕
        clear_search_btn = ttk.Button(
            search_frame,
            text="✕",
            command=self._clear_search,
            width=3,
            style="Accent.TButton"
        )
        clear_search_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 篩選按鈕列
        filter_frame = tk.Frame(middle_container, bg=card_bg)
        filter_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.filter_mode = tk.StringVar(value='all')  # 'all', 'unread', 'favorite'

        filter_all_btn = tk.Radiobutton(
            filter_frame,
            text="📋 全部",
            variable=self.filter_mode,
            value='all',
            command=self._apply_filter,
            bg=card_bg,
            fg=text_color,
            selectcolor=card_bg,
            activebackground=card_bg,
            activeforeground=accent_color,
            font=("Microsoft JhengHei UI", 9)
        )
        filter_all_btn.pack(side=tk.LEFT, padx=5)

        filter_unread_btn = tk.Radiobutton(
            filter_frame,
            text="● 未讀",
            variable=self.filter_mode,
            value='unread',
            command=self._apply_filter,
            bg=card_bg,
            fg=text_color,
            selectcolor=card_bg,
            activebackground=card_bg,
            activeforeground=accent_color,
            font=("Microsoft JhengHei UI", 9)
        )
        filter_unread_btn.pack(side=tk.LEFT, padx=5)

        filter_fav_btn = tk.Radiobutton(
            filter_frame,
            text="⭐ 收藏",
            variable=self.filter_mode,
            value='favorite',
            command=self._apply_filter,
            bg=card_bg,
            fg=text_color,
            selectcolor=card_bg,
            activebackground=card_bg,
            activeforeground=accent_color,
            font=("Microsoft JhengHei UI", 9)
        )
        filter_fav_btn.pack(side=tk.LEFT, padx=5)

        # 文章列表 TreeView
        entries_frame = tk.Frame(middle_container, bg=card_bg)
        entries_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        entries_scrollbar = ttk.Scrollbar(entries_frame)
        entries_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.entries_tree = ttk.Treeview(
            entries_frame,
            columns=('status', 'title', 'published'),
            show='headings',
            yscrollcommand=entries_scrollbar.set
        )
        self.entries_tree.heading('status', text='')
        self.entries_tree.heading('title', text='標題')
        self.entries_tree.heading('published', text='發布時間')
        self.entries_tree.column('status', width=30, anchor='center')
        self.entries_tree.column('title', width=320)
        self.entries_tree.column('published', width=130)
        self.entries_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        entries_scrollbar.config(command=self.entries_tree.yview)

        # 綁定選擇事件來顯示預覽
        self.entries_tree.bind('<<TreeviewSelect>>', self._on_entry_select)
        self.entries_tree.bind('<Double-1>', self._on_entry_double_click)
        self.entries_tree.bind('<Button-3>', self._on_entry_right_click)

        # 右側:內文預覽 (40%)
        right_container = tk.Frame(content_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        right_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        preview_header_frame = tk.Frame(right_container, bg=header_bg)
        preview_header_frame.pack(fill=tk.X)

        preview_header = tk.Label(
            preview_header_frame,
            text="📖 完整內文",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=header_bg,
            fg="white",
            pady=8
        )
        preview_header.pack(side=tk.LEFT, padx=10)

        # 在瀏覽器開啟按鈕
        self.open_browser_button = ttk.Button(
            preview_header_frame,
            text="🌐 在瀏覽器開啟",
            command=self._open_selected_in_browser,
            style="Accent.TButton"
        )
        self.open_browser_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # 內文預覽文字框
        preview_frame = tk.Frame(right_container, bg=card_bg)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.preview_text = scrolledtext.ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            font=("Microsoft JhengHei UI", 10),
            bg="#252525",
            fg=text_color,
            relief=tk.FLAT,
            padx=15,
            pady=15,
            insertbackground=text_color
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.config(state=tk.DISABLED)

        # 設定文字標籤樣式 - 深色主題
        self.preview_text.tag_config("title", font=("Microsoft JhengHei UI", 14, "bold"), foreground="#4fc3f7")
        self.preview_text.tag_config("meta", font=("Microsoft JhengHei UI", 9), foreground=text_secondary)
        self.preview_text.tag_config("content", font=("Microsoft JhengHei UI", 10), foreground=text_color, spacing1=5, spacing3=5)
        self.preview_text.tag_config("link", font=("Microsoft JhengHei UI", 9), foreground="#4fc3f7", underline=True)

        # 載入中標籤(初始隱藏)
        self.loading_label = tk.Label(
            preview_frame,
            text="⏳ 載入中...",
            font=("Microsoft JhengHei UI", 11),
            bg=card_bg,
            fg=text_secondary
        )

        # 關閉視窗時的處理
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        # 載入訂閱列表
        self._load_feeds()

        logger.info("RSS視窗初始化完成")
        # 不需要 mainloop,因為共用主執行緒的事件循環

    def _load_feeds(self):
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
        """訂閱選擇事件"""
        selection = self.feeds_tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.feeds_tree.item(item, 'values')

        if not values:
            return

        feed_url = values[0]
        self.current_feed_url = feed_url

        # 載入文章列表
        self._load_entries(feed_url)

    def _load_entries(self, feed_url):
        """載入文章列表

        Args:
            feed_url (str): RSS feed URL
        """
        # 清空文章列表和預覽
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)

        self._clear_preview()
        self.current_entries = []

        # 顯示載入中
        self.loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.window.update()

        # 在背景執行緒中載入
        def load_thread():
            entries = self.rss_manager.fetch_feed_entries(feed_url)
            self.current_entries = entries

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

        if not entries:
            self.entries_tree.insert('', 'end', values=('❌ 無法載入文章或沒有內容', ''))
            return

        # 儲存所有文章供搜尋使用
        self.all_entries = entries
        self.current_entries = entries

        # 加入文章
        for idx, entry in enumerate(entries):
            # 檢查已讀狀態
            is_read = self.rss_manager.is_read(entry['id'])
            is_fav = self.rss_manager.is_favorite(entry['id'])

            # 狀態圖示
            status = ''
            if is_fav:
                status = '⭐'
            elif not is_read:
                status = '●'

            # 限制標題長度
            title = entry['title']
            if len(title) > 60:
                title = title[:60] + '...'

            # 根據已讀狀態設定標籤
            item_tags = (str(idx), 'read' if is_read else 'unread')
            self.entries_tree.insert('', 'end', values=(status, title, entry['published']), tags=item_tags)

        # 設定已讀/未讀的視覺樣式
        self.entries_tree.tag_configure('unread', font=("Microsoft JhengHei UI", 9, "bold"))
        self.entries_tree.tag_configure('read', foreground='#888888')

    def _apply_filter(self):
        """套用篩選條件 (全部/未讀/收藏)"""
        self._filter_entries()

    def _filter_entries(self):
        """根據搜尋關鍵字和篩選模式過濾文章"""
        if not self.search_var:
            return

        keyword = self.search_var.get().lower().strip()
        filter_mode = self.filter_mode.get() if hasattr(self, 'filter_mode') else 'all'

        # 清空文章列表
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)

        # 根據篩選模式預先過濾
        filtered_by_mode = []
        for entry in self.all_entries:
            if filter_mode == 'unread':
                if not self.rss_manager.is_read(entry['id']):
                    filtered_by_mode.append(entry)
            elif filter_mode == 'favorite':
                if self.rss_manager.is_favorite(entry['id']):
                    filtered_by_mode.append(entry)
            else:  # 'all'
                filtered_by_mode.append(entry)

        if not keyword:
            # 如果搜尋框為空,顯示篩選後的文章
            self.current_entries = filtered_by_mode
            for idx, entry in enumerate(filtered_by_mode):
                is_read = self.rss_manager.is_read(entry['id'])
                is_fav = self.rss_manager.is_favorite(entry['id'])
                status = '⭐' if is_fav else ('●' if not is_read else '')
                title = entry['title']
                if len(title) > 60:
                    title = title[:60] + '...'
                item_tags = (str(idx), 'read' if is_read else 'unread')
                self.entries_tree.insert('', 'end', values=(status, title, entry['published']), tags=item_tags)
            return

        # 過濾文章 - 在已經篩選過的文章中搜尋標題和內容
        filtered_entries = []
        for idx, entry in enumerate(filtered_by_mode):
            title = entry['title'].lower()
            content = entry.get('content', entry.get('summary', '')).lower()

            # 檢查關鍵字是否在標題或內容中
            if keyword in title or keyword in content:
                filtered_entries.append((idx, entry))

        # 更新顯示
        self.current_entries = [entry for _, entry in filtered_entries]

        if not filtered_entries:
            self.entries_tree.insert('', 'end', values=('🔍 找不到符合的文章', ''))
            return

        for original_idx, entry in filtered_entries:
            is_read = self.rss_manager.is_read(entry['id'])
            is_fav = self.rss_manager.is_favorite(entry['id'])
            status = '⭐' if is_fav else ('●' if not is_read else '')
            title = entry['title']
            if len(title) > 60:
                title = title[:60] + '...'
            # 使用原始索引以便正確顯示預覽
            new_idx = [e for _, e in filtered_entries].index(entry)
            item_tags = (str(new_idx), 'read' if is_read else 'unread')
            self.entries_tree.insert('', 'end', values=(status, title, entry['published']), tags=item_tags)

    def _clear_search(self):
        """清除搜尋"""
        if self.search_var:
            self.search_var.set("")

    def _on_entry_select(self, event):
        """文章選擇事件 - 顯示預覽"""
        selection = self.entries_tree.selection()
        if not selection:
            return

        item = selection[0]
        tags = self.entries_tree.item(item, 'tags')

        if not tags or not tags[0].isdigit():
            return

        idx = int(tags[0])
        if idx < len(self.current_entries):
            entry = self.current_entries[idx]
            # 自動標記為已讀
            if not self.rss_manager.is_read(entry['id']):
                self.rss_manager.mark_as_read(entry['id'])
                # 更新顯示
                self._update_entry_item_status(item, entry)
            self._show_preview(entry)

    def _show_preview(self, entry):
        """顯示文章完整內容

        Args:
            entry (dict): 文章資料
        """
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)

        # 標題
        self.preview_text.insert(tk.END, entry['title'] + "\n\n", "title")

        # 發布時間和連結
        meta_text = f"📅 發布時間: {entry['published']}\n🔗 連結: {entry['link']}\n\n"
        self.preview_text.insert(tk.END, meta_text, "meta")

        # 分隔線
        self.preview_text.insert(tk.END, "─" * 80 + "\n\n", "meta")

        # 完整內文
        content = entry.get('content', entry.get('summary', '無內容'))
        if content and content != '無內容':
            # 解碼 HTML 實體
            content = html.unescape(content)
            self.preview_text.insert(tk.END, content, "content")
        else:
            self.preview_text.insert(tk.END, "無法取得完整內容,請點擊「在瀏覽器開啟」查看", "meta")

        self.preview_text.config(state=tk.DISABLED)

    def _clear_preview(self):
        """清空預覽"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "請選擇文章以閱讀完整內容", "meta")
        self.preview_text.config(state=tk.DISABLED)

    def _open_selected_in_browser(self):
        """在瀏覽器中開啟選中的文章"""
        selection = self.entries_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "請先選擇一篇文章")
            return

        item = selection[0]
        tags = self.entries_tree.item(item, 'tags')

        if not tags or not tags[0].isdigit():
            return

        idx = int(tags[0])
        if idx < len(self.current_entries):
            entry = self.current_entries[idx]
            link = entry.get('link', '')
            if link:
                try:
                    webbrowser.open(link)
                except Exception as e:
                    messagebox.showerror("錯誤", f"無法開啟連結: {e}")

    def _on_entry_double_click(self, event):
        """文章雙擊事件 - 開啟瀏覽器"""
        self._open_selected_in_browser()

    def _on_feed_right_click(self, event):
        """訂閱右鍵選單"""
        # 選擇點擊的項目
        item = self.feeds_tree.identify_row(event.y)
        if not item:
            return

        self.feeds_tree.selection_set(item)
        values = self.feeds_tree.item(item, 'values')

        if not values:
            return

        feed_url = values[0]

        # 建立右鍵選單
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="🗑 移除此訂閱", command=lambda: self._remove_feed(feed_url))
        menu.add_command(label="🌐 在瀏覽器中開啟", command=lambda: webbrowser.open(feed_url))

        menu.post(event.x_root, event.y_root)

    def _remove_feed(self, feed_url):
        """移除訂閱

        Args:
            feed_url (str): RSS feed URL
        """
        if messagebox.askyesno("確認", "確定要移除此訂閱嗎?"):
            self.rss_manager.remove_feed(feed_url)
            self._load_feeds()
            # 清空文章列表和預覽
            for item in self.entries_tree.get_children():
                self.entries_tree.delete(item)
            self._clear_preview()

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
            self._load_feeds()
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

    def _update_entry_item_status(self, item, entry):
        """更新文章項目的狀態顯示

        Args:
            item: TreeView 項目
            entry: 文章資料
        """
        is_read = self.rss_manager.is_read(entry['id'])
        is_fav = self.rss_manager.is_favorite(entry['id'])
        status = '⭐' if is_fav else ('●' if not is_read else '')

        # 取得當前值
        current_values = self.entries_tree.item(item, 'values')
        # 更新狀態
        new_values = (status, current_values[1], current_values[2])
        self.entries_tree.item(item, values=new_values)

        # 更新標籤
        current_tags = list(self.entries_tree.item(item, 'tags'))
        if 'read' in current_tags:
            current_tags.remove('read')
        if 'unread' in current_tags:
            current_tags.remove('unread')
        current_tags.append('read' if is_read else 'unread')
        self.entries_tree.item(item, tags=tuple(current_tags))

    def _on_entry_right_click(self, event):
        """文章右鍵選單"""
        # 選擇點擊的項目
        item = self.entries_tree.identify_row(event.y)
        if not item:
            return

        self.entries_tree.selection_set(item)
        tags = self.entries_tree.item(item, 'tags')

        if not tags or not tags[0].isdigit():
            return

        idx = int(tags[0])
        if idx >= len(self.current_entries):
            return

        entry = self.current_entries[idx]
        is_read = self.rss_manager.is_read(entry['id'])
        is_fav = self.rss_manager.is_favorite(entry['id'])

        # 建立右鍵選單
        menu = tk.Menu(self.window, tearoff=0)

        # 已讀/未讀切換
        if is_read:
            menu.add_command(label="📨 標記為未讀",
                           command=lambda: self._toggle_read_status(item, entry, False))
        else:
            menu.add_command(label="✅ 標記為已讀",
                           command=lambda: self._toggle_read_status(item, entry, True))

        # 收藏切換
        if is_fav:
            menu.add_command(label="💔 取消收藏",
                           command=lambda: self._toggle_favorite(item, entry, False))
        else:
            menu.add_command(label="⭐ 加入收藏",
                           command=lambda: self._toggle_favorite(item, entry, True))

        menu.add_separator()
        menu.add_command(label="🌐 在瀏覽器中開啟",
                        command=lambda: webbrowser.open(entry['link']) if entry.get('link') else None)

        menu.post(event.x_root, event.y_root)

    def _toggle_read_status(self, item, entry, mark_as_read):
        """切換已讀狀態

        Args:
            item: TreeView 項目
            entry: 文章資料
            mark_as_read: True=標記已讀, False=標記未讀
        """
        if mark_as_read:
            self.rss_manager.mark_as_read(entry['id'])
        else:
            self.rss_manager.mark_as_unread(entry['id'])
        self._update_entry_item_status(item, entry)

    def _toggle_favorite(self, item, entry, add_favorite):
        """切換收藏狀態

        Args:
            item: TreeView 項目
            entry: 文章資料
            add_favorite: True=加入收藏, False=取消收藏
        """
        if add_favorite:
            self.rss_manager.add_favorite(entry['id'], entry)
        else:
            self.rss_manager.remove_favorite(entry['id'])
        self._update_entry_item_status(item, entry)

    def _close_window(self):
        """關閉視窗"""
        if self.window:
            self.window.destroy()
            self.window = None
        # 不要銷毀共用的根視窗
