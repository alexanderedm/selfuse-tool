"""音樂庫視圖模組 - 資料夾樹和歌曲列表"""
import tkinter as tk
from tkinter import ttk
from logger import logger


class MusicLibraryView:
    """音樂庫視圖類別 - 負責顯示資料夾樹和歌曲列表"""

    def __init__(self, parent, music_manager, on_category_select=None,
                 on_song_select=None, on_song_double_click=None,
                 on_category_rename=None, on_category_delete=None):
        """初始化音樂庫視圖

        Args:
            parent: 父視窗
            music_manager: 音樂管理器實例
            on_category_select: 分類選擇回調函數
            on_song_select: 歌曲選擇回調函數
            on_song_double_click: 歌曲雙擊回調函數
            on_category_rename: 分類重命名回調函數
            on_category_delete: 分類刪除回調函數
        """
        self.parent = parent
        self.music_manager = music_manager
        self.on_category_select = on_category_select
        self.on_song_select = on_song_select
        self.on_song_double_click = on_song_double_click
        self.on_category_rename = on_category_rename
        self.on_category_delete = on_category_delete

        # 當前播放列表
        self.current_playlist = []

        # 顏色主題
        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.accent_color = "#0078d4"
        self.text_color = "#e0e0e0"
        self.text_secondary = "#a0a0a0"
        self.header_bg = "#0d47a1"

        # 建立主框架
        self.main_frame = tk.Frame(parent, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 建立 UI 元件
        self._create_ui()

        # 載入音樂庫
        self._load_music_library()

    def _create_ui(self):
        """建立 UI 元件"""
        # 左側:資料夾樹狀結構
        left_frame = tk.Frame(self.main_frame, bg=self.card_bg, relief=tk.RIDGE, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.config(width=350)

        category_header = tk.Label(
            left_frame,
            text="📁 資料夾",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=self.header_bg,
            fg="white",
            pady=8
        )
        category_header.pack(fill=tk.X)

        # 建立 Treeview
        tree_frame = tk.Frame(left_frame, bg=self.card_bg)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        category_scroll = tk.Scrollbar(tree_frame)
        category_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Music.Treeview",
            background=self.card_bg,
            foreground=self.text_color,
            fieldbackground=self.card_bg,
            borderwidth=0,
            rowheight=28,
            font=("Microsoft JhengHei UI", 10)
        )
        style.configure("Music.Treeview.Heading", background=self.header_bg, foreground="white")
        style.map('Music.Treeview', background=[('selected', self.accent_color)])

        self.category_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=category_scroll.set,
            style="Music.Treeview",
            selectmode='browse',
            show='tree'
        )
        self.category_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        category_scroll.config(command=self.category_tree.yview)

        # 綁定事件
        self.category_tree.bind('<<TreeviewSelect>>', self._on_category_select_internal)
        self.category_tree.bind('<Button-3>', self._on_category_right_click)
        self.category_tree.bind('<Double-1>', self._on_category_double_click_internal)

        # 右側:歌曲列表
        right_frame = tk.Frame(self.main_frame, bg=self.card_bg, relief=tk.RIDGE, bd=1)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        song_header = tk.Label(
            right_frame,
            text="🎵 歌曲列表",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=self.header_bg,
            fg="white",
            pady=8
        )
        song_header.pack(fill=tk.X)

        # 建立 Treeview 用於歌曲列表
        song_tree_frame = tk.Frame(right_frame, bg=self.card_bg)
        song_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        song_scroll = tk.Scrollbar(song_tree_frame)
        song_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style.configure(
            "Song.Treeview",
            background=self.card_bg,
            foreground=self.text_color,
            fieldbackground=self.card_bg,
            borderwidth=0,
            rowheight=25
        )
        style.configure(
            "Song.Treeview.Heading",
            background=self.header_bg,
            foreground="white",
            font=("Microsoft JhengHei UI", 10, "bold")
        )
        style.map('Song.Treeview', background=[('selected', self.accent_color)])

        # 建立 Treeview,包含標題和時長兩個欄位
        self.song_tree = ttk.Treeview(
            song_tree_frame,
            columns=('title', 'duration'),
            show='headings',
            yscrollcommand=song_scroll.set,
            style="Song.Treeview",
            selectmode='browse'
        )

        # 設定欄位標題和寬度
        self.song_tree.heading('title', text='🎵 歌曲名稱', anchor=tk.W)
        self.song_tree.heading('duration', text='⏱ 時長', anchor=tk.E)

        # 設定欄位寬度
        self.song_tree.column('title', width=400, anchor=tk.W)
        self.song_tree.column('duration', width=80, anchor=tk.E)

        self.song_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        song_scroll.config(command=self.song_tree.yview)
        self.song_tree.bind('<Double-1>', self._on_song_double_click)

    def _load_music_library(self):
        """載入音樂庫"""
        result = self.music_manager.scan_music_library()

        if not result['success']:
            logger.error(f"載入音樂庫失敗: {result['message']}")
            return

        # 清空樹狀結構
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)

        # 新增 "所有歌曲" 根節點
        all_songs_node = self.category_tree.insert('', 'end', text='📋 所有歌曲', values=('all',), open=True)

        # 載入分類(資料夾) - 包含空資料夾
        categories = self.music_manager.get_all_categories()
        for category in categories:
            # 新增資料夾節點(即使是空資料夾也顯示)
            folder_node = self.category_tree.insert(
                '', 'end',
                text=f'📁 {category}',
                values=(f'folder:{category}',),
                open=False
            )

            # 載入該資料夾下的歌曲
            songs = self.music_manager.get_songs_by_category(category)
            if songs:
                for song in songs:
                    duration_str = self.music_manager.format_duration(song['duration'])
                    song_text = f'🎵 {song["title"]} ({duration_str})'
                    song_id = song.get('id', '')
                    self.category_tree.insert(
                        folder_node, 'end',
                        text=song_text,
                        values=(f'song:{song_id}',)
                    )
            else:
                # 空資料夾:新增一個提示節點
                self.category_tree.insert(
                    folder_node, 'end',
                    text='   (空資料夾)',
                    values=('empty',),
                    tags=('empty',)
                )

        # 預設選擇所有歌曲
        self.category_tree.selection_set(all_songs_node)
        self._load_all_songs()

    def _load_all_songs(self):
        """載入所有歌曲"""
        songs = self.music_manager.get_all_songs()
        self.display_songs(songs)

    def _on_category_select_internal(self, event):
        """分類/資料夾選擇事件(內部處理)"""
        selection = self.category_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        item_values = self.category_tree.item(item_id, 'values')

        if not item_values:
            return

        item_type = item_values[0]

        if item_type == 'all':
            # 所有歌曲
            self._load_all_songs()
        elif item_type.startswith('folder:'):
            # 資料夾
            category_name = item_type.replace('folder:', '')
            songs = self.music_manager.get_songs_by_category(category_name)
            self.display_songs(songs)
        elif item_type.startswith('song:'):
            # 歌曲被選中
            song_id = item_type.replace('song:', '')
            song = self.music_manager.get_song_by_id(song_id)
            if song:
                # 載入所屬資料夾的所有歌曲到播放列表
                parent_id = self.category_tree.parent(item_id)
                if parent_id:
                    parent_values = self.category_tree.item(parent_id, 'values')
                    if parent_values and parent_values[0].startswith('folder:'):
                        category_name = parent_values[0].replace('folder:', '')
                        self.current_playlist = self.music_manager.get_songs_by_category(category_name)

        # 觸發外部回調
        if self.on_category_select:
            self.on_category_select(item_type)

    def _on_category_double_click_internal(self, event):
        """雙擊事件:展開/收合資料夾 或 觸發歌曲播放"""
        selection = self.category_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        item_values = self.category_tree.item(item_id, 'values')

        if not item_values:
            return

        item_type = item_values[0]

        if item_type.startswith('song:'):
            # 雙擊歌曲,找到索引並觸發回調
            song_id = item_type.replace('song:', '')
            song = self.music_manager.get_song_by_id(song_id)
            if song and self.on_song_double_click:
                # 找到歌曲在當前播放列表中的索引
                index = -1
                for i, s in enumerate(self.current_playlist):
                    if s['id'] == song_id:
                        index = i
                        break
                self.on_song_double_click(song, self.current_playlist, index)

    def _on_category_right_click(self, event):
        """右鍵選單"""
        # 這個方法需要由父視窗實作,因為涉及到對話框和檔案操作
        # 暫時保留為空
        pass

    def _on_song_double_click(self, event):
        """歌曲雙擊事件"""
        selection = self.song_tree.selection()
        if not selection:
            return

        # 獲取選中的項目索引
        item_id = selection[0]
        item_index = self.song_tree.index(item_id)

        if item_index < len(self.current_playlist):
            song = self.current_playlist[item_index]
            if self.on_song_double_click:
                self.on_song_double_click(song, self.current_playlist, item_index)

    def display_songs(self, songs):
        """顯示歌曲列表

        Args:
            songs (list): 歌曲列表
        """
        self.current_playlist = songs

        # 清空 Treeview
        for item in self.song_tree.get_children():
            self.song_tree.delete(item)

        # 插入歌曲到 Treeview
        for song in songs:
            duration_str = self.music_manager.format_duration(song['duration'])
            self.song_tree.insert('', 'end', values=(song['title'], duration_str))

    def reload_library(self):
        """重新載入音樂庫"""
        self._load_music_library()
        logger.info("音樂庫已重新載入")

    def get_selected_category(self):
        """取得選中的分類

        Returns:
            str: 分類類型 ('all', 'folder:name', 'song:id', 或 None)
        """
        selection = self.category_tree.selection()
        if not selection:
            return None

        item_values = self.category_tree.item(selection[0], 'values')
        if not item_values:
            return None

        return item_values[0]

    def get_selected_song_index(self):
        """取得選中的歌曲索引

        Returns:
            int: 歌曲索引,如果沒有選中則回傳 -1
        """
        selection = self.song_tree.selection()
        if not selection:
            return -1

        item_id = selection[0]
        return self.song_tree.index(item_id)

    def get_current_playlist(self):
        """取得當前播放列表

        Returns:
            list: 歌曲列表
        """
        return self.current_playlist

    def clear_song_list(self):
        """清空歌曲列表"""
        for item in self.song_tree.get_children():
            self.song_tree.delete(item)
        self.current_playlist = []

    def destroy(self):
        """銷毀視圖"""
        if self.main_frame:
            self.main_frame.destroy()
