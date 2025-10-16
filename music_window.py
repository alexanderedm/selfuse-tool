"""音樂播放器視窗模組"""
import customtkinter as ctk
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
from music_song_actions import MusicSongActions
from music_lyrics_view import MusicLyricsView
from lyrics_parser import LyricsParser
from music_equalizer import MusicEqualizer
from music_equalizer_dialog import MusicEqualizerDialog
from ui_theme import UITheme
from discord_presence import DiscordPresence
from PIL import Image, ImageTk, ImageDraw
import requests
from io import BytesIO
from pathlib import Path


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
        self.lyrics_view = None  # 歌詞顯示視圖 (MusicLyricsView)
        self.song_actions = None  # 歌曲操作模組 (MusicSongActions)
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

        # 歌詞解析器
        self.lyrics_parser = LyricsParser()

        # UI 主題
        self.theme = UITheme(theme_name='dark')

        # 等化器
        self.equalizer = MusicEqualizer(self.music_manager.config_manager)

        # 等化器對話框(延遲初始化,當 window 建立後)
        self.equalizer_dialog = None

        # 歷史對話框(延遲初始化,當 window 建立後)
        self.history_dialog = None

        # 播放列表對話框(延遲初始化,當 window 建立後)
        self.playlist_dialog = None

        # 下載對話框(延遲初始化,當 window 建立後)
        self.download_dialog = None

        # Discord Rich Presence
        self.discord_presence = DiscordPresence()
        if self.discord_presence.client_id and self.music_manager.config_manager.get('discord_rpc_enabled', default=True):
            self.discord_presence.connect()
            logger.info("Discord Rich Presence 已啟用")

        # 嘗試使用 AudioPlayer，失敗則 fallback 到 pygame
        self.use_audio_player = False
        self.audio_player = None
        self.audio_processor = None

        try:
            from audio_player import AudioPlayer
            from audio_processor import AudioProcessor
            from equalizer_filter import EqualizerFilter

            # 建立等化器濾波器 (從 MusicEqualizer 讀取設定)
            equalizer_filter = EqualizerFilter(sample_rate=44100)

            # 從 MusicEqualizer 載入當前設定
            preset_name = self.equalizer.get_current_preset()
            gains = self.equalizer.get_gains()
            if gains and len(gains) == len(equalizer_filter.frequencies):
                equalizer_filter.set_all_gains(gains)

            # 建立音訊處理器
            self.audio_processor = AudioProcessor(sample_rate=44100)
            self.audio_processor.equalizer = equalizer_filter

            # 建立音訊播放器
            self.audio_player = AudioPlayer(audio_processor=self.audio_processor)
            self.audio_player.on_playback_end = self._on_audio_player_end

            # 設定音量
            self.audio_player.set_volume(self.volume)

            self.use_audio_player = True
            logger.info("✅ 使用 AudioPlayer（支援即時等化器）")

        except Exception as e:
            logger.warning(f"AudioPlayer 初始化失敗，使用 pygame.mixer: {e}")
            self.use_audio_player = False

        # 初始化 pygame mixer (作為 fallback)
        if not self.use_audio_player:
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

        # 設定 CustomTkinter 主題
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 使用共用的根視窗建立 Toplevel 視窗
        if self.tk_root:
            self.window = ctk.CTkToplevel(self.tk_root)
        else:
            self.window = ctk.CTk()

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

        # 初始化等化器對話框
        self.equalizer_dialog = MusicEqualizerDialog(
            parent=self.window,
            equalizer=self.equalizer,
            on_equalizer_change=self._sync_equalizer_to_processor
        )

        # 使用 UI 主題配色（Spotify 風格）- CustomTkinter 會自動管理深色主題
        bg_color = self.theme.bg_color
        card_bg = self.theme.card_bg
        accent_color = self.theme.accent_color
        text_color = self.theme.text_color
        text_secondary = self.theme.text_secondary
        header_bg = self.theme.header_bg

        # 建立主框架（圓角框架）
        main_frame = ctk.CTkFrame(self.window, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # === 頂部標題和功能按鈕 ===
        # 使用 MusicHeaderView 顯示頂部標題和按鈕
        self.header_view = MusicHeaderView(
            parent=main_frame,
            on_download_click=self._open_download_dialog,
            on_playlist_click=self._show_playlists,
            on_history_click=self._show_play_history,
            on_most_played_click=self._show_most_played,
            on_equalizer_click=self._show_equalizer
        )

        # === 主要內容區 ===
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # 建立容器用於音樂庫視圖和搜尋框
        library_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        library_container.pack(side="left", fill="both", expand=True, padx=(0, 10))

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

        # 建立右側容器 (包含播放控制和歌詞)
        right_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_container.pack(side="left", fill="both", expand=False)

        # 使用 MusicPlaybackView 建立播放控制區
        self.playback_view = MusicPlaybackView(
            parent_frame=right_container,
            music_manager=self.music_manager,
            on_play_pause=self._toggle_play_pause,
            on_play_previous=self._play_previous,
            on_play_next=self._play_next,
            on_volume_change=self._on_volume_change,
            on_cycle_play_mode=self._cycle_play_mode
        )
        self.playback_view.create_view()

        # 建立歌詞顯示區 (在播放控制下方)
        self.lyrics_view = MusicLyricsView(
            parent_frame=right_container,
            on_lyric_click=self._on_lyric_click
        )
        self.lyrics_view.create_view()

        # 保持向後相容:設定引用
        self.current_song_label = self.playback_view.current_song_label
        self.artist_label = self.playback_view.artist_label
        self.play_pause_button = self.playback_view.play_pause_button
        self.play_mode_button = self.playback_view.play_mode_button
        self.progress_bar = self.playback_view.progress_bar
        self.time_label = self.playback_view.time_label
        self.volume_scale = self.playback_view.volume_scale
        self.album_cover_label = self.playback_view.album_cover_label

        # 初始化歌曲操作模組
        self.song_actions = MusicSongActions(
            parent_window=self.window,
            music_manager=self.music_manager,
            file_manager=self.file_manager,
            on_play_song=self._on_song_action_play,
            on_reload_library=self._reload_music_library
        )

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

    def _display_songs(self, songs):
        """顯示歌曲列表（向後相容，實際由 MusicLibraryView 處理）

        Args:
            songs (list): 歌曲列表
        """
        if self.library_view:
            self.library_view.display_songs(songs)
        else:
            # 向後相容的實現
            self.playlist = songs
            for item in self.song_tree.get_children():
                self.song_tree.delete(item)
            for song in songs:
                duration_str = self.music_manager.format_duration(song['duration'])
                self.song_tree.insert('', 'end', values=(song['title'], duration_str))

    def _play_song(self, song):
        """播放歌曲（自動選擇播放器）

        Args:
            song (dict): 歌曲資訊
        """
        try:
            # 使用適當的播放器播放
            if self.use_audio_player:
                self._play_with_audio_player(song)
            else:
                self._play_with_pygame(song)

            # 共同的後續處理
            self.current_song = song
            self.is_playing = True
            self.is_paused = False

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

            # 載入並顯示歌詞
            self._load_lyrics_for_song(song)

            # 啟動進度更新執行緒
            threading.Thread(target=self._update_progress, daemon=True).start()

            # 背景執行元數據補全
            if self.metadata_fetcher.is_enabled():
                def on_fetch_complete(success, metadata):
                    if success and metadata:
                        # 在主執行緒更新 UI
                        self.window.after(0, lambda: self._on_metadata_updated(song, metadata))

                self.metadata_fetcher.fetch_metadata_async(song, on_fetch_complete)

            # 更新 Discord Rich Presence
            self._update_discord_presence(song)

            logger.info(f"開始播放: {song['title']}")

        except Exception as e:
            logger.error(f"播放失敗: {e}")
            messagebox.showerror("播放錯誤", f"無法播放歌曲:\n{str(e)}")

    def _play_with_audio_player(self, song):
        """使用 AudioPlayer 播放

        Args:
            song (dict): 歌曲資訊
        """
        # 同步等化器設定到 AudioProcessor
        self._sync_equalizer_to_processor()

        # 播放音樂
        result = self.audio_player.play(song['audio_path'])
        if not result:
            raise Exception("AudioPlayer 播放失敗")

        self.start_time = time.time()
        self.pause_position = 0

    def _play_with_pygame(self, song):
        """使用 pygame.mixer 播放（fallback）

        Args:
            song (dict): 歌曲資訊
        """
        pygame.mixer.music.load(song['audio_path'])
        pygame.mixer.music.play()
        self.start_time = time.time()
        self.pause_position = 0

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

    def _start_first_song_if_available(self):
        """如果沒有歌曲但有播放列表，播放第一首歌

        Returns:
            bool: 如果開始播放第一首歌則返回 True
        """
        if self.playlist:
            self.current_index = 0
            self._play_song(self.playlist[0])
            return True
        return False

    def _resume_playback(self):
        """恢復播放"""
        if self.use_audio_player:
            self.audio_player.resume()
        else:
            pygame.mixer.music.unpause()

        self.is_paused = False
        self.start_time = time.time() - self.pause_position
        self._update_playback_ui(is_paused=False)

    def _pause_playback(self):
        """暫停播放"""
        if self.use_audio_player:
            self.audio_player.pause()
        else:
            pygame.mixer.music.pause()

        self.is_paused = True
        self.pause_position = time.time() - self.start_time
        self._update_playback_ui(is_paused=True)

    def _update_playback_ui(self, is_paused):
        """更新播放/暫停按鈕 UI

        Args:
            is_paused (bool): 是否為暫停狀態
        """
        if self.playback_view:
            self.playback_view.update_play_pause_button(is_paused=is_paused)

    def _toggle_play_pause(self):
        """切換播放/暫停"""
        # 如果沒有歌曲，嘗試播放第一首
        if not self.current_song:
            self._start_first_song_if_available()
            return

        # 如果正在播放，切換暫停/恢復
        if self.is_playing:
            if self.is_paused:
                self._resume_playback()
            else:
                self._pause_playback()
        else:
            # 重新播放當前歌曲
            self._play_song(self.current_song)

    def _play_previous(self):
        """播放上一首"""
        if not self.playlist:
            return

        self.current_index = (self.current_index - 1) % len(self.playlist)
        self._play_song(self.playlist[self.current_index])

    def _is_valid_current_index(self):
        """檢查當前索引是否有效

        Returns:
            bool: 如果當前索引有效則返回 True
        """
        return 0 <= self.current_index < len(self.playlist)

    def _get_available_shuffle_indices(self):
        """取得隨機模式下可用的歌曲索引

        Returns:
            list: 可用的歌曲索引列表
        """
        available_indices = [i for i in range(len(self.playlist)) if i not in self.played_indices]

        if not available_indices:
            # 所有歌曲都播放過了,清空記錄重新開始
            self.played_indices = []
            available_indices = list(range(len(self.playlist)))

        return available_indices

    def _play_next_in_repeat_one_mode(self):
        """單曲循環模式 - 重播當前歌曲"""
        if self._is_valid_current_index():
            self._play_song(self.playlist[self.current_index])

    def _play_next_in_shuffle_mode(self):
        """隨機模式 - 隨機選擇下一首歌曲"""
        available_indices = self._get_available_shuffle_indices()
        self.current_index = random.choice(available_indices)
        self.played_indices.append(self.current_index)
        self._play_song(self.playlist[self.current_index])

    def _play_next_in_sequential_mode(self):
        """順序模式或列表循環模式 - 播放下一首"""
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self._play_song(self.playlist[self.current_index])

    def _play_next(self):
        """播放下一首"""
        if not self.playlist:
            return

        if self.play_mode == 'repeat_one':
            self._play_next_in_repeat_one_mode()
        elif self.play_mode == 'shuffle':
            self._play_next_in_shuffle_mode()
        else:
            self._play_next_in_sequential_mode()

    def _on_volume_change(self, value):
        """音量改變事件

        Args:
            value (str): 音量值(0-100)
        """
        volume = float(value) / 100
        self.volume = volume

        # 設定音量
        if self.use_audio_player:
            self.audio_player.set_volume(volume)
        else:
            pygame.mixer.music.set_volume(volume)

        # 儲存音量設定到設定檔
        self.music_manager.config_manager.set_music_volume(int(float(value)))

    def _should_play_next(self):
        """檢查是否應該播放下一首

        Returns:
            bool: 如果播放結束應播放下一首則返回 True
        """
        if self.use_audio_player:
            # AudioPlayer 使用回調處理播放結束
            return False
        else:
            return not pygame.mixer.music.get_busy() and not self.is_paused

    def _handle_paused_state(self):
        """處理暫停狀態

        Returns:
            bool: 如果當前為暫停狀態則返回 True
        """
        if self.is_paused:
            time.sleep(0.1)
            return True
        return False

    def _calculate_playback_position(self):
        """計算當前播放位置

        Returns:
            tuple: (當前位置(秒), 總時長(秒))
        """
        if self.use_audio_player:
            # 從 AudioPlayer 獲取精確位置
            current_pos = self.audio_player.get_position()
            total_duration = self.audio_player.get_duration()
        else:
            # 從 pygame 計算位置
            current_pos = time.time() - self.start_time
            total_duration = self.current_song.get('duration', 0)

        return current_pos, total_duration

    def _format_time_text(self, current_pos, total_duration):
        """格式化時間文字

        Args:
            current_pos (float): 當前播放位置(秒)
            total_duration (int): 總時長(秒)

        Returns:
            str: 格式化的時間文字 "MM:SS / MM:SS"
        """
        current_str = self.music_manager.format_duration(int(current_pos))
        total_str = self.music_manager.format_duration(total_duration)
        return f"{current_str} / {total_str}"

    def _update_ui_progress(self, current_pos, total_duration):
        """更新 UI 進度條和時間標籤

        Args:
            current_pos (float): 當前播放位置(秒)
            total_duration (int): 總時長(秒)
        """
        if total_duration <= 0 or not self.playback_view:
            return

        # 更新進度條
        progress = min(100, (current_pos / total_duration) * 100)
        self.window.after(0, lambda: self.playback_view.update_progress(progress))

        # 更新時間標籤
        time_text = self._format_time_text(current_pos, total_duration)
        self.window.after(0, lambda t=time_text: self.playback_view.update_time_label(t))

        # 更新歌詞同步
        if self.lyrics_view:
            self.window.after(0, lambda p=current_pos: self.lyrics_view.update_current_time(p))

    def _update_progress(self):
        """更新播放進度"""
        while self.is_playing and self.current_song:
            try:
                # 檢查是否播放結束
                if self._should_play_next():
                    self.window.after(0, self._play_next)
                    break

                # 處理暫停狀態
                if self._handle_paused_state():
                    continue

                # 計算播放位置並更新 UI
                current_pos, total_duration = self._calculate_playback_position()
                self._update_ui_progress(current_pos, total_duration)

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

    def _on_song_action_play(self, song, playlist, index):
        """歌曲操作模組的播放回調

        Args:
            song: 歌曲資訊
            playlist: 播放列表
            index: 歌曲在播放列表中的索引
        """
        self.playlist = playlist
        self.current_index = index
        self._play_song(song)

    def _play_song_from_tree(self, song):
        """從樹狀結構播放歌曲(使用 song_actions 模組)"""
        if self.song_actions:
            self.song_actions.play_song_from_tree(song)

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
        """刪除歌曲(使用 song_actions 模組)"""
        if self.song_actions:
            self.song_actions.delete_song(song)

    def _move_song_to_category(self, item_id, song):
        """移動歌曲到不同分類(使用 song_actions 模組)"""
        if self.song_actions:
            self.song_actions.move_song_to_category(song)

    def _show_play_history(self):
        """顯示播放歷史對話框"""
        self.history_dialog.show_play_history()

    def _show_most_played(self):
        """顯示最常播放的歌曲對話框"""
        self.history_dialog.show_most_played()

    def _show_playlists(self):
        """顯示播放列表管理對話框"""
        self.playlist_dialog.show_playlists()

    def _show_equalizer(self):
        """顯示等化器設定對話框"""
        if self.equalizer_dialog:
            self.equalizer_dialog.show()

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

    def _load_lyrics_for_song(self, song):
        """載入歌曲的歌詞檔案

        Args:
            song (dict): 歌曲資訊
        """
        try:
            # 取得音樂檔案路徑
            audio_path = song.get('audio_path', '')
            if not audio_path:
                if self.lyrics_view:
                    self.lyrics_view.show_no_lyrics_message()
                return

            # 取得對應的 LRC 檔案路徑
            lrc_path = Path(audio_path).with_suffix('.lrc')

            if not lrc_path.exists():
                logger.info(f"找不到歌詞檔案: {lrc_path}")
                if self.lyrics_view:
                    self.lyrics_view.show_no_lyrics_message()
                return

            # 解析歌詞
            lyrics = self.lyrics_parser.parse_lrc_file(str(lrc_path))

            if lyrics and self.lyrics_view:
                self.lyrics_view.set_lyrics(lyrics)
                logger.info(f"成功載入歌詞: {lrc_path.name} ({len(lyrics)} 行)")
            else:
                if self.lyrics_view:
                    self.lyrics_view.show_no_lyrics_message()

        except Exception as e:
            logger.error(f"載入歌詞時發生錯誤: {e}")
            if self.lyrics_view:
                self.lyrics_view.show_no_lyrics_message()

    def _on_lyric_click(self, time):
        """點擊歌詞跳轉到指定時間

        Args:
            time (float): 跳轉的時間點(秒)
        """
        if not self.current_song or not self.is_playing:
            return

        try:
            if self.use_audio_player:
                # AudioPlayer 支援直接跳轉
                self.audio_player.seek(time)
                logger.info(f"跳轉到歌詞位置: {time:.2f} 秒")
            else:
                # pygame 需要重新載入
                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.current_song['audio_path'])
                pygame.mixer.music.play(start=time)
                self.start_time = time.time() - time
                self.is_paused = False
                logger.info(f"跳轉到歌詞位置: {time:.2f} 秒")

        except Exception as e:
            logger.error(f"跳轉播放位置失敗: {e}")

    def _sync_equalizer_to_processor(self):
        """同步等化器設定到 AudioProcessor"""
        if not self.use_audio_player or not self.audio_processor:
            return

        try:
            # 取得等化器設定
            gains = self.equalizer.get_gains()

            # 同步到 AudioProcessor 的 EqualizerFilter
            if self.audio_processor.equalizer and gains:
                if len(gains) == len(self.audio_processor.equalizer.frequencies):
                    self.audio_processor.equalizer.set_all_gains(gains)
                    logger.info("等化器設定已同步到 AudioProcessor")

        except Exception as e:
            logger.error(f"同步等化器設定失敗: {e}")

    def _on_audio_player_end(self):
        """AudioPlayer 播放結束回調"""
        logger.info("AudioPlayer 播放結束，自動播放下一首")

        # 在主線程中觸發下一首
        if self.window:
            self.window.after(0, self._play_next)

    def _update_discord_presence(self, song):
        """更新 Discord Rich Presence 狀態

        Args:
            song (dict): 當前播放的歌曲資訊
        """
        if not self.discord_presence or not self.discord_presence.connected:
            return

        try:
            # 取得歌曲資訊
            song_name = song.get('title', 'Unknown')
            artist = song.get('uploader', 'Unknown Artist')
            album = song.get('album', None)
            duration = song.get('duration', 0)

            # 取得封面 URL（如果有）
            album_cover_url = song.get('thumbnail', None)

            # 更新 Discord 狀態
            self.discord_presence.update_playing(
                song_name=song_name,
                artist=artist,
                album=album,
                total_time=duration,
                album_cover_url=album_cover_url
            )

            logger.info(f"Discord Rich Presence 已更新: {song_name} - {artist}")

        except Exception as e:
            logger.error(f"更新 Discord Rich Presence 失敗: {e}")

    def cleanup(self):
        """清理資源(在應用程式完全關閉時呼叫)"""
        # 停止音樂
        if self.is_playing:
            if self.use_audio_player:
                self.audio_player.stop()
            else:
                pygame.mixer.music.stop()

        # 清除並斷開 Discord Rich Presence
        if self.discord_presence:
            self.discord_presence.clear()
            self.discord_presence.disconnect()
            logger.info("Discord Rich Presence 已斷開")

        logger.info("音樂播放器資源已清理")
