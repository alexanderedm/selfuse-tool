from src.plugins.plugin_base import Plugin
from src.music.managers.music_manager import MusicManager
from src.music.windows.music_window import MusicWindow
from src.core.logger import logger
from pystray import MenuItem as item
import pystray
import pygame

class MusicPlugin(Plugin):
    @property
    def name(self) -> str:
        return "music_player"

    @property
    def description(self) -> str:
        return "Local music player with YouTube download support."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def default_enabled(self) -> bool:
        return True

    def start(self) -> None:
        pass

    def on_load(self, context) -> None:
        super().on_load(context)
        self.app = context
        try:
            logger.info("Initializing Music Manager...")
            self.music_manager = MusicManager(self.app.config_manager)
            self.music_window = None
        except Exception as e:
            logger.error(f"Failed to initialize MusicPlugin: {e}")

    def on_unload(self) -> None:
        if self.music_window:
            self.music_window.cleanup()
        try:
           if pygame.mixer.get_init():
               pygame.mixer.music.stop()
        except:
            pass
        super().on_unload()

    def get_menu_items(self) -> list:
        return [
            item("🎵 本地音樂播放器", self.open_music_player),
            pystray.Menu.SEPARATOR,
            item(
                "🎵 音樂控制",
                pystray.Menu(
                    item("⏯ 播放/暫停", self.toggle_play_pause),
                    item("⏭ 下一首", self.play_next),
                    item("⏮ 上一首", self.play_previous),
                    item("⏹ 停止", self.stop_music),
                ),
            )
        ]

    def open_music_player(self):
        try:
            if self.music_window is None:
                self.music_window = MusicWindow(
                    self.music_manager, tk_root=self.app.tk_root
                )
                self.music_window.show()
            elif self.music_window.window is None:
                self.music_window.show()
            else:
                try:
                    self.music_window.window.lift()
                    self.music_window.window.focus_force()
                except:
                    self.music_window.show()
        except Exception as e:
            logger.exception("Error opening music player")

    def toggle_play_pause(self):
        if self.music_window:
            self.music_window._toggle_play_pause()
            if self.music_window.current_song:
                status = "暫停" if self.music_window.is_paused else "播放中"
                self.app.show_notification(f"{status}: {self.music_window.current_song['title']}", "音樂播放器")
            else:
                self.app.show_notification("沒有正在播放的歌曲", "音樂播放器")
        else:
             self.app.show_notification("請先開啟音樂播放器", "音樂播放器")

    def play_next(self):
        if self.music_window:
            self.music_window._play_next()
        else:
             self.app.show_notification("請先開啟音樂播放器", "音樂播放器")

    def play_previous(self):
        if self.music_window:
            self.music_window._play_previous()
        else:
             self.app.show_notification("請先開啟音樂播放器", "音樂播放器")

    def stop_music(self):
        if self.music_window:
           try:
                pygame.mixer.music.stop()
                self.music_window.is_playing = False
                self.music_window.is_paused = False
                self.app.show_notification("音樂已停止", "音樂播放器")
           except:
               pass
