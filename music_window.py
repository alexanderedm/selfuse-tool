"""音樂播放器視窗模組"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pygame
import threading
import time
import random
import os
import shutil
from logger import logger
from youtube_downloader import YouTubeDownloader
from play_history_manager import PlayHistoryManager
from playlist_manager import PlaylistManager
from PIL import Image, ImageTk, ImageDraw
import requests
from io import BytesIO


class MusicWindow:
    """音樂播放器視窗類別"""

    def __init__(self, music_manager, tk_root=None):
        """初始化音樂播放器視窗

        Args:
            music_manager: 音樂管理器實例
            tk_root: 共用的 Tk 根視窗
        """
        self.music_manager = music_manager
        self.tk_root = tk_root
        self.window = None

        # 播放器狀態
        self.current_song = None
        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.is_paused = False
        # 從設定檔讀取音量
        self.volume = self.music_manager.config_manager.get_music_volume() / 100.0
        # 播放模式: 'sequential' (順序), 'shuffle' (隨機), 'repeat_one' (單曲循環), 'repeat_all' (列表循環)
        self.play_mode = 'sequential'
        self.played_indices = []  # 已播放的歌曲索引(隨機模式用)

        # 時間追蹤
        self.start_time = 0  # 開始播放的時間戳
        self.pause_position = 0  # 暫停時的位置(秒)

        # 專輯封面快取
        self.thumbnail_cache = {}  # {url: PhotoImage}
        self.default_cover_image = None  # 預設封面圖片

        # UI 元件
        self.category_tree = None  # 使用 Treeview 替換 Listbox
        self.song_tree = None  # 使用 Treeview 顯示歌曲列表
        self.current_song_label = None
        self.artist_label = None  # 藝術家標籤
        self.play_pause_button = None
        self.play_mode_button = None  # 播放模式按鈕
        self.progress_bar = None
        self.time_label = None
        self.volume_scale = None
        self.album_cover_label = None  # 專輯封面
        self.search_entry = None  # 搜尋框

        # YouTube 下載器
        self.youtube_downloader = YouTubeDownloader(self.music_manager.music_root_path)

        # 播放歷史管理器
        self.play_history_manager = PlayHistoryManager("play_history.json")

        # 播放列表管理器
        self.playlist_manager = PlaylistManager("playlists.json")

        # 初始化 pygame mixer
        try:
            pygame.mixer.init()
            logger.info("Pygame mixer 初始化成功")
        except Exception as e:
            logger.error(f"Pygame mixer 初始化失敗: {e}")

    def show(self):
        """顯示音樂播放器視窗"""
        logger.info("音樂播放器視窗 show() 方法被呼叫")

        if self.window is not None:
            logger.info("音樂播放器視窗已存在,嘗試顯示")
            try:
                self.window.lift()
                self.window.focus_force()
            except:
                logger.warning("無法顯示現有音樂播放器視窗,將重新建立")
                self.window = None
                self.show()
            return

        logger.info("建立新的音樂播放器視窗")

        # 使用共用的根視窗建立 Toplevel 視窗
        if self.tk_root:
            self.window = tk.Toplevel(self.tk_root)
        else:
            self.window = tk.Tk()

        self.window.title("🎵 本地音樂播放器")
        self.window.geometry("900x600")
        self.window.resizable(True, True)

        # 深色主題顏色
        bg_color = "#1e1e1e"
        card_bg = "#2d2d2d"
        accent_color = "#0078d4"
        text_color = "#e0e0e0"
        text_secondary = "#a0a0a0"
        header_bg = "#0d47a1"
        self.window.configure(bg=bg_color)

        # 建立主框架
        main_frame = tk.Frame(self.window, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # === 頂部標題和功能按鈕 ===
        header_frame = tk.Frame(main_frame, bg=bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        title_label = tk.Label(
            header_frame,
            text="🎵 本地音樂播放器",
            font=("Microsoft JhengHei UI", 18, "bold"),
            bg=bg_color,
            fg=text_color
        )
        title_label.pack(side=tk.LEFT)

        # 右側按鈕區域
        button_frame = tk.Frame(header_frame, bg=bg_color)
        button_frame.pack(side=tk.RIGHT)

        # YouTube 下載按鈕
        download_button = tk.Button(
            button_frame,
            text="📥 下載",
            font=("Microsoft JhengHei UI", 10),
            bg=accent_color,
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self._open_download_dialog
        )
        download_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 最常播放按鈕
        most_played_button = tk.Button(
            button_frame,
            text="🏆 最常播放",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg=text_color,
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self._show_most_played
        )
        most_played_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 播放列表按鈕
        playlist_button = tk.Button(
            button_frame,
            text="📋 播放列表",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg=text_color,
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self._show_playlists
        )
        playlist_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 播放歷史按鈕
        history_button = tk.Button(
            button_frame,
            text="📜 播放歷史",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg=text_color,
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self._show_play_history
        )
        history_button.pack(side=tk.RIGHT, padx=(5, 0))

        # === 主要內容區 ===
        content_frame = tk.Frame(main_frame, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 左側:資料夾樹狀結構
        left_frame = tk.Frame(content_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.config(width=350)  # 增加寬度從 250 到 350

        category_header = tk.Label(
            left_frame,
            text="📁 資料夾",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=header_bg,
            fg="white",
            pady=8
        )
        category_header.pack(fill=tk.X)

        # 建立 Treeview
        tree_frame = tk.Frame(left_frame, bg=card_bg)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        category_scroll = tk.Scrollbar(tree_frame)
        category_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Music.Treeview",
            background=card_bg,
            foreground=text_color,
            fieldbackground=card_bg,
            borderwidth=0,
            rowheight=28,  # 增加行高
            font=("Microsoft JhengHei UI", 10)  # 增加字體大小
        )
        style.configure("Music.Treeview.Heading", background=header_bg, foreground="white")
        style.map('Music.Treeview', background=[('selected', accent_color)])

        self.category_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=category_scroll.set,
            style="Music.Treeview",
            selectmode='browse',
            show='tree'  # 只顯示樹狀結構,不顯示標題
        )
        self.category_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        category_scroll.config(command=self.category_tree.yview)

        # 綁定事件
        self.category_tree.bind('<<TreeviewSelect>>', self._on_category_select)
        self.category_tree.bind('<Button-3>', self._on_category_right_click)  # 右鍵選單
        self.category_tree.bind('<Double-1>', self._on_category_double_click)  # 雙擊展開/收合

        # 中間:歌曲列表
        middle_frame = tk.Frame(content_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        song_header = tk.Label(
            middle_frame,
            text="🎵 歌曲列表",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=header_bg,
            fg="white",
            pady=8
        )
        song_header.pack(fill=tk.X)

        # 搜尋框
        search_frame = tk.Frame(middle_frame, bg=card_bg)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(
            search_frame,
            text="🔍",
            font=("Arial", 12),
            bg=card_bg,
            fg=text_secondary
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.search_entry = tk.Entry(
            search_frame,
            font=("Microsoft JhengHei UI", 10),
            bg="#3d3d3d",
            fg=text_color,
            insertbackground=text_color,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.search_entry.bind('<KeyRelease>', self._on_search_change)

        # 清除搜尋按鈕
        clear_search_button = tk.Button(
            search_frame,
            text="✖",
            font=("Arial", 10),
            bg=card_bg,
            fg=text_secondary,
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=5,
            command=self._clear_search
        )
        clear_search_button.pack(side=tk.LEFT, padx=(5, 0))

        # 建立 Treeview 用於歌曲列表
        song_tree_frame = tk.Frame(middle_frame, bg=card_bg)
        song_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        song_scroll = tk.Scrollbar(song_tree_frame)
        song_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style.configure(
            "Song.Treeview",
            background=card_bg,
            foreground=text_color,
            fieldbackground=card_bg,
            borderwidth=0,
            rowheight=25
        )
        style.configure("Song.Treeview.Heading", background=header_bg, foreground="white", font=("Microsoft JhengHei UI", 10, "bold"))
        style.map('Song.Treeview', background=[('selected', accent_color)])

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

        # 右側:播放控制區
        right_frame = tk.Frame(content_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        right_frame.config(width=250)

        control_header = tk.Label(
            right_frame,
            text="🎧 播放控制",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=header_bg,
            fg="white",
            pady=8
        )
        control_header.pack(fill=tk.X)

        control_content = tk.Frame(right_frame, bg=card_bg)
        control_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 專輯封面(縮圖)
        self.album_cover_label = tk.Label(
            control_content,
            bg=card_bg,
            text="🎵",
            font=("Arial", 48),
            fg=text_secondary
        )
        self.album_cover_label.pack(pady=(0, 10))

        # 當前播放歌曲
        tk.Label(
            control_content,
            text="正在播放:",
            font=("Microsoft JhengHei UI", 9),
            bg=card_bg,
            fg=text_secondary
        ).pack(anchor=tk.W, pady=(0, 5))

        self.current_song_label = tk.Label(
            control_content,
            text="未播放",
            font=("Microsoft JhengHei UI", 10, "bold"),
            bg=card_bg,
            fg=text_color,
            wraplength=220,
            justify=tk.LEFT
        )
        self.current_song_label.pack(anchor=tk.W, pady=(0, 5))

        # 藝術家/上傳者
        self.artist_label = tk.Label(
            control_content,
            text="",
            font=("Microsoft JhengHei UI", 9),
            bg=card_bg,
            fg=text_secondary,
            wraplength=220,
            justify=tk.LEFT
        )
        self.artist_label.pack(anchor=tk.W, pady=(0, 15))

        # 播放進度條
        self.time_label = tk.Label(
            control_content,
            text="00:00 / 00:00",
            font=("Microsoft JhengHei UI", 9),
            bg=card_bg,
            fg=text_secondary
        )
        self.time_label.pack(pady=(0, 5))

        self.progress_bar = ttk.Progressbar(
            control_content,
            orient=tk.HORIZONTAL,
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))

        # 播放控制按鈕
        button_frame = tk.Frame(control_content, bg=card_bg)
        button_frame.pack(pady=(0, 10))

        prev_button = tk.Button(
            button_frame,
            text="⏮",
            font=("Arial", 14),
            bg=accent_color,
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self._play_previous
        )
        prev_button.pack(side=tk.LEFT, padx=5)

        self.play_pause_button = tk.Button(
            button_frame,
            text="▶",
            font=("Arial", 16),
            bg=accent_color,
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=5,
            command=self._toggle_play_pause
        )
        self.play_pause_button.pack(side=tk.LEFT, padx=5)

        next_button = tk.Button(
            button_frame,
            text="⏭",
            font=("Arial", 14),
            bg=accent_color,
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self._play_next
        )
        next_button.pack(side=tk.LEFT, padx=5)

        # 播放模式按鈕
        mode_frame = tk.Frame(control_content, bg=card_bg)
        mode_frame.pack(pady=(0, 15))

        self.play_mode_button = tk.Button(
            mode_frame,
            text="➡️ 順序播放",
            font=("Microsoft JhengHei UI", 9),
            bg="#353535",
            fg=text_color,
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=10,
            pady=5,
            command=self._cycle_play_mode
        )
        self.play_mode_button.pack()

        # 音量控制
        tk.Label(
            control_content,
            text="🔊 音量",
            font=("Microsoft JhengHei UI", 9),
            bg=card_bg,
            fg=text_secondary
        ).pack(anchor=tk.W, pady=(0, 5))

        self.volume_scale = tk.Scale(
            control_content,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self._on_volume_change,
            bg=card_bg,
            fg=text_color,
            highlightthickness=0,
            troughcolor="#353535",
            activebackground=accent_color
        )
        # 從設定檔讀取音量
        saved_volume = self.music_manager.config_manager.get_music_volume()
        self.volume_scale.set(saved_volume)
        # 設定 pygame mixer 音量
        pygame.mixer.music.set_volume(saved_volume / 100.0)
        self.volume_scale.pack(fill=tk.X)

        # 載入音樂庫
        self._load_music_library()

        # 恢復播放狀態(如果音樂正在背景播放)
        self._restore_playback_state()

        # 關閉視窗時的處理
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        logger.info("音樂播放器視窗初始化完成")

    def _load_music_library(self):
        """載入音樂庫"""
        result = self.music_manager.scan_music_library()

        if not result['success']:
            messagebox.showerror("錯誤", result['message'])
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
            folder_node = self.category_tree.insert('', 'end', text=f'📁 {category}', values=(f'folder:{category}',), open=False)

            # 載入該資料夾下的歌曲
            songs = self.music_manager.get_songs_by_category(category)
            if songs:
                for song in songs:
                    duration_str = self.music_manager.format_duration(song['duration'])
                    song_text = f'🎵 {song["title"]} ({duration_str})'
                    # 將歌曲資訊編碼到 values 中
                    song_id = song.get('id', '')
                    self.category_tree.insert(folder_node, 'end', text=song_text, values=(f'song:{song_id}',))
            else:
                # 空資料夾:新增一個提示節點
                self.category_tree.insert(folder_node, 'end', text='   (空資料夾)', values=('empty',), tags=('empty',))

        # 預設選擇所有歌曲
        self.category_tree.selection_set(all_songs_node)
        self._load_all_songs()

    def _load_all_songs(self):
        """載入所有歌曲"""
        songs = self.music_manager.get_all_songs()
        self._display_songs(songs)

    def _on_search_change(self, event):
        """搜尋框內容改變事件"""
        keyword = self.search_entry.get().strip()

        if not keyword:
            # 搜尋框為空,重新載入當前分類
            self._reload_current_category()
            return

        # 搜尋歌曲
        results = self.music_manager.search_songs(keyword)
        self._display_songs(results)

        logger.info(f"搜尋關鍵字: '{keyword}', 找到 {len(results)} 首歌曲")

    def _clear_search(self):
        """清除搜尋"""
        self.search_entry.delete(0, tk.END)
        self._reload_current_category()

    def _reload_current_category(self):
        """重新載入當前選擇的分類"""
        selection = self.category_tree.selection()
        if not selection:
            self._load_all_songs()
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
            # 特定資料夾
            category_name = item_type.replace('folder:', '')
            songs = self.music_manager.get_songs_by_category(category_name)
            self._display_songs(songs)
        elif item_type.startswith('song:'):
            # 選中的是歌曲,載入其所屬資料夾的所有歌曲
            parent_id = self.category_tree.parent(item_id)
            if parent_id:
                parent_values = self.category_tree.item(parent_id, 'values')
                if parent_values and parent_values[0].startswith('folder:'):
                    category_name = parent_values[0].replace('folder:', '')
                    songs = self.music_manager.get_songs_by_category(category_name)
                    self._display_songs(songs)

    def _on_category_select(self, event):
        """分類/資料夾選擇事件"""
        # 清除搜尋框
        if self.search_entry:
            self.search_entry.delete(0, tk.END)

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
            self._display_songs(songs)
        elif item_type.startswith('song:'):
            # 歌曲被選中,播放該歌曲
            song_id = item_type.replace('song:', '')
            song = self.music_manager.get_song_by_id(song_id)
            if song:
                # 先載入所屬資料夾的所有歌曲到播放列表
                parent_id = self.category_tree.parent(item_id)
                if parent_id:
                    parent_values = self.category_tree.item(parent_id, 'values')
                    if parent_values and parent_values[0].startswith('folder:'):
                        category_name = parent_values[0].replace('folder:', '')
                        self.playlist = self.music_manager.get_songs_by_category(category_name)
                        # 找到該歌曲在播放列表中的索引
                        for i, s in enumerate(self.playlist):
                            if s['id'] == song_id:
                                self.current_index = i
                                break
                # 不要在這裡自動播放,只載入到列表

    def _on_category_double_click(self, event):
        """雙擊事件:展開/收合資料夾 或 播放歌曲"""
        selection = self.category_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        item_values = self.category_tree.item(item_id, 'values')

        if not item_values:
            return

        item_type = item_values[0]

        if item_type.startswith('song:'):
            # 雙擊歌曲,播放歌曲
            song_id = item_type.replace('song:', '')
            song = self.music_manager.get_song_by_id(song_id)
            if song:
                # 載入所屬資料夾的所有歌曲到播放列表
                parent_id = self.category_tree.parent(item_id)
                if parent_id:
                    parent_values = self.category_tree.item(parent_id, 'values')
                    if parent_values and parent_values[0].startswith('folder:'):
                        category_name = parent_values[0].replace('folder:', '')
                        self.playlist = self.music_manager.get_songs_by_category(category_name)
                        # 找到該歌曲在播放列表中的索引
                        for i, s in enumerate(self.playlist):
                            if s['id'] == song_id:
                                self.current_index = i
                                break
                # 播放歌曲
                self._play_song(song)

    def _on_category_right_click(self, event):
        """右鍵選單"""
        # 選中右鍵點擊的項目
        item_id = self.category_tree.identify_row(event.y)
        if not item_id:
            # 點擊空白處,顯示新增資料夾選單
            menu = tk.Menu(self.window, tearoff=0, bg="#2d2d2d", fg="#e0e0e0")
            menu.add_command(label="➕ 新增資料夾", command=self._create_new_folder)
            menu.post(event.x_root, event.y_root)
            return

        self.category_tree.selection_set(item_id)
        item_values = self.category_tree.item(item_id, 'values')

        if not item_values:
            return

        item_type = item_values[0]

        menu = tk.Menu(self.window, tearoff=0, bg="#2d2d2d", fg="#e0e0e0")

        if item_type == 'all':
            # 所有歌曲節點:只能新增資料夾
            menu.add_command(label="➕ 新增資料夾", command=self._create_new_folder)
        elif item_type.startswith('folder:'):
            # 資料夾節點
            category_name = item_type.replace('folder:', '')
            menu.add_command(label="✏️ 重新命名", command=lambda: self._rename_folder(item_id, category_name))
            menu.add_command(label="🗑️ 刪除資料夾", command=lambda: self._delete_folder(item_id, category_name))
            menu.add_separator()
            menu.add_command(label="➕ 新增資料夾", command=self._create_new_folder)
        elif item_type.startswith('song:'):
            # 歌曲節點
            song_id = item_type.replace('song:', '')
            song = self.music_manager.get_song_by_id(song_id)
            if song:
                menu.add_command(label="▶️ 播放", command=lambda: self._play_song_from_tree(song))
                menu.add_separator()
                menu.add_command(label="➕ 加入到播放列表", command=lambda: self._add_song_to_playlist(song))
                menu.add_command(label="📁 移動到...", command=lambda: self._move_song_to_category(item_id, song))
                menu.add_separator()
                menu.add_command(label="🗑️ 刪除歌曲", command=lambda: self._delete_song(item_id, song))

        menu.post(event.x_root, event.y_root)

    def _display_songs(self, songs):
        """顯示歌曲列表

        Args:
            songs (list): 歌曲列表
        """
        self.playlist = songs

        # 清空 Treeview
        for item in self.song_tree.get_children():
            self.song_tree.delete(item)

        # 插入歌曲到 Treeview
        for song in songs:
            duration_str = self.music_manager.format_duration(song['duration'])
            self.song_tree.insert('', 'end', values=(song['title'], duration_str))

    def _on_song_double_click(self, event):
        """歌曲雙擊事件"""
        selection = self.song_tree.selection()
        if not selection:
            return

        # 獲取選中的項目索引
        item_id = selection[0]
        item_index = self.song_tree.index(item_id)

        if item_index < len(self.playlist):
            self.current_index = item_index
            self._play_song(self.playlist[item_index])

    def _play_song(self, song):
        """播放歌曲

        Args:
            song (dict): 歌曲資訊
        """
        try:
            pygame.mixer.music.load(song['audio_path'])
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.current_song = song
            self.start_time = time.time()
            self.pause_position = 0

            # 記錄播放歷史
            try:
                song_info = {
                    'title': song.get('title', 'Unknown'),
                    'artist': song.get('uploader', 'Unknown'),
                    'category': song.get('category', 'Unknown')
                }
                self.play_history_manager.record_play(song.get('id', ''), song_info)
            except Exception as e:
                logger.error(f"記錄播放歷史失敗: {e}")

            # 更新 UI
            self.current_song_label.config(text=song['title'])
            # 顯示藝術家
            if self.artist_label and song.get('uploader'):
                self.artist_label.config(text=f"🎤 {song.get('uploader', '未知')}")
            self.play_pause_button.config(text="⏸")

            # 更新專輯封面
            threading.Thread(target=self._update_album_cover, args=(song,), daemon=True).start()

            # 重置進度條
            self.progress_bar['value'] = 0

            # 啟動進度更新執行緒
            threading.Thread(target=self._update_progress, daemon=True).start()

            logger.info(f"開始播放: {song['title']}")

        except Exception as e:
            logger.error(f"播放失敗: {e}")
            messagebox.showerror("播放錯誤", f"無法播放歌曲:\n{str(e)}")

    def _toggle_play_pause(self):
        """切換播放/暫停"""
        if not self.current_song:
            # 如果沒有歌曲,播放第一首
            if self.playlist:
                self.current_index = 0
                self._play_song(self.playlist[0])
            return

        if self.is_playing:
            if self.is_paused:
                # 恢復播放
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.start_time = time.time() - self.pause_position  # 調整開始時間
                self.play_pause_button.config(text="⏸")
            else:
                # 暫停
                pygame.mixer.music.pause()
                self.is_paused = True
                self.pause_position = time.time() - self.start_time  # 記錄暫停位置
                self.play_pause_button.config(text="▶")
        else:
            # 重新播放
            if self.current_song:
                self._play_song(self.current_song)

    def _play_previous(self):
        """播放上一首"""
        if not self.playlist:
            return

        self.current_index = (self.current_index - 1) % len(self.playlist)
        self._play_song(self.playlist[self.current_index])

    def _play_next(self):
        """播放下一首"""
        if not self.playlist:
            return

        if self.play_mode == 'repeat_one':
            # 單曲循環模式 - 重播當前歌曲
            if self.current_index >= 0 and self.current_index < len(self.playlist):
                self._play_song(self.playlist[self.current_index])
        elif self.play_mode == 'shuffle':
            # 隨機模式
            available_indices = [i for i in range(len(self.playlist)) if i not in self.played_indices]

            if not available_indices:
                # 所有歌曲都播放過了,清空記錄重新開始
                self.played_indices = []
                available_indices = list(range(len(self.playlist)))

            self.current_index = random.choice(available_indices)
            self.played_indices.append(self.current_index)
            self._play_song(self.playlist[self.current_index])
        else:
            # 順序模式或列表循環模式
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self._play_song(self.playlist[self.current_index])

    def _on_volume_change(self, value):
        """音量改變事件

        Args:
            value (str): 音量值(0-100)
        """
        volume = float(value) / 100
        pygame.mixer.music.set_volume(volume)
        self.volume = volume
        # 儲存音量設定到設定檔
        self.music_manager.config_manager.set_music_volume(int(float(value)))

    def _update_progress(self):
        """更新播放進度"""
        while self.is_playing and self.current_song:
            try:
                if not pygame.mixer.music.get_busy() and not self.is_paused:
                    # 播放結束,自動播放下一首
                    self.window.after(0, self._play_next)
                    break

                if self.is_paused:
                    time.sleep(0.1)
                    continue

                # 計算當前播放位置
                current_pos = time.time() - self.start_time
                total_duration = self.current_song.get('duration', 0)

                if total_duration > 0:
                    # 更新進度條
                    progress = min(100, (current_pos / total_duration) * 100)
                    self.window.after(0, lambda: self.progress_bar.config(value=progress))

                    # 更新時間標籤
                    current_str = self.music_manager.format_duration(int(current_pos))
                    total_str = self.music_manager.format_duration(total_duration)
                    time_text = f"{current_str} / {total_str}"
                    self.window.after(0, lambda t=time_text: self.time_label.config(text=t))

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"更新進度時發生錯誤: {e}")
                break

    def _cycle_play_mode(self):
        """循環切換播放模式"""
        modes = ['sequential', 'repeat_all', 'repeat_one', 'shuffle']
        current_index = modes.index(self.play_mode)
        next_index = (current_index + 1) % len(modes)
        self.play_mode = modes[next_index]

        # 更新按鈕文字和顏色
        mode_config = {
            'sequential': {'text': '➡️ 順序播放', 'bg': '#353535'},
            'repeat_all': {'text': '🔂 列表循環', 'bg': '#0078d4'},
            'repeat_one': {'text': '🔁 單曲循環', 'bg': '#d43d00'},
            'shuffle': {'text': '🔀 隨機播放', 'bg': '#00b050'}
        }

        config = mode_config[self.play_mode]
        self.play_mode_button.config(text=config['text'], bg=config['bg'])

        # 如果切換到隨機模式,清空已播放記錄
        if self.play_mode == 'shuffle':
            self.played_indices = []

        logger.info(f"播放模式已切換為: {config['text']}")

    def _load_album_cover(self, thumbnail_url):
        """載入專輯封面圖片

        Args:
            thumbnail_url (str): 縮圖 URL

        Returns:
            ImageTk.PhotoImage: 圖片物件,失敗則回傳 None
        """
        if not thumbnail_url:
            return None

        # 檢查快取
        if thumbnail_url in self.thumbnail_cache:
            return self.thumbnail_cache[thumbnail_url]

        try:
            # 下載圖片
            response = requests.get(thumbnail_url, timeout=5)
            response.raise_for_status()

            # 載入圖片
            image_data = BytesIO(response.content)
            image = Image.open(image_data)

            # 保持原始長寬比,調整圖片大小以適應顯示區域
            # 最大寬度和高度設為 250px
            max_size = 250
            original_width, original_height = image.size

            # 計算縮放比例
            ratio = min(max_size / original_width, max_size / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            # 使用高品質重採樣保持長寬比
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 轉換為 PhotoImage
            photo = ImageTk.PhotoImage(image)

            # 快取圖片
            self.thumbnail_cache[thumbnail_url] = photo

            logger.info(f"成功載入專輯封面: {thumbnail_url[:50]}... ({new_width}x{new_height})")
            return photo

        except Exception as e:
            logger.error(f"載入專輯封面失敗: {e}")
            return None

    def _get_default_cover_image(self):
        """取得預設封面圖片

        Returns:
            ImageTk.PhotoImage: 預設封面圖片
        """
        if self.default_cover_image:
            return self.default_cover_image

        try:
            # 建立一個簡單的預設封面 (灰色背景 + 音符圖示)
            image = Image.new('RGB', (200, 200), color='#2d2d2d')
            draw = ImageDraw.Draw(image)

            # 繪製音符 (簡化版)
            # 音符圓圈
            draw.ellipse([70, 110, 110, 150], fill='#0078d4')
            # 音符桿
            draw.rectangle([105, 70, 115, 130], fill='#0078d4')
            # 音符旗
            draw.polygon([115, 70, 115, 80, 135, 90, 135, 80], fill='#0078d4')

            self.default_cover_image = ImageTk.PhotoImage(image)
            return self.default_cover_image

        except Exception as e:
            logger.error(f"建立預設封面失敗: {e}")
            return None

    def _update_album_cover(self, song):
        """更新專輯封面顯示

        Args:
            song (dict): 歌曲資訊
        """
        try:
            thumbnail_url = song.get('thumbnail', '')

            # 先嘗試載入實際封面
            cover_image = self._load_album_cover(thumbnail_url)

            # 如果載入失敗,使用預設封面
            if not cover_image:
                cover_image = self._get_default_cover_image()

            # 更新 UI
            if cover_image and self.album_cover_label:
                self.album_cover_label.config(image=cover_image, text="")
                # 保持引用避免被垃圾回收
                self.album_cover_label.image = cover_image

        except Exception as e:
            logger.error(f"更新專輯封面時發生錯誤: {e}")

    def _restore_playback_state(self):
        """恢復播放狀態(重新開啟視窗時)"""
        try:
            # 檢查是否有音樂正在播放
            is_music_playing = pygame.mixer.music.get_busy()

            if is_music_playing and self.current_song:
                # 音樂正在播放,恢復 UI 狀態
                logger.info(f"恢復播放狀態: {self.current_song['title']}")

                # 更新 UI
                self.current_song_label.config(text=self.current_song['title'])
                if self.artist_label and self.current_song.get('uploader'):
                    self.artist_label.config(text=f"🎤 {self.current_song.get('uploader', '未知')}")

                # 更新專輯封面
                threading.Thread(target=self._update_album_cover, args=(self.current_song,), daemon=True).start()

                # 更新播放按鈕
                if self.is_paused:
                    self.play_pause_button.config(text="▶")
                else:
                    self.play_pause_button.config(text="⏸")

                # 更新播放模式按鈕
                mode_config = {
                    'sequential': {'text': '➡️ 順序播放', 'bg': '#353535'},
                    'repeat_all': {'text': '🔂 列表循環', 'bg': '#0078d4'},
                    'repeat_one': {'text': '🔁 單曲循環', 'bg': '#d43d00'},
                    'shuffle': {'text': '🔀 隨機播放', 'bg': '#00b050'}
                }
                if self.play_mode in mode_config:
                    config = mode_config[self.play_mode]
                    self.play_mode_button.config(text=config['text'], bg=config['bg'])

                # 如果正在播放(非暫停),重新啟動進度更新
                if not self.is_paused:
                    threading.Thread(target=self._update_progress, daemon=True).start()

                logger.info("播放狀態已恢復")
            else:
                logger.info("沒有音樂在背景播放")

        except Exception as e:
            logger.error(f"恢復播放狀態時發生錯誤: {e}")

    def _open_download_dialog(self):
        """開啟 YouTube 下載對話框"""
        # 檢查 yt-dlp 是否安裝
        if not self.youtube_downloader.check_ytdlp_installed():
            messagebox.showerror(
                "錯誤",
                "未安裝 yt-dlp!\n\n請在命令提示字元執行:\npip install yt-dlp"
            )
            return

        # 建立下載對話框
        dialog = tk.Toplevel(self.window)
        dialog.title("📥 下載 YouTube 音樂")
        dialog.geometry("600x400")
        dialog.configure(bg="#1e1e1e")
        dialog.resizable(False, False)

        # 置中顯示
        dialog.transient(self.window)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        tk.Label(
            main_frame,
            text="下載 YouTube 音樂",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(pady=(0, 15))

        # 搜尋/URL 輸入框架
        input_frame = tk.Frame(main_frame, bg="#1e1e1e")
        input_frame.pack(fill=tk.X, pady=(0, 15))

        # URL 輸入
        tk.Label(
            input_frame,
            text="YouTube 連結或搜尋關鍵字:",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(anchor=tk.W)

        url_entry = tk.Entry(
            input_frame,
            font=("Microsoft JhengHei UI", 10),
            bg="#2d2d2d",
            fg="#e0e0e0",
            insertbackground="#e0e0e0",
            relief=tk.FLAT,
            borderwidth=0
        )
        url_entry.pack(fill=tk.X, ipady=8, pady=(5, 0))

        # 分類選擇
        tk.Label(
            main_frame,
            text="下載到分類:",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(anchor=tk.W)

        category_frame = tk.Frame(main_frame, bg="#1e1e1e")
        category_frame.pack(fill=tk.X, pady=(5, 15))

        categories = self.music_manager.get_all_categories()
        if not categories:
            categories = ["下載"]

        category_var = tk.StringVar(value=categories[0] if categories else "下載")

        category_combo = ttk.Combobox(
            category_frame,
            textvariable=category_var,
            values=categories,
            font=("Microsoft JhengHei UI", 10),
            state="readonly"
        )
        category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 或新增分類
        new_category_button = tk.Button(
            category_frame,
            text="+ 新增分類",
            font=("Microsoft JhengHei UI", 9),
            bg="#353535",
            fg="#e0e0e0",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=10,
            pady=5,
            command=lambda: self._add_new_category(category_combo, category_var)
        )
        new_category_button.pack(side=tk.LEFT, padx=(10, 0))

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack(pady=(10, 0))

        download_btn = tk.Button(
            button_frame,
            text="🎵 開始",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=30,
            pady=8,
            command=lambda: self._smart_download_or_search(url_entry.get(), category_var.get(), dialog)
        )
        download_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _smart_download_or_search(self, input_text, category, parent_dialog):
        """智能判斷輸入是 URL 還是搜尋關鍵字"""
        if not input_text or not input_text.strip():
            messagebox.showwarning("警告", "請輸入 YouTube 連結或搜尋關鍵字", parent=parent_dialog)
            return

        input_text = input_text.strip()

        # 判斷是否為 YouTube URL
        import re
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com',
            r'(?:https?://)?(?:www\.)?youtu\.be',
            r'(?:https?://)?music\.youtube\.com'
        ]

        is_url = any(re.search(pattern, input_text, re.IGNORECASE) for pattern in youtube_patterns)

        if is_url:
            # 是 URL,直接下載
            logger.info(f"偵測到 YouTube 連結,直接下載: {input_text}")
            self._start_download(input_text, category, parent_dialog)
        else:
            # 不是 URL,進行搜尋(保存選擇的分類)
            logger.info(f"偵測到搜尋關鍵字,開始搜尋: {input_text}")
            self._search_youtube(input_text, category, parent_dialog)

    def _search_youtube(self, query, category, parent_dialog):
        """搜尋 YouTube 影片

        Args:
            query (str): 搜尋關鍵字
            category (str): 預先選擇的下載分類
            parent_dialog: 父對話框
        """
        if not query or not query.strip():
            messagebox.showwarning("警告", "請輸入搜尋關鍵字", parent=parent_dialog)
            return

        # 顯示搜尋中訊息
        search_msg = messagebox.showinfo(
            "搜尋中",
            "正在搜尋 YouTube 影片,請稍候...",
            parent=parent_dialog
        )

        # 在背景執行緒中搜尋
        def search_thread():
            results = self.youtube_downloader.search_youtube(query, max_results=5)

            if not results:
                self.window.after(0, lambda: messagebox.showerror(
                    "搜尋失敗",
                    "沒有找到相關影片,請嘗試其他關鍵字。",
                    parent=parent_dialog
                ))
                return

            # 顯示搜尋結果選擇對話框,傳遞預選的分類
            self.window.after(0, lambda: self._show_search_results(results, category, parent_dialog))

        threading.Thread(target=search_thread, daemon=True).start()

    def _show_search_results(self, results, category, parent_dialog):
        """顯示搜尋結果對話框

        Args:
            results (list): 搜尋結果列表
            category (str): 預先選擇的下載分類
            parent_dialog: 父對話框
        """
        # 建立結果對話框
        result_dialog = tk.Toplevel(parent_dialog)
        result_dialog.title("🔍 搜尋結果")
        result_dialog.geometry("700x500")
        result_dialog.configure(bg="#1e1e1e")
        result_dialog.resizable(False, False)

        # 置中顯示
        result_dialog.transient(parent_dialog)
        result_dialog.grab_set()

        main_frame = tk.Frame(result_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        tk.Label(
            main_frame,
            text=f"找到 {len(results)} 個結果,請選擇要下載的影片:",
            font=("Microsoft JhengHei UI", 12, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(pady=(0, 10))

        # 顯示將下載到的分類
        tk.Label(
            main_frame,
            text=f"下載分類: {category}",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#a0a0a0"
        ).pack(pady=(0, 15))

        # 結果列表框架
        list_frame = tk.Frame(main_frame, bg="#2d2d2d")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 滾動條
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 結果列表
        result_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg="#2d2d2d",
            fg="#e0e0e0",
            selectbackground="#0078d4",
            selectforeground="white",
            font=("Microsoft JhengHei UI", 10),
            borderwidth=0,
            highlightthickness=0,
            height=15
        )
        result_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=result_listbox.yview)

        # 填充搜尋結果
        for i, video in enumerate(results):
            duration_str = self.music_manager.format_duration(video['duration'])
            display_text = f"{i+1}. {video['title']}\n   👤 {video['uploader']} | ⏱ {duration_str}"
            result_listbox.insert(tk.END, display_text)
            # 添加空行分隔
            if i < len(results) - 1:
                result_listbox.insert(tk.END, "")

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        def on_select():
            selection = result_listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "請選擇一個影片", parent=result_dialog)
                return

            # 因為有空行,需要計算實際的影片索引
            selected_index = selection[0]
            video_index = selected_index // 2  # 每個影片佔2行(內容+空行)

            if video_index < len(results):
                selected_video = results[video_index]

                # 關閉對話框
                result_dialog.destroy()
                parent_dialog.destroy()

                # 直接使用預選的分類開始下載
                self._start_download(selected_video.get('webpage_url', ''), category, None)

        select_btn = tk.Button(
            button_frame,
            text="選擇並下載",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=on_select
        )
        select_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=result_dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _show_category_selection_dialog(self, video_info, categories, search_result_dialog, download_dialog):
        """顯示分類選擇對話框

        Args:
            video_info (dict): 影片資訊
            categories (list): 可用分類列表
            search_result_dialog: 搜尋結果對話框
            download_dialog: 下載對話框
        """
        # 建立分類選擇對話框
        category_dialog = tk.Toplevel(self.window)
        category_dialog.title("選擇下載分類")
        category_dialog.geometry("450x350")
        category_dialog.configure(bg="#1e1e1e")
        category_dialog.resizable(False, False)

        # 置中顯示
        category_dialog.transient(search_result_dialog)
        category_dialog.grab_set()

        main_frame = tk.Frame(category_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        tk.Label(
            main_frame,
            text="選擇下載分類",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(pady=(0, 10))

        # 影片資訊
        video_title = video_info.get('title', '未知影片')
        tk.Label(
            main_frame,
            text=f"影片: {video_title[:50]}{'...' if len(video_title) > 50 else ''}",
            font=("Microsoft JhengHei UI", 9),
            bg="#1e1e1e",
            fg="#a0a0a0",
            wraplength=400,
            justify=tk.LEFT
        ).pack(pady=(0, 20))

        # 分類選擇區域
        tk.Label(
            main_frame,
            text="選擇資料夾:",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(anchor=tk.W, pady=(0, 5))

        # 下拉選單框架
        combo_frame = tk.Frame(main_frame, bg="#1e1e1e")
        combo_frame.pack(fill=tk.X, pady=(0, 15))

        category_var = tk.StringVar(value=categories[0] if categories else "下載")

        # 設定 ttk.Combobox 樣式
        style = ttk.Style()
        style.configure(
            "Category.TCombobox",
            fieldbackground="#2d2d2d",
            background="#2d2d2d",
            foreground="#e0e0e0",
            borderwidth=0
        )

        category_combo = ttk.Combobox(
            combo_frame,
            textvariable=category_var,
            values=categories,
            font=("Microsoft JhengHei UI", 10),
            state="readonly",
            style="Category.TCombobox"
        )
        category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

        # "新增分類" 按鈕
        def create_new_category():
            new_category = simpledialog.askstring(
                "新增分類",
                "請輸入新分類名稱:",
                parent=category_dialog
            )
            if new_category and new_category.strip():
                new_category = new_category.strip()
                # 建立分類資料夾
                category_path = os.path.join(self.music_manager.music_root_path, new_category)
                if os.path.exists(category_path):
                    messagebox.showwarning("警告", f"分類 '{new_category}' 已存在", parent=category_dialog)
                    return

                os.makedirs(category_path, exist_ok=True)
                logger.info(f"建立新分類: {new_category}")

                # 更新下拉選單
                updated_categories = self.music_manager.get_all_categories()
                category_combo['values'] = updated_categories
                category_var.set(new_category)

        new_category_btn = tk.Button(
            combo_frame,
            text="+ 新增",
            font=("Microsoft JhengHei UI", 9),
            bg="#353535",
            fg="#e0e0e0",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=create_new_category
        )
        new_category_btn.pack(side=tk.LEFT, padx=(10, 0))

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack(pady=(20, 0))

        def confirm_download():
            selected_category = category_var.get()
            if not selected_category:
                messagebox.showwarning("警告", "請選擇一個分類", parent=category_dialog)
                return

            # 確保分類資料夾存在
            category_path = os.path.join(self.music_manager.music_root_path, selected_category)
            os.makedirs(category_path, exist_ok=True)

            # 關閉所有對話框
            category_dialog.destroy()
            if search_result_dialog:
                search_result_dialog.destroy()
            if download_dialog:
                download_dialog.destroy()

            # 開始下載
            self._start_download(video_info.get('webpage_url', ''), selected_category, None)

        download_btn = tk.Button(
            button_frame,
            text="確認下載",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=30,
            pady=8,
            command=confirm_download
        )
        download_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=category_dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _start_download_with_url(self, url):
        """使用指定 URL 開始下載流程"""
        # 取得分類列表
        categories = self.music_manager.get_all_categories()
        if not categories:
            categories = ["下載"]

        # 建立假的 video_info
        video_info = {'webpage_url': url, 'title': url}

        # 顯示分類選擇對話框
        self._show_category_selection_dialog(video_info, categories, None, None)

    def _add_new_category(self, combo, var):
        """新增分類"""
        new_category = simpledialog.askstring("新增分類", "請輸入新分類名稱:")
        if new_category and new_category.strip():
            new_category = new_category.strip()
            # 建立分類資料夾
            category_path = os.path.join(self.music_manager.music_root_path, new_category)
            os.makedirs(category_path, exist_ok=True)

            # 更新下拉選單
            categories = self.music_manager.get_all_categories()
            categories.append(new_category)
            combo['values'] = categories
            var.set(new_category)

            logger.info(f"新增分類: {new_category}")

    def _start_download(self, url, category, dialog):
        """開始下載"""
        if not url or not url.strip():
            if dialog:
                messagebox.showwarning("警告", "請輸入 YouTube 連結", parent=dialog)
            else:
                messagebox.showwarning("警告", "請輸入 YouTube 連結")
            return

        # 關閉對話框(如果存在)
        if dialog:
            dialog.destroy()

        # 建立進度對話框
        progress_dialog = tk.Toplevel(self.window)
        progress_dialog.title("📥 下載中")
        progress_dialog.geometry("450x200")
        progress_dialog.configure(bg="#1e1e1e")
        progress_dialog.resizable(False, False)
        progress_dialog.transient(self.window)
        progress_dialog.grab_set()

        # 進度框架
        progress_frame = tk.Frame(progress_dialog, bg="#1e1e1e")
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        tk.Label(
            progress_frame,
            text="正在下載音樂...",
            font=("Microsoft JhengHei UI", 12, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(pady=(0, 15))

        # 狀態標籤
        status_label = tk.Label(
            progress_frame,
            text="準備下載...",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#a0a0a0",
            wraplength=400,
            justify=tk.CENTER
        )
        status_label.pack(pady=(0, 15))

        # 不確定模式的進度條(因為 yt-dlp 不提供詳細進度)
        progress_bar = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            mode='indeterminate',
            length=400
        )
        progress_bar.pack(pady=(0, 15))
        progress_bar.start(10)  # 開始動畫

        # 小提示
        tk.Label(
            progress_frame,
            text="這可能需要幾分鐘時間,請耐心等候...",
            font=("Microsoft JhengHei UI", 8),
            bg="#1e1e1e",
            fg="#606060"
        ).pack()

        # 在背景執行緒中下載
        def download_thread():
            # 更新狀態
            self.window.after(0, lambda: status_label.config(text="正在獲取影片資訊..."))

            result = self.youtube_downloader.download_audio(url, category)

            # 停止進度條動畫
            self.window.after(0, lambda: progress_bar.stop())

            # 關閉進度對話框
            self.window.after(0, lambda: progress_dialog.destroy())

            if result['success']:
                # 重新掃描音樂庫
                self.music_manager.scan_music_library()

                # 重新載入分類和歌曲列表
                self.window.after(0, self._reload_music_library)

                # 顯示成功訊息
                self.window.after(0, lambda: messagebox.showinfo(
                    "✅ 下載完成",
                    f"音樂已下載到分類: {category}\n\n{result['message']}"
                ))

                logger.info(f"YouTube 下載成功: {url}")
            else:
                # 顯示錯誤訊息
                self.window.after(0, lambda: messagebox.showerror(
                    "❌ 下載失敗",
                    result['message']
                ))

                logger.error(f"YouTube 下載失敗: {url}, {result['message']}")

        threading.Thread(target=download_thread, daemon=True).start()

    def _reload_music_library(self):
        """重新載入音樂庫"""
        # 重新掃描
        self.music_manager.scan_music_library()

        # 重新載入樹狀結構
        self._load_music_library()

        logger.info("音樂庫已重新載入")

    def _play_song_from_tree(self, song):
        """從樹狀結構播放歌曲"""
        if song:
            # 載入所屬資料夾的所有歌曲到播放列表
            category = song.get('category', '')
            if category:
                self.playlist = self.music_manager.get_songs_by_category(category)
                # 找到該歌曲在播放列表中的索引
                for i, s in enumerate(self.playlist):
                    if s['id'] == song['id']:
                        self.current_index = i
                        break
            # 播放歌曲
            self._play_song(song)

    def _create_new_folder(self):
        """新增資料夾"""
        folder_name = simpledialog.askstring("新增資料夾", "請輸入資料夾名稱:")
        if not folder_name or not folder_name.strip():
            return

        folder_name = folder_name.strip()

        # 建立資料夾
        folder_path = os.path.join(self.music_manager.music_root_path, folder_name)
        if os.path.exists(folder_path):
            messagebox.showerror("錯誤", f"資料夾 '{folder_name}' 已存在")
            return

        try:
            os.makedirs(folder_path, exist_ok=True)
            logger.info(f"建立新資料夾: {folder_name}")

            # 重新載入音樂庫
            self._reload_music_library()

            messagebox.showinfo("成功", f"資料夾 '{folder_name}' 已建立")
        except Exception as e:
            logger.error(f"建立資料夾失敗: {e}")
            messagebox.showerror("錯誤", f"建立資料夾失敗:\n{str(e)}")

    def _rename_folder(self, item_id, old_name):
        """重新命名資料夾"""
        new_name = simpledialog.askstring("重新命名資料夾", "請輸入新的資料夾名稱:", initialvalue=old_name)
        if not new_name or not new_name.strip() or new_name == old_name:
            return

        new_name = new_name.strip()

        # 重新命名資料夾
        old_path = os.path.join(self.music_manager.music_root_path, old_name)
        new_path = os.path.join(self.music_manager.music_root_path, new_name)

        if os.path.exists(new_path):
            messagebox.showerror("錯誤", f"資料夾 '{new_name}' 已存在")
            return

        try:
            os.rename(old_path, new_path)
            logger.info(f"重新命名資料夾: {old_name} -> {new_name}")

            # 重新載入音樂庫
            self._reload_music_library()

            messagebox.showinfo("成功", f"資料夾已重新命名為 '{new_name}'")
        except Exception as e:
            logger.error(f"重新命名資料夾失敗: {e}")
            messagebox.showerror("錯誤", f"重新命名資料夾失敗:\n{str(e)}")

    def _delete_folder(self, item_id, folder_name):
        """刪除資料夾"""
        # 確認刪除
        result = messagebox.askyesno(
            "確認刪除",
            f"確定要刪除資料夾 '{folder_name}' 及其所有內容嗎?\n\n此操作無法復原!"
        )

        if not result:
            return

        # 刪除資料夾
        folder_path = os.path.join(self.music_manager.music_root_path, folder_name)

        try:
            import shutil
            shutil.rmtree(folder_path)
            logger.info(f"刪除資料夾: {folder_name}")

            # 重新載入音樂庫
            self._reload_music_library()

            messagebox.showinfo("成功", f"資料夾 '{folder_name}' 已刪除")
        except Exception as e:
            logger.error(f"刪除資料夾失敗: {e}")
            messagebox.showerror("錯誤", f"刪除資料夾失敗:\n{str(e)}")

    def _delete_song(self, item_id, song):
        """刪除歌曲"""
        # 確認刪除
        result = messagebox.askyesno(
            "確認刪除",
            f"確定要刪除歌曲 '{song['title']}' 嗎?\n\n此操作無法復原!"
        )

        if not result:
            return

        # 刪除歌曲檔案和 JSON
        try:
            audio_path = song['audio_path']
            json_path = song['json_path']

            if os.path.exists(audio_path):
                os.remove(audio_path)
                logger.info(f"刪除音訊檔案: {audio_path}")

            if os.path.exists(json_path):
                os.remove(json_path)
                logger.info(f"刪除 JSON 檔案: {json_path}")

            # 重新載入音樂庫
            self._reload_music_library()

            messagebox.showinfo("成功", f"歌曲 '{song['title']}' 已刪除")
        except Exception as e:
            logger.error(f"刪除歌曲失敗: {e}")
            messagebox.showerror("錯誤", f"刪除歌曲失敗:\n{str(e)}")

    def _move_song_to_category(self, item_id, song):
        """移動歌曲到不同分類

        Args:
            item_id: 樹狀結構中的項目ID
            song (dict): 歌曲資訊
        """
        # 取得所有分類
        categories = self.music_manager.get_all_categories()
        if not categories:
            messagebox.showwarning("警告", "沒有可用的分類")
            return

        # 取得當前分類
        current_category = song.get('category', '')

        # 從分類列表中移除當前分類
        available_categories = [c for c in categories if c != current_category]

        if not available_categories:
            messagebox.showinfo("提示", "沒有其他分類可以移動到。\n請先建立新的分類資料夾。")
            return

        # 建立分類選擇對話框
        move_dialog = tk.Toplevel(self.window)
        move_dialog.title("移動歌曲")
        move_dialog.geometry("450x300")
        move_dialog.configure(bg="#1e1e1e")
        move_dialog.resizable(False, False)
        move_dialog.transient(self.window)
        move_dialog.grab_set()

        main_frame = tk.Frame(move_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        tk.Label(
            main_frame,
            text="移動歌曲到...",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(pady=(0, 10))

        # 歌曲資訊
        tk.Label(
            main_frame,
            text=f"歌曲: {song['title'][:40]}{'...' if len(song['title']) > 40 else ''}",
            font=("Microsoft JhengHei UI", 9),
            bg="#1e1e1e",
            fg="#a0a0a0",
            wraplength=400,
            justify=tk.LEFT
        ).pack(pady=(0, 5))

        tk.Label(
            main_frame,
            text=f"目前位置: {current_category}",
            font=("Microsoft JhengHei UI", 9),
            bg="#1e1e1e",
            fg="#a0a0a0"
        ).pack(pady=(0, 20))

        # 選擇目標分類
        tk.Label(
            main_frame,
            text="選擇目標資料夾:",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(anchor=tk.W, pady=(0, 5))

        # 下拉選單
        category_var = tk.StringVar(value=available_categories[0])

        style = ttk.Style()
        style.configure(
            "Move.TCombobox",
            fieldbackground="#2d2d2d",
            background="#2d2d2d",
            foreground="#e0e0e0"
        )

        category_combo = ttk.Combobox(
            main_frame,
            textvariable=category_var,
            values=available_categories,
            font=("Microsoft JhengHei UI", 10),
            state="readonly",
            style="Move.TCombobox"
        )
        category_combo.pack(fill=tk.X, ipady=5, pady=(0, 20))

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        def confirm_move():
            target_category = category_var.get()
            if not target_category:
                messagebox.showwarning("警告", "請選擇目標資料夾", parent=move_dialog)
                return

            # 關閉對話框
            move_dialog.destroy()

            # 執行移動操作
            try:
                # 取得檔案路徑
                audio_path = song['audio_path']
                json_path = song['json_path']

                # 取得檔名
                audio_filename = os.path.basename(audio_path)
                json_filename = os.path.basename(json_path)

                # 建立目標路徑
                target_audio_path = os.path.join(
                    self.music_manager.music_root_path,
                    target_category,
                    audio_filename
                )
                target_json_path = os.path.join(
                    self.music_manager.music_root_path,
                    target_category,
                    json_filename
                )

                # 檢查目標檔案是否已存在
                if os.path.exists(target_audio_path):
                    messagebox.showerror("錯誤", f"目標資料夾中已存在同名檔案:\n{audio_filename}")
                    return

                # 移動檔案
                shutil.move(audio_path, target_audio_path)
                logger.info(f"移動音訊檔案: {audio_path} -> {target_audio_path}")

                if os.path.exists(json_path):
                    shutil.move(json_path, target_json_path)
                    logger.info(f"移動 JSON 檔案: {json_path} -> {target_json_path}")

                # 重新載入音樂庫
                self._reload_music_library()

                messagebox.showinfo("成功", f"歌曲已移動到分類: {target_category}")

            except Exception as e:
                logger.error(f"移動歌曲失敗: {e}")
                messagebox.showerror("錯誤", f"移動歌曲失敗:\n{str(e)}")

        move_btn = tk.Button(
            button_frame,
            text="移動",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=30,
            pady=8,
            command=confirm_move
        )
        move_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=move_dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _show_play_history(self):
        """顯示播放歷史對話框"""
        # 建立對話框
        history_dialog = tk.Toplevel(self.window)
        history_dialog.title("📜 播放歷史")
        history_dialog.geometry("700x500")
        history_dialog.configure(bg="#1e1e1e")
        history_dialog.resizable(True, True)
        history_dialog.transient(self.window)

        main_frame = tk.Frame(history_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題和統計資訊
        header_frame = tk.Frame(main_frame, bg="#1e1e1e")
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header_frame,
            text="📜 最近播放",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(side=tk.LEFT)

        total_plays = self.play_history_manager.get_total_plays()
        tk.Label(
            header_frame,
            text=f"總播放次數: {total_plays}",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#a0a0a0"
        ).pack(side=tk.RIGHT)

        # 建立 Treeview 顯示歷史記錄
        tree_frame = tk.Frame(main_frame, bg="#2d2d2d")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style = ttk.Style()
        style.configure(
            "History.Treeview",
            background="#2d2d2d",
            foreground="#e0e0e0",
            fieldbackground="#2d2d2d",
            borderwidth=0,
            rowheight=25
        )
        style.configure("History.Treeview.Heading", background="#0d47a1", foreground="white", font=("Microsoft JhengHei UI", 10, "bold"))
        style.map('History.Treeview', background=[('selected', '#0078d4')])

        history_tree = ttk.Treeview(
            tree_frame,
            columns=('title', 'artist', 'category', 'played_at'),
            show='headings',
            yscrollcommand=scrollbar.set,
            style="History.Treeview",
            selectmode='browse'
        )

        # 設定欄位
        history_tree.heading('title', text='🎵 歌曲名稱', anchor=tk.W)
        history_tree.heading('artist', text='🎤 藝術家', anchor=tk.W)
        history_tree.heading('category', text='📁 分類', anchor=tk.W)
        history_tree.heading('played_at', text='⏰ 播放時間', anchor=tk.W)

        history_tree.column('title', width=250, anchor=tk.W)
        history_tree.column('artist', width=150, anchor=tk.W)
        history_tree.column('category', width=100, anchor=tk.W)
        history_tree.column('played_at', width=150, anchor=tk.W)

        history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=history_tree.yview)

        # 載入歷史記錄
        recent_plays = self.play_history_manager.get_recent_plays(limit=50)
        for record in recent_plays:
            # 格式化播放時間
            from datetime import datetime
            try:
                played_time = datetime.fromisoformat(record['played_at'])
                time_str = played_time.strftime('%Y-%m-%d %H:%M')
            except:
                time_str = record['played_at'][:16]  # 截取前 16 個字符

            history_tree.insert('', 'end', values=(
                record['title'],
                record['artist'],
                record['category'],
                time_str
            ))

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        clear_button = tk.Button(
            button_frame,
            text="🗑️ 清除歷史",
            font=("Microsoft JhengHei UI", 10),
            bg="#d43d00",
            fg="white",
            activebackground="#b03400",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=lambda: self._clear_play_history(history_dialog)
        )
        clear_button.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(
            button_frame,
            text="關閉",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=history_dialog.destroy
        )
        close_button.pack(side=tk.LEFT, padx=5)

        logger.info(f"顯示播放歷史,共 {len(recent_plays)} 筆記錄")

    def _show_most_played(self):
        """顯示最常播放的歌曲對話框"""
        # 建立對話框
        most_played_dialog = tk.Toplevel(self.window)
        most_played_dialog.title("🏆 最常播放")
        most_played_dialog.geometry("700x500")
        most_played_dialog.configure(bg="#1e1e1e")
        most_played_dialog.resizable(True, True)
        most_played_dialog.transient(self.window)

        main_frame = tk.Frame(most_played_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        tk.Label(
            main_frame,
            text="🏆 最常播放排行榜",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(pady=(0, 15))

        # 建立 Treeview 顯示排行榜
        tree_frame = tk.Frame(main_frame, bg="#2d2d2d")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style = ttk.Style()
        style.configure(
            "MostPlayed.Treeview",
            background="#2d2d2d",
            foreground="#e0e0e0",
            fieldbackground="#2d2d2d",
            borderwidth=0,
            rowheight=25
        )
        style.configure("MostPlayed.Treeview.Heading", background="#0d47a1", foreground="white", font=("Microsoft JhengHei UI", 10, "bold"))
        style.map('MostPlayed.Treeview', background=[('selected', '#0078d4')])

        most_played_tree = ttk.Treeview(
            tree_frame,
            columns=('rank', 'title', 'artist', 'category', 'play_count'),
            show='headings',
            yscrollcommand=scrollbar.set,
            style="MostPlayed.Treeview",
            selectmode='browse'
        )

        # 設定欄位
        most_played_tree.heading('rank', text='🥇 排名', anchor=tk.CENTER)
        most_played_tree.heading('title', text='🎵 歌曲名稱', anchor=tk.W)
        most_played_tree.heading('artist', text='🎤 藝術家', anchor=tk.W)
        most_played_tree.heading('category', text='📁 分類', anchor=tk.W)
        most_played_tree.heading('play_count', text='🔢 播放次數', anchor=tk.CENTER)

        most_played_tree.column('rank', width=60, anchor=tk.CENTER)
        most_played_tree.column('title', width=230, anchor=tk.W)
        most_played_tree.column('artist', width=130, anchor=tk.W)
        most_played_tree.column('category', width=100, anchor=tk.W)
        most_played_tree.column('play_count', width=90, anchor=tk.CENTER)

        most_played_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=most_played_tree.yview)

        # 載入最常播放的歌曲
        most_played = self.play_history_manager.get_most_played(limit=50)

        for rank, record in enumerate(most_played, start=1):
            song_id = record['song_id']
            play_count = record['play_count']

            # 從音樂管理器獲取歌曲詳細資訊
            song = self.music_manager.get_song_by_id(song_id)

            if song:
                # 排名表情符號
                rank_emoji = ""
                if rank == 1:
                    rank_emoji = "🥇"
                elif rank == 2:
                    rank_emoji = "🥈"
                elif rank == 3:
                    rank_emoji = "🥉"
                else:
                    rank_emoji = f"{rank}"

                most_played_tree.insert('', 'end', values=(
                    rank_emoji,
                    song.get('title', 'Unknown'),
                    song.get('uploader', 'Unknown'),
                    song.get('category', 'Unknown'),
                    play_count
                ))

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        close_button = tk.Button(
            button_frame,
            text="關閉",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=most_played_dialog.destroy
        )
        close_button.pack()

        logger.info(f"顯示最常播放排行榜,共 {len(most_played)} 首歌曲")

    def _clear_play_history(self, dialog):
        """清除播放歷史"""
        result = messagebox.askyesno(
            "確認清除",
            "確定要清除所有播放歷史記錄嗎?\n\n此操作無法復原!",
            parent=dialog
        )

        if result:
            self.play_history_manager.clear_history()
            messagebox.showinfo("成功", "播放歷史已清除", parent=dialog)
            dialog.destroy()
            logger.info("播放歷史已清除")

    def _show_playlists(self):
        """顯示播放列表管理對話框"""
        # 建立對話框
        playlist_dialog = tk.Toplevel(self.window)
        playlist_dialog.title("📋 播放列表管理")
        playlist_dialog.geometry("700x500")
        playlist_dialog.configure(bg="#1e1e1e")
        playlist_dialog.resizable(True, True)
        playlist_dialog.transient(self.window)

        main_frame = tk.Frame(playlist_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題和操作按鈕區
        header_frame = tk.Frame(main_frame, bg="#1e1e1e")
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header_frame,
            text="📋 我的播放列表",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(side=tk.LEFT)

        # 新增播放列表按鈕
        new_playlist_button = tk.Button(
            header_frame,
            text="➕ 新增播放列表",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=lambda: self._create_playlist(playlist_dialog)
        )
        new_playlist_button.pack(side=tk.RIGHT)

        # 建立 Treeview 顯示播放列表
        tree_frame = tk.Frame(main_frame, bg="#2d2d2d")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style = ttk.Style()
        style.configure(
            "Playlist.Treeview",
            background="#2d2d2d",
            foreground="#e0e0e0",
            fieldbackground="#2d2d2d",
            borderwidth=0,
            rowheight=30
        )
        style.configure("Playlist.Treeview.Heading", background="#0d47a1", foreground="white", font=("Microsoft JhengHei UI", 10, "bold"))
        style.map('Playlist.Treeview', background=[('selected', '#0078d4')])

        playlist_tree = ttk.Treeview(
            tree_frame,
            columns=('name', 'song_count', 'description'),
            show='headings',
            yscrollcommand=scrollbar.set,
            style="Playlist.Treeview",
            selectmode='browse'
        )

        # 設定欄位
        playlist_tree.heading('name', text='📋 播放列表名稱', anchor=tk.W)
        playlist_tree.heading('song_count', text='🎵 歌曲數', anchor=tk.CENTER)
        playlist_tree.heading('description', text='📝 描述', anchor=tk.W)

        playlist_tree.column('name', width=200, anchor=tk.W)
        playlist_tree.column('song_count', width=80, anchor=tk.CENTER)
        playlist_tree.column('description', width=350, anchor=tk.W)

        playlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=playlist_tree.yview)

        # 載入播放列表
        playlists = self.playlist_manager.get_all_playlists()
        for playlist in playlists:
            playlist_tree.insert('', 'end', values=(
                playlist['name'],
                playlist['song_count'],
                playlist['description']
            ))

        # 雙擊事件:查看播放列表詳情
        def on_playlist_double_click(event):
            selection = playlist_tree.selection()
            if not selection:
                return
            item_values = playlist_tree.item(selection[0], 'values')
            playlist_name = item_values[0]
            self._show_playlist_detail(playlist_name)

        playlist_tree.bind('<Double-1>', on_playlist_double_click)

        # 右鍵選單
        def on_playlist_right_click(event):
            item_id = playlist_tree.identify_row(event.y)
            if not item_id:
                return

            playlist_tree.selection_set(item_id)
            item_values = playlist_tree.item(item_id, 'values')
            playlist_name = item_values[0]

            menu = tk.Menu(playlist_dialog, tearoff=0, bg="#2d2d2d", fg="#e0e0e0")
            menu.add_command(label="👁️ 查看", command=lambda: self._show_playlist_detail(playlist_name))
            menu.add_command(label="✏️ 重新命名", command=lambda: self._rename_playlist(playlist_name, playlist_dialog))
            menu.add_command(label="📝 編輯描述", command=lambda: self._edit_playlist_description(playlist_name, playlist_dialog))
            menu.add_separator()
            menu.add_command(label="🗑️ 刪除", command=lambda: self._delete_playlist(playlist_name, playlist_dialog))
            menu.post(event.x_root, event.y_root)

        playlist_tree.bind('<Button-3>', on_playlist_right_click)

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        close_button = tk.Button(
            button_frame,
            text="關閉",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=playlist_dialog.destroy
        )
        close_button.pack()

        logger.info(f"顯示播放列表管理,共 {len(playlists)} 個列表")

    def _create_playlist(self, parent_dialog):
        """建立新播放列表"""
        name = simpledialog.askstring("新增播放列表", "請輸入播放列表名稱:", parent=parent_dialog)
        if not name or not name.strip():
            return

        name = name.strip()

        # 詢問描述(可選)
        description = simpledialog.askstring("播放列表描述", "請輸入描述 (可留空):", parent=parent_dialog)
        if description is None:
            description = ""

        if self.playlist_manager.create_playlist(name, description):
            messagebox.showinfo("成功", f"播放列表 '{name}' 已建立", parent=parent_dialog)
            # 關閉並重新開啟對話框以刷新列表
            parent_dialog.destroy()
            self._show_playlists()
        else:
            messagebox.showerror("錯誤", "建立播放列表失敗,名稱可能已存在", parent=parent_dialog)

    def _delete_playlist(self, playlist_name, parent_dialog):
        """刪除播放列表"""
        result = messagebox.askyesno(
            "確認刪除",
            f"確定要刪除播放列表 '{playlist_name}' 嗎?\n\n此操作無法復原!",
            parent=parent_dialog
        )

        if result:
            if self.playlist_manager.delete_playlist(playlist_name):
                messagebox.showinfo("成功", f"播放列表 '{playlist_name}' 已刪除", parent=parent_dialog)
                # 關閉並重新開啟對話框以刷新列表
                parent_dialog.destroy()
                self._show_playlists()
            else:
                messagebox.showerror("錯誤", "刪除播放列表失敗", parent=parent_dialog)

    def _rename_playlist(self, old_name, parent_dialog):
        """重新命名播放列表"""
        new_name = simpledialog.askstring("重新命名播放列表", "請輸入新名稱:", initialvalue=old_name, parent=parent_dialog)
        if not new_name or not new_name.strip() or new_name == old_name:
            return

        new_name = new_name.strip()

        if self.playlist_manager.rename_playlist(old_name, new_name):
            messagebox.showinfo("成功", f"播放列表已重新命名為 '{new_name}'", parent=parent_dialog)
            # 關閉並重新開啟對話框以刷新列表
            parent_dialog.destroy()
            self._show_playlists()
        else:
            messagebox.showerror("錯誤", "重新命名失敗,名稱可能已存在", parent=parent_dialog)

    def _edit_playlist_description(self, playlist_name, parent_dialog):
        """編輯播放列表描述"""
        playlist = self.playlist_manager.get_playlist(playlist_name)
        if not playlist:
            return

        current_desc = playlist['description']
        new_desc = simpledialog.askstring(
            "編輯描述",
            f"播放列表: {playlist_name}\n\n請輸入新的描述:",
            initialvalue=current_desc,
            parent=parent_dialog
        )

        if new_desc is None:  # 使用者取消
            return

        if self.playlist_manager.update_description(playlist_name, new_desc):
            messagebox.showinfo("成功", "描述已更新", parent=parent_dialog)
            # 關閉並重新開啟對話框以刷新列表
            parent_dialog.destroy()
            self._show_playlists()
        else:
            messagebox.showerror("錯誤", "更新描述失敗", parent=parent_dialog)

    def _add_song_to_playlist(self, song):
        """加入歌曲到播放列表"""
        playlists = self.playlist_manager.get_all_playlists()

        if not playlists:
            result = messagebox.askyesno(
                "沒有播放列表",
                "目前沒有任何播放列表。\n\n是否要建立新的播放列表?"
            )
            if result:
                self._show_playlists()
            return

        # 建立選擇對話框
        select_dialog = tk.Toplevel(self.window)
        select_dialog.title("加入到播放列表")
        select_dialog.geometry("450x350")
        select_dialog.configure(bg="#1e1e1e")
        select_dialog.resizable(False, False)
        select_dialog.transient(self.window)
        select_dialog.grab_set()

        main_frame = tk.Frame(select_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 歌曲資訊
        tk.Label(
            main_frame,
            text=f"歌曲: {song['title'][:40]}{'...' if len(song['title']) > 40 else ''}",
            font=("Microsoft JhengHei UI", 10, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0",
            wraplength=400,
            justify=tk.LEFT
        ).pack(pady=(0, 20))

        # 播放列表選擇
        tk.Label(
            main_frame,
            text="選擇播放列表:",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(anchor=tk.W, pady=(0, 5))

        # 列表框
        listbox_frame = tk.Frame(main_frame, bg="#2d2d2d")
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        playlist_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            bg="#2d2d2d",
            fg="#e0e0e0",
            selectbackground="#0078d4",
            selectforeground="white",
            font=("Microsoft JhengHei UI", 10),
            borderwidth=0,
            highlightthickness=0
        )
        playlist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=playlist_listbox.yview)

        # 填充播放列表
        for playlist in playlists:
            display_text = f"{playlist['name']} ({playlist['song_count']} 首歌)"
            playlist_listbox.insert(tk.END, display_text)

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        def confirm_add():
            selection = playlist_listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "請選擇一個播放列表", parent=select_dialog)
                return

            selected_index = selection[0]
            selected_playlist = playlists[selected_index]
            playlist_name = selected_playlist['name']

            if self.playlist_manager.add_song(playlist_name, song['id']):
                messagebox.showinfo("成功", f"已加入到播放列表 '{playlist_name}'", parent=select_dialog)
                select_dialog.destroy()
            else:
                messagebox.showwarning("提示", "歌曲已在播放列表中", parent=select_dialog)

        add_button = tk.Button(
            button_frame,
            text="加入",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=30,
            pady=8,
            command=confirm_add
        )
        add_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(
            button_frame,
            text="取消",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=select_dialog.destroy
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

    def _show_playlist_detail(self, playlist_name):
        """顯示播放列表詳情"""
        playlist = self.playlist_manager.get_playlist(playlist_name)
        if not playlist:
            messagebox.showerror("錯誤", "播放列表不存在")
            return

        # 建立對話框
        detail_dialog = tk.Toplevel(self.window)
        detail_dialog.title(f"📋 {playlist_name}")
        detail_dialog.geometry("700x500")
        detail_dialog.configure(bg="#1e1e1e")
        detail_dialog.resizable(True, True)
        detail_dialog.transient(self.window)

        main_frame = tk.Frame(detail_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題和資訊
        header_frame = tk.Frame(main_frame, bg="#1e1e1e")
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header_frame,
            text=f"📋 {playlist_name}",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(side=tk.LEFT)

        tk.Label(
            header_frame,
            text=f"{playlist['song_count']} 首歌",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#a0a0a0"
        ).pack(side=tk.RIGHT)

        # 描述
        if playlist['description']:
            tk.Label(
                main_frame,
                text=playlist['description'],
                font=("Microsoft JhengHei UI", 9),
                bg="#1e1e1e",
                fg="#a0a0a0",
                wraplength=650,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=(0, 15))

        # 建立 Treeview 顯示歌曲列表
        tree_frame = tk.Frame(main_frame, bg="#2d2d2d")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        style = ttk.Style()
        style.configure(
            "PlaylistDetail.Treeview",
            background="#2d2d2d",
            foreground="#e0e0e0",
            fieldbackground="#2d2d2d",
            borderwidth=0,
            rowheight=25
        )
        style.configure("PlaylistDetail.Treeview.Heading", background="#0d47a1", foreground="white", font=("Microsoft JhengHei UI", 10, "bold"))
        style.map('PlaylistDetail.Treeview', background=[('selected', '#0078d4')])

        song_tree = ttk.Treeview(
            tree_frame,
            columns=('title', 'artist', 'duration'),
            show='headings',
            yscrollcommand=scrollbar.set,
            style="PlaylistDetail.Treeview",
            selectmode='browse'
        )

        song_tree.heading('title', text='🎵 歌曲名稱', anchor=tk.W)
        song_tree.heading('artist', text='🎤 藝術家', anchor=tk.W)
        song_tree.heading('duration', text='⏱ 時長', anchor=tk.E)

        song_tree.column('title', width=300, anchor=tk.W)
        song_tree.column('artist', width=200, anchor=tk.W)
        song_tree.column('duration', width=80, anchor=tk.E)

        song_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=song_tree.yview)

        # 載入歌曲
        for song_id in playlist['songs']:
            song = self.music_manager.get_song_by_id(song_id)
            if song:
                duration_str = self.music_manager.format_duration(song['duration'])
                song_tree.insert('', 'end', values=(
                    song['title'],
                    song.get('uploader', 'Unknown'),
                    duration_str
                ))

        # 雙擊播放
        def on_song_double_click(event):
            selection = song_tree.selection()
            if not selection:
                return
            item_index = song_tree.index(selection[0])
            if item_index < len(playlist['songs']):
                song_id = playlist['songs'][item_index]
                song = self.music_manager.get_song_by_id(song_id)
                if song:
                    # 設定播放列表為該播放列表的所有歌曲
                    self.playlist = [self.music_manager.get_song_by_id(sid) for sid in playlist['songs'] if self.music_manager.get_song_by_id(sid)]
                    self.current_index = item_index
                    self._play_song(song)

        song_tree.bind('<Double-1>', on_song_double_click)

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        play_all_button = tk.Button(
            button_frame,
            text="▶️ 播放全部",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=lambda: self._play_playlist(playlist_name)
        )
        play_all_button.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(
            button_frame,
            text="關閉",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=detail_dialog.destroy
        )
        close_button.pack(side=tk.LEFT, padx=5)

        logger.info(f"顯示播放列表詳情: {playlist_name}, {playlist['song_count']} 首歌")

    def _play_playlist(self, playlist_name):
        """播放整個播放列表"""
        playlist = self.playlist_manager.get_playlist(playlist_name)
        if not playlist or playlist['song_count'] == 0:
            messagebox.showinfo("提示", "播放列表是空的")
            return

        # 載入所有歌曲
        songs = []
        for song_id in playlist['songs']:
            song = self.music_manager.get_song_by_id(song_id)
            if song:
                songs.append(song)

        if not songs:
            messagebox.showinfo("提示", "播放列表中沒有有效的歌曲")
            return

        # 設定播放列表並播放第一首
        self.playlist = songs
        self.current_index = 0
        self._play_song(songs[0])

        logger.info(f"開始播放播放列表: {playlist_name}, {len(songs)} 首歌")

    def _close_window(self):
        """關閉視窗(不停止播放,音樂在背景繼續)"""
        # 不停止播放,讓音樂在背景繼續
        logger.info("音樂播放器視窗已關閉,音樂繼續在背景播放")

        if self.window:
            self.window.destroy()
            self.window = None

    def cleanup(self):
        """清理資源(在應用程式完全關閉時呼叫)"""
        # 停止音樂
        if self.is_playing:
            pygame.mixer.music.stop()

        logger.info("音樂播放器資源已清理")
