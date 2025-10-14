"""RSS Entry List View 模組 - 文章列表視圖"""
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from logger import logger


class RSSEntryListView:
    """RSS 文章列表視圖類別"""

    def __init__(self, parent, rss_manager, filter_manager, on_entry_select_callback=None):
        """初始化文章列表視圖

        Args:
            parent: 父容器
            rss_manager: RSS 管理器實例
            filter_manager: 篩選管理器實例
            on_entry_select_callback: 選擇文章時的回調函數 (entry)
        """
        self.parent = parent
        self.rss_manager = rss_manager
        self.filter_manager = filter_manager
        self.on_entry_select_callback = on_entry_select_callback
        self.entries_tree = None
        self.search_var = None
        self.filter_mode = None
        self.current_entries = []

        self._create_ui()

    def _create_ui(self):
        """建立文章列表 UI"""
        # 深色主題顏色
        card_bg = "#2d2d2d"
        header_bg = "#0d47a1"
        accent_color = "#0078d4"
        text_color = "#e0e0e0"

        # 中間容器
        middle_container = tk.Frame(self.parent, bg=card_bg, relief=tk.RIDGE, bd=1)
        middle_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 標題
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
        self.search_var.trace('w', lambda *args: self.apply_filter())

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
            command=self.clear_search,
            width=3,
            style="Accent.TButton"
        )
        clear_search_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 篩選按鈕列
        filter_frame = tk.Frame(middle_container, bg=card_bg)
        filter_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.filter_mode = tk.StringVar(value='all')

        filter_all_btn = tk.Radiobutton(
            filter_frame,
            text="📋 全部",
            variable=self.filter_mode,
            value='all',
            command=self.apply_filter,
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
            command=self.apply_filter,
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
            command=self.apply_filter,
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

        # 綁定事件
        self.entries_tree.bind('<<TreeviewSelect>>', self._on_entry_select)
        self.entries_tree.bind('<Double-1>', self._on_entry_double_click)
        self.entries_tree.bind('<Button-3>', self._on_entry_right_click)

        # 設定已讀/未讀的視覺樣式
        self.entries_tree.tag_configure('unread', font=("Microsoft JhengHei UI", 9, "bold"))
        self.entries_tree.tag_configure('read', foreground='#888888')

    def display_entries(self, entries):
        """顯示文章列表

        Args:
            entries (list): 文章列表
        """
        # 清空列表
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)

        if not entries:
            self.entries_tree.insert('', 'end', values=('❌', '無法載入文章或沒有內容', ''))
            return

        self.current_entries = entries

        # 加入文章
        for idx, entry in enumerate(entries):
            is_read = self.rss_manager.is_read(entry['id'])
            is_fav = self.rss_manager.is_favorite(entry['id'])

            # 狀態圖示
            status = '⭐' if is_fav else ('●' if not is_read else '')

            # 限制標題長度
            title = entry['title']
            if len(title) > 60:
                title = title[:60] + '...'

            # 根據已讀狀態設定標籤
            item_tags = (str(idx), 'read' if is_read else 'unread')
            self.entries_tree.insert('', 'end', values=(status, title, entry['published']), tags=item_tags)

    def _on_entry_select(self, event):
        """文章選擇事件 - 顯示預覽

        Args:
            event: Tkinter event
        """
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
                self._update_entry_item_status(item, entry)

            # 呼叫回調
            if self.on_entry_select_callback:
                self.on_entry_select_callback(entry)

    def _on_entry_double_click(self, event):
        """文章雙擊事件 - 開啟瀏覽器

        Args:
            event: Tkinter event
        """
        self._open_selected_in_browser()

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

    def _on_entry_right_click(self, event):
        """文章右鍵選單

        Args:
            event: Tkinter event
        """
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
        menu = tk.Menu(self.parent, tearoff=0)

        # 已讀/未讀切換
        if is_read:
            menu.add_command(label="📨 標記為未讀",
                           command=lambda: self.toggle_read_status(item, entry, False))
        else:
            menu.add_command(label="✅ 標記為已讀",
                           command=lambda: self.toggle_read_status(item, entry, True))

        # 收藏切換
        if is_fav:
            menu.add_command(label="💔 取消收藏",
                           command=lambda: self.toggle_favorite(item, entry, False))
        else:
            menu.add_command(label="⭐ 加入收藏",
                           command=lambda: self.toggle_favorite(item, entry, True))

        menu.add_separator()
        menu.add_command(label="🌐 在瀏覽器中開啟",
                        command=lambda: webbrowser.open(entry['link']) if entry.get('link') else None)

        menu.post(event.x_root, event.y_root)

    def toggle_read_status(self, item, entry, mark_as_read):
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

    def toggle_favorite(self, item, entry, add_favorite):
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

    def _update_entry_item_status(self, item, entry):
        """更新文章項目的狀態顯示

        Args:
            item: TreeView 項目
            entry: 文章資料
        """
        is_read = self.rss_manager.is_read(entry['id'])
        is_fav = self.rss_manager.is_favorite(entry['id'])
        status = '⭐' if is_fav else ('●' if not is_read else '')

        current_values = self.entries_tree.item(item, 'values')
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

    def apply_filter(self):
        """套用篩選條件"""
        keyword = self.search_var.get() if self.search_var else ''
        mode = self.filter_mode.get() if self.filter_mode else 'all'

        filtered_entries = self.filter_manager.apply_filters(mode, keyword)
        self.display_entries(filtered_entries)

    def clear_search(self):
        """清除搜尋"""
        if self.search_var:
            self.search_var.set("")

    def clear(self):
        """清空文章列表"""
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)
        self.current_entries = []
