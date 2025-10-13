"""音樂播放控制器模組 - 處理播放邏輯"""
import pygame
import time
import random
from logger import logger


class MusicPlayerController:
    """音樂播放控制器 - 處理播放、暫停、下一首等邏輯"""

    def __init__(self, music_manager):
        """初始化播放控制器

        Args:
            music_manager: 音樂管理器實例
        """
        self.music_manager = music_manager

        # 播放器狀態
        self.current_song = None
        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.is_paused = False
        self.volume = self.music_manager.config_manager.get_music_volume() / 100.0

        # 播放模式: 'sequential', 'shuffle', 'repeat_one', 'repeat_all'
        self.play_mode = 'sequential'
        self.played_indices = []  # 隨機模式用

        # 時間追蹤
        self.start_time = 0
        self.pause_position = 0

        # 初始化 pygame mixer
        try:
            pygame.mixer.init()
            logger.info("Pygame mixer 初始化成功")
        except Exception as e:
            logger.error(f"Pygame mixer 初始化失敗: {e}", exc_info=True)

    def play_song(self, song):
        """播放歌曲

        Args:
            song (dict): 歌曲資訊

        Returns:
            bool: 播放成功返回 True,失敗返回 False
        """
        try:
            pygame.mixer.music.load(song['audio_path'])
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.current_song = song
            self.start_time = time.time()
            self.pause_position = 0

            logger.info(f"開始播放: {song['title']}")
            return True

        except Exception as e:
            logger.error(f"播放失敗: {e}", exc_info=True)
            return False

    def toggle_play_pause(self):
        """切換播放/暫停狀態

        Returns:
            str: 當前狀態 'playing', 'paused', 或 'stopped'
        """
        if not self.current_song:
            # 如果沒有歌曲,播放第一首
            if self.playlist:
                self.current_index = 0
                self.play_song(self.playlist[0])
                return 'playing'
            return 'stopped'

        if self.is_playing:
            if self.is_paused:
                # 恢復播放
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.start_time = time.time() - self.pause_position
                return 'playing'
            else:
                # 暫停
                pygame.mixer.music.pause()
                self.is_paused = True
                self.pause_position = time.time() - self.start_time
                return 'paused'
        else:
            # 重新播放
            if self.current_song:
                self.play_song(self.current_song)
                return 'playing'
            return 'stopped'

    def play_previous(self):
        """播放上一首

        Returns:
            dict: 上一首歌曲資訊,如果沒有則返回 None
        """
        if not self.playlist:
            return None

        self.current_index = (self.current_index - 1) % len(self.playlist)
        song = self.playlist[self.current_index]
        self.play_song(song)
        return song

    def play_next(self):
        """播放下一首

        Returns:
            dict: 下一首歌曲資訊,如果沒有則返回 None
        """
        if not self.playlist:
            return None

        if self.play_mode == 'repeat_one':
            # 單曲循環模式 - 重播當前歌曲
            if 0 <= self.current_index < len(self.playlist):
                song = self.playlist[self.current_index]
                self.play_song(song)
                return song
        elif self.play_mode == 'shuffle':
            # 隨機模式
            available_indices = [i for i in range(len(self.playlist)) if i not in self.played_indices]

            if not available_indices:
                # 所有歌曲都播放過了,清空記錄重新開始
                self.played_indices = []
                available_indices = list(range(len(self.playlist)))

            self.current_index = random.choice(available_indices)
            self.played_indices.append(self.current_index)
            song = self.playlist[self.current_index]
            self.play_song(song)
            return song
        else:
            # 順序模式或列表循環模式
            self.current_index = (self.current_index + 1) % len(self.playlist)
            song = self.playlist[self.current_index]
            self.play_song(song)
            return song

    def set_volume(self, volume):
        """設定音量

        Args:
            volume (int): 音量值 (0-100)
        """
        volume_float = float(volume) / 100
        pygame.mixer.music.set_volume(volume_float)
        self.volume = volume_float
        # 儲存音量設定
        self.music_manager.config_manager.set_music_volume(int(volume))
        logger.info(f"音量已設定為: {volume}%")

    def cycle_play_mode(self):
        """循環切換播放模式

        Returns:
            str: 新的播放模式
        """
        modes = ['sequential', 'repeat_all', 'repeat_one', 'shuffle']
        current_index = modes.index(self.play_mode)
        next_index = (current_index + 1) % len(modes)
        self.play_mode = modes[next_index]

        # 如果切換到隨機模式,清空已播放記錄
        if self.play_mode == 'shuffle':
            self.played_indices = []

        logger.info(f"播放模式已切換為: {self.play_mode}")
        return self.play_mode

    def get_play_mode_config(self):
        """取得當前播放模式的配置

        Returns:
            dict: 包含 'text' 和 'bg' 的配置字典
        """
        mode_config = {
            'sequential': {'text': '➡️ 順序播放', 'bg': '#353535'},
            'repeat_all': {'text': '🔂 列表循環', 'bg': '#0078d4'},
            'repeat_one': {'text': '🔁 單曲循環', 'bg': '#d43d00'},
            'shuffle': {'text': '🔀 隨機播放', 'bg': '#00b050'}
        }
        return mode_config.get(self.play_mode, mode_config['sequential'])

    def set_playlist(self, songs, index=0):
        """設定播放列表

        Args:
            songs (list): 歌曲列表
            index (int): 起始索引,默認為 0
        """
        self.playlist = songs
        self.current_index = index
        logger.info(f"播放列表已設定: {len(songs)} 首歌曲, 起始索引: {index}")

    def get_current_position(self):
        """取得當前播放位置

        Returns:
            tuple: (當前位置秒數, 總時長秒數)
        """
        if not self.current_song:
            return (0, 0)

        if self.is_paused:
            current_pos = self.pause_position
        else:
            current_pos = time.time() - self.start_time

        total_duration = self.current_song.get('duration', 0)
        return (int(current_pos), total_duration)

    def is_finished(self):
        """檢查當前歌曲是否播放完畢

        Returns:
            bool: 如果播放完畢返回 True
        """
        return self.is_playing and not self.is_paused and not pygame.mixer.music.get_busy()

    def stop(self):
        """停止播放"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        logger.info("音樂播放已停止")

    def cleanup(self):
        """清理資源"""
        if self.is_playing:
            pygame.mixer.music.stop()
        logger.info("播放控制器資源已清理")
