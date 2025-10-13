"""音樂播放檢視模組 - 負責右側播放控制 UI"""
import tkinter as tk
from tkinter import ttk
import threading
import requests
from PIL import Image, ImageTk, ImageDraw
from io import BytesIO
from logger import logger


class MusicPlaybackView:
    """管理播放控制區域的 UI 顯示和更新"""

    def __init__(self, parent_frame, music_manager, on_play_pause, on_play_previous,
                 on_play_next, on_volume_change, on_cycle_play_mode):
        """初始化播放檢視

        Args:
            parent_frame: 父框架
            music_manager: 音樂管理器實例
            on_play_pause: 播放/暫停回調
            on_play_previous: 上一首回調
            on_play_next: 下一首回調
            on_volume_change: 音量變更回調
            on_cycle_play_mode: 播放模式切換回調
        """
        self.parent_frame = parent_frame
        self.music_manager = music_manager
        self.on_play_pause = on_play_pause
        self.on_play_previous = on_play_previous
        self.on_play_next = on_play_next
        self.on_volume_change = on_volume_change
        self.on_cycle_play_mode = on_cycle_play_mode

        # UI 元件
        self.album_cover_label = None
        self.current_song_label = None
        self.artist_label = None
        self.time_label = None
        self.progress_bar = None
        self.play_pause_button = None
        self.play_mode_button = None
        self.volume_scale = None

        # 專輯封面快取
        self.thumbnail_cache = {}
        self.default_cover_image = None

        # 顏色主題
        self.card_bg = "#2d2d2d"
        self.accent_color = "#0078d4"
        self.text_color = "#e0e0e0"
        self.text_secondary = "#a0a0a0"
        self.header_bg = "#0d47a1"

    def create_view(self):
        """建立播放控制檢視"""
        # 右側:播放控制區
        right_frame = tk.Frame(self.parent_frame, bg=self.card_bg, relief=tk.RIDGE, bd=1)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        right_frame.config(width=250)

        control_header = tk.Label(
            right_frame,
            text="🎧 播放控制",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=self.header_bg,
            fg="white",
            pady=8
        )
        control_header.pack(fill=tk.X)

        control_content = tk.Frame(right_frame, bg=self.card_bg)
        control_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 專輯封面(縮圖)
        self.album_cover_label = tk.Label(
            control_content,
            bg=self.card_bg,
            text="🎵",
            font=("Arial", 48),
            fg=self.text_secondary
        )
        self.album_cover_label.pack(pady=(0, 10))

        # 當前播放歌曲
        tk.Label(
            control_content,
            text="正在播放:",
            font=("Microsoft JhengHei UI", 9),
            bg=self.card_bg,
            fg=self.text_secondary
        ).pack(anchor=tk.W, pady=(0, 5))

        self.current_song_label = tk.Label(
            control_content,
            text="未播放",
            font=("Microsoft JhengHei UI", 10, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            wraplength=220,
            justify=tk.LEFT
        )
        self.current_song_label.pack(anchor=tk.W, pady=(0, 5))

        # 藝術家/上傳者
        self.artist_label = tk.Label(
            control_content,
            text="",
            font=("Microsoft JhengHei UI", 9),
            bg=self.card_bg,
            fg=self.text_secondary,
            wraplength=220,
            justify=tk.LEFT
        )
        self.artist_label.pack(anchor=tk.W, pady=(0, 15))

        # 播放進度條
        self.time_label = tk.Label(
            control_content,
            text="00:00 / 00:00",
            font=("Microsoft JhengHei UI", 9),
            bg=self.card_bg,
            fg=self.text_secondary
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
        button_frame = tk.Frame(control_content, bg=self.card_bg)
        button_frame.pack(pady=(0, 10))

        prev_button = tk.Button(
            button_frame,
            text="⏮",
            font=("Arial", 14),
            bg=self.accent_color,
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self.on_play_previous
        )
        prev_button.pack(side=tk.LEFT, padx=5)

        self.play_pause_button = tk.Button(
            button_frame,
            text="▶",
            font=("Arial", 16),
            bg=self.accent_color,
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=5,
            command=self.on_play_pause
        )
        self.play_pause_button.pack(side=tk.LEFT, padx=5)

        next_button = tk.Button(
            button_frame,
            text="⏭",
            font=("Arial", 14),
            bg=self.accent_color,
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=self.on_play_next
        )
        next_button.pack(side=tk.LEFT, padx=5)

        # 播放模式按鈕
        mode_frame = tk.Frame(control_content, bg=self.card_bg)
        mode_frame.pack(pady=(0, 15))

        self.play_mode_button = tk.Button(
            mode_frame,
            text="➡️ 順序播放",
            font=("Microsoft JhengHei UI", 9),
            bg="#353535",
            fg=self.text_color,
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=10,
            pady=5,
            command=self.on_cycle_play_mode
        )
        self.play_mode_button.pack()

        # 音量控制
        tk.Label(
            control_content,
            text="🔊 音量",
            font=("Microsoft JhengHei UI", 9),
            bg=self.card_bg,
            fg=self.text_secondary
        ).pack(anchor=tk.W, pady=(0, 5))

        self.volume_scale = tk.Scale(
            control_content,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.on_volume_change,
            bg=self.card_bg,
            fg=self.text_color,
            highlightthickness=0,
            troughcolor="#353535",
            activebackground=self.accent_color
        )
        # 從設定檔讀取音量
        saved_volume = self.music_manager.config_manager.get_music_volume()
        self.volume_scale.set(saved_volume)
        self.volume_scale.pack(fill=tk.X)

    def update_current_song(self, song):
        """更新當前播放歌曲顯示

        Args:
            song (dict): 歌曲資訊
        """
        if self.current_song_label:
            self.current_song_label.config(text=song['title'])

        if self.artist_label and song.get('uploader'):
            self.artist_label.config(text=f"🎤 {song.get('uploader', '未知')}")

        # 更新專輯封面(在背景執行緒中)
        threading.Thread(target=self._update_album_cover, args=(song,), daemon=True).start()

    def update_play_pause_button(self, is_paused):
        """更新播放/暫停按鈕

        Args:
            is_paused (bool): 是否為暫停狀態
        """
        if self.play_pause_button:
            self.play_pause_button.config(text="▶" if is_paused else "⏸")

    def update_progress(self, progress_value):
        """更新進度條

        Args:
            progress_value (float): 進度值 (0-100)
        """
        if self.progress_bar:
            self.progress_bar['value'] = progress_value

    def update_time_label(self, time_text):
        """更新時間標籤

        Args:
            time_text (str): 時間文字,格式如 "01:30 / 03:45"
        """
        if self.time_label:
            self.time_label.config(text=time_text)

    def update_play_mode(self, play_mode):
        """更新播放模式按鈕

        Args:
            play_mode (str): 播放模式 ('sequential', 'repeat_all', 'repeat_one', 'shuffle')
        """
        mode_config = {
            'sequential': {'text': '➡️ 順序播放', 'bg': '#353535'},
            'repeat_all': {'text': '🔂 列表循環', 'bg': '#0078d4'},
            'repeat_one': {'text': '🔁 單曲循環', 'bg': '#d43d00'},
            'shuffle': {'text': '🔀 隨機播放', 'bg': '#00b050'}
        }

        if play_mode in mode_config and self.play_mode_button:
            config = mode_config[play_mode]
            self.play_mode_button.config(text=config['text'], bg=config['bg'])

    def reset_display(self):
        """重置顯示(停止播放時)"""
        if self.current_song_label:
            self.current_song_label.config(text="未播放")
        if self.artist_label:
            self.artist_label.config(text="")
        if self.time_label:
            self.time_label.config(text="00:00 / 00:00")
        if self.progress_bar:
            self.progress_bar['value'] = 0
        if self.play_pause_button:
            self.play_pause_button.config(text="▶")
        # 重置專輯封面
        if self.album_cover_label:
            self.album_cover_label.config(image="", text="🎵")

    def get_volume(self):
        """取得當前音量

        Returns:
            int: 音量值 (0-100)
        """
        if self.volume_scale:
            return int(self.volume_scale.get())
        return 50

    def set_volume(self, volume):
        """設定音量

        Args:
            volume (int): 音量值 (0-100)
        """
        if self.volume_scale:
            self.volume_scale.set(volume)

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
