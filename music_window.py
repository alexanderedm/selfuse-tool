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
from music_file_manager import MusicFileManager
from music_history_dialog import MusicHistoryDialog
from music_playlist_dialog import MusicPlaylistDialog
from music_download_dialog import MusicDownloadDialog
from music_metadata_fetcher import MusicMetadataFetcher
from music_library_view import MusicLibraryView
from music_search_view import MusicSearchView
from music_header_view import MusicHeaderView
from music_playback_view import MusicPlaybackView
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
        self.header_view = None  # 頂部標題和按鈕視圖 (MusicHeaderView)
        self.library_view = None  # 音樂庫視圖 (MusicLibraryView)
        self.search_view = None  # 搜尋視圖 (MusicSearchView)
        self.playback_view = None  # 播放控制視圖 (MusicPlaybackView)
        self.category_tree = None  # 使用 Treeview 替換 Listbox (將被 library_view 取代)
        self.song_tree = None  # 使用 Treeview 顯示歌曲列表 (將被 library_view 取代)
        self.current_song_label = None  # 向後相容 (由 playback_view 管理)
        self.artist_label = None  # 向後相容 (由 playback_view 管理)
        self.play_pause_button = None  # 向後相容 (由 playback_view 管理)
        self.play_mode_button = None  # 向後相容 (由 playback_view 管理)
        self.progress_bar = None  # 向後相容 (由 playback_view 管理)
        self.time_label = None  # 向後相容 (由 playback_view 管理)
        self.volume_scale = None  # 向後相容 (由 playback_view 管理)
        self.album_cover_label = None  # 向後相容 (由 playback_view 管理)
        self.search_entry = None  # 搜尋框 (將被 search_view 取代)

        # YouTube 下載器
        self.youtube_downloader = YouTubeDownloader(self.music_manager.music_root_path)

        # 播放歷史管理器
        self.play_history_manager = PlayHistoryManager("play_history.json")

        # 播放列表管理器
        self.playlist_manager = PlaylistManager("playlists.json")

        # 檔案管理器
        self.file_manager = MusicFileManager(self.music_manager.music_root_path)

        # 音樂元數據自動補全
        self.metadata_fetcher = MusicMetadataFetcher(
            self.music_manager,
            self.music_manager.config_manager
        )

        # 歷史對話框(延遲初始化,當 window 建立後)
        self.history_dialog = None

        # 播放列表對話框(延遲初始化,當 window 建立後)
        self.playlist_dialog = None

        # 下載對話框(延遲初始化,當 window 建立後)
        self.download_dialog = None

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

        # 初始化歷史對話框
        self.history_dialog = MusicHistoryDialog(
            parent=self.window,
            play_history_manager=self.play_history_manager,
            music_manager=self.music_manager
        )

        # 初始化播放列表對話框
        self.playlist_dialog = MusicPlaylistDialog(
            parent_window=self.window,
            playlist_manager=self.playlist_manager,
            music_manager=self.music_manager,
            on_play_playlist=self._play_playlist,
            on_play_song=self._play_song_from_playlist
        )

        # 初始化下載對話框
        self.download_dialog = MusicDownloadDialog(
            parent=self.window,
            music_manager=self.music_manager,
            youtube_downloader=self.youtube_downloader,
            on_download_complete=self._on_download_complete
        )

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
        # 使用 MusicHeaderView 顯示頂部標題和按鈕
        self.header_view = MusicHeaderView(
            parent=main_frame,
            on_download_click=self._open_download_dialog,
            on_playlist_click=self._show_playlists,
            on_history_click=self._show_play_history,
            on_most_played_click=self._show_most_played
        )

        # === 主要內容區 ===
        content_frame = tk.Frame(main_frame, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 建立容器用於音樂庫視圖和搜尋框
        library_container = tk.Frame(content_frame, bg=bg_color)
        library_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 使用 MusicSearchView 顯示搜尋框
        self.search_view = MusicSearchView(
            parent=library_container,
            music_manager=self.music_manager,
            on_search_results=self._on_search_results,
            on_search_cleared=self._on_search_cleared
        )

        # 保持向後相容:設定 search_entry 引用
        self.search_entry = self.search_view.search_entry

        # 使用 MusicLibraryView 顯示音樂庫
        self.library_view = MusicLibraryView(
            parent=library_container,
            music_manager=self.music_manager,
            on_category_select=self._on_library_category_select,
            on_song_double_click=self._on_library_song_double_click,
            on_category_rename=self._rename_folder,
            on_category_delete=self._delete_folder
        )

        # 保持向後相容:設定 category_tree 和 song_tree 引用
        self.category_tree = self.library_view.category_tree
        self.song_tree = self.library_view.song_tree

        # 使用 MusicPlaybackView 建立播放控制區
        self.playback_view = MusicPlaybackView(
            parent_frame=content_frame,
            music_manager=self.music_manager,
            on_play_pause=self._toggle_play_pause,
            on_play_previous=self._play_previous,
            on_play_next=self._play_next,
            on_volume_change=self._on_volume_change,
            on_cycle_play_mode=self._cycle_play_mode
        )
        self.playback_view.create_view()

        # 保持向後相容:設定引用
        self.current_song_label = self.playback_view.current_song_label
        self.artist_label = self.playback_view.artist_label
        self.play_pause_button = self.playback_view.play_pause_button
        self.play_mode_button = self.playback_view.play_mode_button
        self.progress_bar = self.playback_view.progress_bar
        self.time_label = self.playback_view.time_label
        self.volume_scale = self.playback_view.volume_scale
        self.album_cover_label = self.playback_view.album_cover_label

        # 設定 pygame mixer 音量
        saved_volume = self.music_manager.config_manager.get_music_volume()
        pygame.mixer.music.set_volume(saved_volume / 100.0)

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

        # 使用 MusicLibraryView 重新載入音樂庫
        if self.library_view:
            self.library_view.reload_library()

    def _load_all_songs(self):
        """載入所有歌曲"""
        songs = self.music_manager.get_all_songs()
        self._display_songs(songs)

    def _on_library_category_select(self, item_type):
        """音樂庫視圖的分類選擇回調

        Args:
            item_type: 項目類型 ('all', 'folder:name', 'song:id')
        """
        # 清除搜尋框
        if self.search_view:
            self.search_view.clear()

        # 這個回調由 MusicLibraryView 內部處理,
        # 我們只需要更新 playlist 引用
        if self.library_view:
            self.playlist = self.library_view.get_current_playlist()

    def _on_library_song_double_click(self, song, playlist, index):
        """音樂庫視圖的歌曲雙擊回調

        Args:
            song: 歌曲資訊
            playlist: 當前播放列表
            index: 歌曲在播放列表中的索引
        """
        self.playlist = playlist
        self.current_index = index
        self._play_song(song)

    def _on_search_results(self, results):
        """搜尋結果回調 - 由 MusicSearchView 觸發

        Args:
            results (list): 搜尋結果歌曲列表
        """
        # 顯示搜尋結果
        if self.library_view:
            self.library_view.display_songs(results)
        else:
            self._display_songs(results)

    def _on_search_cleared(self):
        """搜尋清除回調 - 由 MusicSearchView 觸發"""
        # 重新載入當前分類
        if self.library_view:
            # 讓 MusicLibraryView 重新顯示當前選中的分類
            selected = self.library_view.get_selected_category()
            if selected:
                self._on_library_category_select(selected)
            else:
                self._load_all_songs()

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

            # 使用 playback_view 更新 UI
            if self.playback_view:
                self.playback_view.update_current_song(song)
                self.playback_view.update_play_pause_button(is_paused=False)
                self.playback_view.update_progress(0)

            # 啟動進度更新執行緒
            threading.Thread(target=self._update_progress, daemon=True).start()

            # 背景執行元數據補全
            if self.metadata_fetcher.is_enabled():
                def on_fetch_complete(success, metadata):
                    if success and metadata:
                        # 在主執行緒更新 UI
                        self.window.after(0, lambda: self._on_metadata_updated(song, metadata))

                self.metadata_fetcher.fetch_metadata_async(song, on_fetch_complete)

            logger.info(f"開始播放: {song['title']}")

        except Exception as e:
            logger.error(f"播放失敗: {e}")
            messagebox.showerror("播放錯誤", f"無法播放歌曲:\n{str(e)}")

    def _on_metadata_updated(self, song, metadata):
        """元數據更新完成的回調

        Args:
            song: 原始歌曲資料
            metadata: 新的元數據
        """
        try:
            # 使用 playback_view 更新顯示
            if self.playback_view:
                # 更新歌曲資訊 (包含新的 thumbnail 和 artist)
                updated_song = song.copy()
                if metadata.get("thumbnail"):
                    updated_song["thumbnail"] = metadata["thumbnail"]
                if metadata.get("artist"):
                    updated_song["uploader"] = metadata["artist"]

                self.playback_view.update_current_song(updated_song)

            logger.info("UI 已更新顯示新的元數據")
        except Exception as e:
            logger.error(f"更新 UI 失敗: {e}")

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
                if self.playback_view:
                    self.playback_view.update_play_pause_button(is_paused=False)
            else:
                # 暫停
                pygame.mixer.music.pause()
                self.is_paused = True
                self.pause_position = time.time() - self.start_time  # 記錄暫停位置
                if self.playback_view:
                    self.playback_view.update_play_pause_button(is_paused=True)
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

                if total_duration > 0 and self.playback_view:
                    # 使用 playback_view 更新進度
                    progress = min(100, (current_pos / total_duration) * 100)
                    self.window.after(0, lambda: self.playback_view.update_progress(progress))

                    # 更新時間標籤
                    current_str = self.music_manager.format_duration(int(current_pos))
                    total_str = self.music_manager.format_duration(total_duration)
                    time_text = f"{current_str} / {total_str}"
                    self.window.after(0, lambda t=time_text: self.playback_view.update_time_label(t))

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

        # 使用 playback_view 更新播放模式顯示
        if self.playback_view:
            self.playback_view.update_play_mode(self.play_mode)

        # 如果切換到隨機模式,清空已播放記錄
        if self.play_mode == 'shuffle':
            self.played_indices = []

        mode_names = {
            'sequential': '➡️ 順序播放',
            'repeat_all': '🔂 列表循環',
            'repeat_one': '🔁 單曲循環',
            'shuffle': '🔀 隨機播放'
        }
        logger.info(f"播放模式已切換為: {mode_names[self.play_mode]}")

    def _restore_playback_state(self):
        """恢復播放狀態(重新開啟視窗時)"""
        try:
            # 檢查是否有音樂正在播放
            is_music_playing = pygame.mixer.music.get_busy()

            if is_music_playing and self.current_song and self.playback_view:
                # 音樂正在播放,恢復 UI 狀態
                logger.info(f"恢復播放狀態: {self.current_song['title']}")

                # 使用 playback_view 更新 UI
                self.playback_view.update_current_song(self.current_song)
                self.playback_view.update_play_pause_button(is_paused=self.is_paused)
                self.playback_view.update_play_mode(self.play_mode)

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
        self.download_dialog.show_download_dialog()

    def _on_download_complete(self, success, message, category=None):
        """下載完成回調

        Args:
            success (bool): 是否下載成功
            message (str): 訊息
            category (str): 下載分類
        """
        if success:
            # 重新掃描音樂庫
            self.music_manager.scan_music_library()

            # 重新載入分類和歌曲列表
            self._reload_music_library()

            # 顯示成功訊息
            messagebox.showinfo(
                "✅ 下載完成",
                f"音樂已下載到分類: {category}\n\n{message}"
            )

            logger.info("YouTube 下載成功")
        else:
            # 顯示錯誤訊息
            messagebox.showerror(
                "❌ 下載失敗",
                message
            )

            logger.error(f"YouTube 下載失敗: {message}")

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

        # 使用 MusicFileManager 建立資料夾
        if self.file_manager.create_folder(folder_name):
            # 重新載入音樂庫
            self._reload_music_library()
            messagebox.showinfo("成功", f"資料夾 '{folder_name}' 已建立")
        else:
            if self.file_manager.folder_exists(folder_name):
                messagebox.showerror("錯誤", f"資料夾 '{folder_name}' 已存在")
            else:
                messagebox.showerror("錯誤", "建立資料夾失敗")

    def _rename_folder(self, item_id, old_name):
        """重新命名資料夾"""
        new_name = simpledialog.askstring("重新命名資料夾", "請輸入新的資料夾名稱:", initialvalue=old_name)
        if not new_name or not new_name.strip() or new_name == old_name:
            return

        new_name = new_name.strip()

        # 使用 MusicFileManager 重新命名資料夾
        if self.file_manager.rename_folder(old_name, new_name):
            # 重新載入音樂庫
            self._reload_music_library()
            messagebox.showinfo("成功", f"資料夾已重新命名為 '{new_name}'")
        else:
            if self.file_manager.folder_exists(new_name):
                messagebox.showerror("錯誤", f"資料夾 '{new_name}' 已存在")
            else:
                messagebox.showerror("錯誤", "重新命名資料夾失敗")

    def _delete_folder(self, item_id, folder_name):
        """刪除資料夾"""
        # 確認刪除
        result = messagebox.askyesno(
            "確認刪除",
            f"確定要刪除資料夾 '{folder_name}' 及其所有內容嗎?\n\n此操作無法復原!"
        )

        if not result:
            return

        # 使用 MusicFileManager 刪除資料夾
        if self.file_manager.delete_folder(folder_name):
            # 重新載入音樂庫
            self._reload_music_library()
            messagebox.showinfo("成功", f"資料夾 '{folder_name}' 已刪除")
        else:
            messagebox.showerror("錯誤", "刪除資料夾失敗")

    def _delete_song(self, item_id, song):
        """刪除歌曲"""
        # 確認刪除
        result = messagebox.askyesno(
            "確認刪除",
            f"確定要刪除歌曲 '{song['title']}' 嗎?\n\n此操作無法復原!"
        )

        if not result:
            return

        # 使用 MusicFileManager 刪除歌曲
        if self.file_manager.delete_song(song):
            # 重新載入音樂庫
            self._reload_music_library()
            messagebox.showinfo("成功", f"歌曲 '{song['title']}' 已刪除")
        else:
            messagebox.showerror("錯誤", "刪除歌曲失敗")

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

            # 使用 MusicFileManager 執行移動操作
            if self.file_manager.move_song(song, target_category):
                # 重新載入音樂庫
                self._reload_music_library()
                messagebox.showinfo("成功", f"歌曲已移動到分類: {target_category}")
            else:
                # 取得檔名用於錯誤訊息
                audio_filename = os.path.basename(song['audio_path'])
                target_audio_path = os.path.join(
                    self.music_manager.music_root_path,
                    target_category,
                    audio_filename
                )
                if os.path.exists(target_audio_path):
                    messagebox.showerror("錯誤", f"目標資料夾中已存在同名檔案:\n{audio_filename}")
                else:
                    messagebox.showerror("錯誤", "移動歌曲失敗")

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
        self.history_dialog.show_play_history()

    def _show_most_played(self):
        """顯示最常播放的歌曲對話框"""
        self.history_dialog.show_most_played()

    def _show_playlists(self):
        """顯示播放列表管理對話框"""
        self.playlist_dialog.show_playlists()

    def _add_song_to_playlist(self, song):
        """加入歌曲到播放列表"""
        self.playlist_dialog.add_song_to_playlist(song)

    def _play_song_from_playlist(self, song, playlist_songs, index):
        """從播放列表播放歌曲的回調"""
        self.playlist = playlist_songs
        self.current_index = index
        self._play_song(song)

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
