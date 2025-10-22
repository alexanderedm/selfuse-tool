"""Windows 媒體通知整合模組

使用 Windows Runtime API 整合系統媒體通知中心（SMTC）
顯示封面、歌曲資訊、媒體控制按鈕
"""
import asyncio
from typing import Optional, Callable
from pathlib import Path
from src.core.logger import logger

try:
    from winrt.windows.media import SystemMediaTransportControls, MediaPlaybackStatus
    from winrt.windows.media.playback import MediaPlayer
    from winrt.windows.storage import StorageFile
    from winrt.windows.storage.streams import RandomAccessStreamReference
    WINRT_AVAILABLE = True
except ImportError:
    WINRT_AVAILABLE = False
    logger.warning("winrt 未安裝，Windows 媒體通知功能無法使用")


class WindowsMediaNotification:
    """Windows 媒體通知管理器"""

    def __init__(self):
        """初始化媒體通知管理器"""
        if not WINRT_AVAILABLE:
            raise ImportError(
                "winrt-Windows.Media 未安裝。請執行: pip install winrt-Windows.Media"
            )

        self.smtc: Optional[SystemMediaTransportControls] = None
        self.media_player: Optional[MediaPlayer] = None
        self.callbacks = {}

        # 初始化媒體播放器
        try:
            self.media_player = MediaPlayer()
            self.smtc = self.media_player.system_media_transport_controls

            # 啟用控制按鈕
            self.smtc.is_enabled = True
            self.smtc.is_play_enabled = True
            self.smtc.is_pause_enabled = True
            self.smtc.is_next_enabled = True
            self.smtc.is_previous_enabled = True

            # 註冊事件處理
            self._setup_event_handlers()

            logger.info("Windows 媒體通知已初始化")

        except Exception as e:
            logger.error(f"初始化 Windows 媒體通知失敗: {e}")
            raise

    def _setup_event_handlers(self):
        """設定事件處理器"""
        try:
            self.smtc.button_pressed += self._on_button_pressed
            logger.debug("媒體控制事件處理器已註冊")
        except Exception as e:
            logger.error(f"設定事件處理器失敗: {e}")

    def _on_button_pressed(self, sender, args):
        """媒體按鈕按下事件處理"""
        try:
            from winrt.windows.media import SystemMediaTransportControlsButton

            button = args.button

            # 觸發對應的回調
            if button == SystemMediaTransportControlsButton.PLAY:
                if 'play' in self.callbacks:
                    self.callbacks['play']()
            elif button == SystemMediaTransportControlsButton.PAUSE:
                if 'pause' in self.callbacks:
                    self.callbacks['pause']()
            elif button == SystemMediaTransportControlsButton.NEXT:
                if 'next' in self.callbacks:
                    self.callbacks['next']()
            elif button == SystemMediaTransportControlsButton.PREVIOUS:
                if 'previous' in self.callbacks:
                    self.callbacks['previous']()

            logger.debug(f"媒體按鈕觸發: {button}")

        except Exception as e:
            logger.error(f"處理媒體按鈕事件失敗: {e}")

    def set_callback(self, action: str, callback: Callable):
        """設定媒體控制回調

        Args:
            action: 動作名稱 ('play', 'pause', 'next', 'previous')
            callback: 回調函數
        """
        self.callbacks[action] = callback
        logger.debug(f"已註冊媒體控制回調: {action}")

    async def update_metadata_async(
        self,
        title: str,
        artist: str = "",
        album: str = "",
        thumbnail_path: Optional[str] = None
    ):
        """更新媒體元數據（異步）

        Args:
            title: 歌曲標題
            artist: 藝術家
            album: 專輯
            thumbnail_path: 封面圖片路徑
        """
        try:
            updater = self.smtc.display_updater

            # 設定類型為音樂
            updater.type = 0  # MediaPlaybackType.Music

            # 更新音樂元數據
            music_properties = updater.music_properties
            music_properties.title = title
            music_properties.artist = artist
            music_properties.album_title = album

            # 更新封面
            if thumbnail_path and Path(thumbnail_path).exists():
                try:
                    storage_file = await StorageFile.get_file_from_path_async(thumbnail_path)
                    thumbnail = RandomAccessStreamReference.create_from_file(storage_file)
                    updater.thumbnail = thumbnail
                except Exception as e:
                    logger.warning(f"載入封面失敗: {e}")

            # 應用更新
            updater.update()

            logger.info(f"已更新媒體通知: {title} - {artist}")

        except Exception as e:
            logger.error(f"更新媒體元數據失敗: {e}")

    def update_metadata(
        self,
        title: str,
        artist: str = "",
        album: str = "",
        thumbnail_path: Optional[str] = None
    ):
        """更新媒體元數據（同步版本）

        Args:
            title: 歌曲標題
            artist: 藝術家
            album: 專輯
            thumbnail_path: 封面圖片路徑
        """
        try:
            # 在新的事件循環中運行異步方法
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                self.update_metadata_async(title, artist, album, thumbnail_path)
            )
            loop.close()
        except Exception as e:
            logger.error(f"更新媒體元數據失敗: {e}")

    def set_playback_status(self, is_playing: bool):
        """設定播放狀態

        Args:
            is_playing: 是否正在播放
        """
        try:
            if is_playing:
                self.smtc.playback_status = MediaPlaybackStatus.PLAYING
            else:
                self.smtc.playback_status = MediaPlaybackStatus.PAUSED

            logger.debug(f"播放狀態已更新: {'播放中' if is_playing else '暫停'}")

        except Exception as e:
            logger.error(f"設定播放狀態失敗: {e}")

    def clear_metadata(self):
        """清除媒體元數據"""
        try:
            self.smtc.display_updater.clear_all()
            self.smtc.playback_status = MediaPlaybackStatus.STOPPED
            logger.info("已清除媒體通知")
        except Exception as e:
            logger.error(f"清除媒體元數據失敗: {e}")

    def disable(self):
        """停用媒體通知"""
        try:
            if self.smtc:
                self.smtc.is_enabled = False
                logger.info("Windows 媒體通知已停用")
        except Exception as e:
            logger.error(f"停用媒體通知失敗: {e}")

    def enable(self):
        """啟用媒體通知"""
        try:
            if self.smtc:
                self.smtc.is_enabled = True
                logger.info("Windows 媒體通知已啟用")
        except Exception as e:
            logger.error(f"啟用媒體通知失敗: {e}")
