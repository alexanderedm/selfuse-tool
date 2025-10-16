"""Discord Rich Presence 整合模組

用於在 Discord 顯示當前播放的音樂資訊
"""
import os
import logging
from typing import Optional

try:
    from pypresence import Presence
    PYPRESENCE_AVAILABLE = True
except ImportError:
    PYPRESENCE_AVAILABLE = False
    Presence = None

logger = logging.getLogger(__name__)


class DiscordPresence:
    """Discord Rich Presence 管理器

    使用 pypresence 套件在 Discord 顯示當前播放狀態
    """

    def __init__(self, client_id: Optional[str] = None):
        """初始化 Discord Presence

        Args:
            client_id: Discord Application Client ID
                      如果為 None，會嘗試從環境變數 DISCORD_CLIENT_ID 讀取
        """
        self.client_id = client_id or os.getenv('DISCORD_CLIENT_ID')
        self.rpc: Optional[Presence] = None
        self.connected = False

        if not PYPRESENCE_AVAILABLE:
            logger.warning("pypresence 套件未安裝，Discord Rich Presence 功能無法使用")

        if not self.client_id:
            logger.info("未設定 Discord Client ID，Rich Presence 功能已停用")

    def connect(self) -> bool:
        """連接到 Discord

        Returns:
            bool: 連接成功返回 True，否則返回 False
        """
        if not PYPRESENCE_AVAILABLE or not self.client_id:
            return False

        if self.connected and self.rpc:
            return True

        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            self.connected = True
            logger.info("已連接到 Discord Rich Presence")
            return True
        except Exception as e:
            logger.error(f"連接 Discord 失敗: {e}")
            self.connected = False
            return False

    def update_playing(
        self,
        song_name: str,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        current_time: Optional[int] = None,
        total_time: Optional[int] = None,
        album_cover_url: Optional[str] = None
    ) -> bool:
        """更新 Discord 狀態為正在播放

        Args:
            song_name: 歌曲名稱
            artist: 藝術家名稱
            album: 專輯名稱
            current_time: 當前播放時間（秒）
            total_time: 總時長（秒）
            album_cover_url: 專輯封面 URL

        Returns:
            bool: 更新成功返回 True
        """
        if not self.connected:
            if not self.connect():
                return False

        try:
            # 準備狀態資訊
            details = f"🎵 {song_name}"
            state = f"by {artist}" if artist else "播放中"

            # 準備更新參數
            update_kwargs = {
                'details': details,
                'state': state,
                'large_image': 'music_icon',  # 預設圖示
                'large_text': album or '音樂播放器',
                'small_image': 'play',
                'small_text': '播放中'
            }

            # 如果有封面 URL，使用封面圖片
            if album_cover_url:
                update_kwargs['large_image'] = album_cover_url

            # 如果有時間資訊，顯示進度
            if current_time is not None and total_time is not None:
                # 計算結束時間戳（用於顯示倒數）
                import time
                start_time = int(time.time()) - current_time
                end_time = start_time + total_time
                update_kwargs['start'] = start_time
                update_kwargs['end'] = end_time

            self.rpc.update(**update_kwargs)
            return True

        except Exception as e:
            logger.error(f"更新 Discord 狀態失敗: {e}")
            return False

    def clear(self) -> bool:
        """清除 Discord 狀態

        Returns:
            bool: 清除成功返回 True
        """
        if not self.connected or not self.rpc:
            return False

        try:
            self.rpc.clear()
            logger.info("已清除 Discord 狀態")
            return True
        except Exception as e:
            logger.error(f"清除 Discord 狀態失敗: {e}")
            return False

    def disconnect(self) -> None:
        """斷開與 Discord 的連接"""
        if self.rpc:
            try:
                self.rpc.close()
                logger.info("已斷開 Discord 連接")
            except Exception as e:
                logger.error(f"斷開 Discord 連接失敗: {e}")
            finally:
                self.rpc = None
                self.connected = False

    def __enter__(self):
        """Context manager 進入"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 離開"""
        self.disconnect()
