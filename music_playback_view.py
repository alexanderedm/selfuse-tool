"""音樂播放檢視模組 - 負責右側播放控制 UI"""
import customtkinter as ctk
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
        self.main_frame = None
        self.album_cover_label = None
        self.current_song_label = None
        self.artist_label = None
        self.time_label = None
        self.progress_slider = None
        self.progress_bar = None  # 向後相容別名
        self.play_pause_button = None
        self.play_mode_button = None
        self.volume_slider = None
        self.volume_scale = None  # 向後相容別名

        # 專輯封面快取
        self.thumbnail_cache = {}
        self.default_cover_image = None

        # 顏色主題
        self.accent_color = "#0078d4"
        self.hover_color = "#005a9e"

    def create_view(self):
        """建立播放控制檢視"""
        # 右側:播放控制區（大圓角框架）
        self.main_frame = ctk.CTkFrame(
            self.parent_frame,
            corner_radius=15,
            width=280
        )
        self.main_frame.pack(side="left", fill="both", expand=False, padx=(10, 0))
        self.main_frame.pack_propagate(False)

        # === 標題區 ===
        header_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12,
            fg_color="#0d47a1"
        )
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            header_frame,
            text="🎧 播放控制",
            font=("Microsoft JhengHei UI", 14, "bold"),
            text_color="white"
        ).pack(pady=10)

        # === 內容區 ===
        content_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # === 專輯封面（圓角） ===
        cover_frame = ctk.CTkFrame(
            content_frame,
            corner_radius=12,
            width=230,
            height=230
        )
        cover_frame.pack(pady=(0, 15))
        cover_frame.pack_propagate(False)

        self.album_cover_label = ctk.CTkLabel(
            cover_frame,
            text="🎵",
            font=("Arial", 48),
            text_color="#b0b0b0"
        )
        self.album_cover_label.pack(expand=True)

        # === 歌曲資訊區（圓角） ===
        info_frame = ctk.CTkFrame(
            content_frame,
            corner_radius=10
        )
        info_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            info_frame,
            text="正在播放:",
            font=("Microsoft JhengHei UI", 10),
            text_color="#b0b0b0"
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.current_song_label = ctk.CTkLabel(
            info_frame,
            text="未播放",
            font=("Microsoft JhengHei UI", 12, "bold"),
            wraplength=220,
            anchor="w"
        )
        self.current_song_label.pack(anchor="w", padx=10, pady=(0, 5))

        self.artist_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=("Microsoft JhengHei UI", 10),
            text_color="#b0b0b0",
            wraplength=220,
            anchor="w"
        )
        self.artist_label.pack(anchor="w", padx=10, pady=(0, 10))

        # === 播放模式按鈕（圓角） ===
        self.play_mode_button = ctk.CTkButton(
            content_frame,
            text="➡️ 順序播放",
            font=("Microsoft JhengHei UI", 11),
            height=38,
            corner_radius=10,
            command=self.on_cycle_play_mode
        )
        self.play_mode_button.pack(fill="x", pady=(0, 15))

        # === 進度條區域 ===
        progress_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        progress_frame.pack(fill="x", pady=(0, 15))

        # 時間標籤
        self.time_label = ctk.CTkLabel(
            progress_frame,
            text="00:00 / 00:00",
            font=("Microsoft JhengHei UI", 10),
            text_color="#b0b0b0"
        )
        self.time_label.pack(pady=(0, 5))

        # 進度滑桿（可拖動）
        self.progress_slider = ctk.CTkSlider(
            progress_frame,
            from_=0,
            to=100,
            height=20,
            button_color=self.accent_color,
            button_hover_color=self.hover_color,
            progress_color=self.accent_color,
            command=self._on_seek
        )
        self.progress_slider.set(0)
        self.progress_slider.pack(fill="x")

        # === 播放控制按鈕 ===
        control_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        control_frame.pack(pady=(0, 15))

        # 按鈕容器（置中）
        button_container = ctk.CTkFrame(
            control_frame,
            fg_color="transparent"
        )
        button_container.pack()

        # 上一首按鈕（中等圓角）
        prev_button = ctk.CTkButton(
            button_container,
            text="⏮",
            font=("Arial", 20),
            width=55,
            height=55,
            corner_radius=28,
            fg_color=self.accent_color,
            hover_color=self.hover_color,
            command=self.on_play_previous
        )
        prev_button.pack(side="left", padx=5)

        # 播放/暫停按鈕（大圓形）
        self.play_pause_button = ctk.CTkButton(
            button_container,
            text="▶",
            font=("Arial", 26),
            width=75,
            height=75,
            corner_radius=38,
            fg_color=self.accent_color,
            hover_color=self.hover_color,
            command=self.on_play_pause
        )
        self.play_pause_button.pack(side="left", padx=8)

        # 下一首按鈕（中等圓角）
        next_button = ctk.CTkButton(
            button_container,
            text="⏭",
            font=("Arial", 20),
            width=55,
            height=55,
            corner_radius=28,
            fg_color=self.accent_color,
            hover_color=self.hover_color,
            command=self.on_play_next
        )
        next_button.pack(side="left", padx=5)

        # === 音量控制區 ===
        volume_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        volume_frame.pack(fill="x")

        ctk.CTkLabel(
            volume_frame,
            text="🔊 音量",
            font=("Microsoft JhengHei UI", 11),
            text_color="#b0b0b0"
        ).pack(anchor="w", pady=(0, 5))

        self.volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=100,
            height=20,
            button_color=self.accent_color,
            button_hover_color=self.hover_color,
            progress_color=self.accent_color,
            command=self._on_volume_change_internal
        )
        # 從設定檔讀取音量
        saved_volume = self.music_manager.config_manager.get_music_volume()
        self.volume_slider.set(saved_volume)
        self.volume_slider.pack(fill="x")

        # 設定向後相容別名
        self.progress_bar = self.progress_slider
        self.volume_scale = self.volume_slider

    def _on_seek(self, value):
        """進度條拖動事件（內部處理）

        Args:
            value (float): 滑桿位置 (0-100)
        """
        # 這裡可以添加進度條拖動邏輯
        # 目前進度條主要用於顯示進度，實際拖動功能需要與播放器整合
        pass

    def _on_volume_change_internal(self, value):
        """音量滑桿變更事件（內部處理）

        Args:
            value (float): 音量值 (0-100)
        """
        if self.on_volume_change:
            self.on_volume_change(value)

    def update_current_song(self, song):
        """更新當前播放歌曲顯示

        Args:
            song (dict): 歌曲資訊
        """
        if self.current_song_label:
            self.current_song_label.configure(text=song['title'])

        if self.artist_label and song.get('uploader'):
            self.artist_label.configure(text=f"🎤 {song.get('uploader', '未知')}")

        # 更新專輯封面(在背景執行緒中)
        threading.Thread(target=self._update_album_cover, args=(song,), daemon=True).start()

    def update_play_pause_button(self, is_paused):
        """更新播放/暫停按鈕

        Args:
            is_paused (bool): 是否為暫停狀態
        """
        if self.play_pause_button:
            self.play_pause_button.configure(text="▶" if is_paused else "⏸")

    def update_progress(self, progress_value):
        """更新進度條

        Args:
            progress_value (float): 進度值 (0-100)
        """
        if self.progress_slider:
            self.progress_slider.set(progress_value)

    def update_time_label(self, time_text):
        """更新時間標籤

        Args:
            time_text (str): 時間文字,格式如 "01:30 / 03:45"
        """
        if self.time_label:
            self.time_label.configure(text=time_text)

    def update_play_mode(self, play_mode):
        """更新播放模式按鈕

        Args:
            play_mode (str): 播放模式 ('sequential', 'repeat_all', 'repeat_one', 'shuffle')
        """
        mode_config = {
            'sequential': {'text': '➡️ 順序播放', 'fg_color': ("gray40", "gray25")},
            'repeat_all': {'text': '🔂 列表循環', 'fg_color': '#0078d4'},
            'repeat_one': {'text': '🔁 單曲循環', 'fg_color': '#d43d00'},
            'shuffle': {'text': '🔀 隨機播放', 'fg_color': '#00b050'}
        }

        if play_mode in mode_config and self.play_mode_button:
            config = mode_config[play_mode]
            self.play_mode_button.configure(
                text=config['text'],
                fg_color=config['fg_color']
            )

    def reset_display(self):
        """重置顯示(停止播放時)"""
        if self.current_song_label:
            self.current_song_label.configure(text="未播放")
        if self.artist_label:
            self.artist_label.configure(text="")
        if self.time_label:
            self.time_label.configure(text="00:00 / 00:00")
        if self.progress_slider:
            self.progress_slider.set(0)
        if self.play_pause_button:
            self.play_pause_button.configure(text="▶")
        # 重置專輯封面
        if self.album_cover_label:
            self.album_cover_label.configure(image=None, text="🎵")

    def get_volume(self):
        """取得當前音量

        Returns:
            int: 音量值 (0-100)
        """
        if self.volume_slider:
            return int(self.volume_slider.get())
        return 50

    def set_volume(self, volume):
        """設定音量

        Args:
            volume (int): 音量值 (0-100)
        """
        if self.volume_slider:
            self.volume_slider.set(volume)

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
                self.album_cover_label.configure(image=cover_image, text="")
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
            # 最大寬度和高度設為 230px（配合圓角框架）
            max_size = 230
            original_width, original_height = image.size

            # 計算縮放比例
            ratio = min(max_size / original_width, max_size / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            # 使用高品質重採樣保持長寬比
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 轉換為 PhotoImage
            photo = ctk.CTkImage(light_image=image, dark_image=image, size=(new_width, new_height))

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
            CTkImage: 預設封面圖片
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

            self.default_cover_image = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 200))
            return self.default_cover_image

        except Exception as e:
            logger.error(f"建立預設封面失敗: {e}")
            return None
