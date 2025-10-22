"""媒體鍵監聽器模組

支援監聽以下媒體鍵：
- 播放/暫停 (Play/Pause)
- 上一首 (Previous Track)
- 下一首 (Next Track)
- 停止 (Stop)
- 音量增加 (Volume Up)
- 音量減少 (Volume Down)
- 靜音 (Mute)
"""
import threading
from typing import Callable, Optional, Dict
from src.core.logger import logger

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logger.warning("pynput 未安裝，媒體鍵功能無法使用")


class MediaKeyListener:
    """媒體鍵監聽器

    使用 pynput 監聽鍵盤的媒體鍵事件，並觸發對應的回調函數。
    """

    # 媒體鍵映射
    MEDIA_KEY_MAP = {
        keyboard.Key.media_play_pause: 'play_pause',
        keyboard.Key.media_next: 'next',
        keyboard.Key.media_previous: 'previous',
        keyboard.Key.media_volume_up: 'volume_up',
        keyboard.Key.media_volume_down: 'volume_down',
        keyboard.Key.media_volume_mute: 'mute',
    }

    def __init__(self):
        """初始化媒體鍵監聽器"""
        if not PYNPUT_AVAILABLE:
            raise ImportError(
                "pynput 未安裝。請執行: pip install pynput"
            )

        self.listener: Optional[keyboard.Listener] = None
        self.callbacks: Dict[str, Callable[[], None]] = {}
        self._running = False

    def on_media_key(self, key_name: str, callback: Callable[[], None]):
        """註冊媒體鍵回調函數

        Args:
            key_name: 媒體鍵名稱
                     'play_pause', 'next', 'previous',
                     'volume_up', 'volume_down', 'mute'
            callback: 回調函數
        """
        if key_name not in ['play_pause', 'next', 'previous',
                            'volume_up', 'volume_down', 'mute']:
            logger.warning(f"不支援的媒體鍵名稱: {key_name}")
            return

        self.callbacks[key_name] = callback
        logger.info(f"已註冊媒體鍵回調: {key_name}")

    def _on_press(self, key):
        """鍵盤按下事件處理"""
        try:
            # 檢查是否為媒體鍵
            if key in self.MEDIA_KEY_MAP:
                key_name = self.MEDIA_KEY_MAP[key]

                # 觸發回調
                if key_name in self.callbacks:
                    callback = self.callbacks[key_name]

                    # 在新線程中執行回調，避免阻塞監聽器
                    threading.Thread(
                        target=callback,
                        daemon=True,
                        name=f"MediaKey-{key_name}"
                    ).start()

                    logger.debug(f"媒體鍵觸發: {key_name}")

        except Exception as e:
            logger.error(f"媒體鍵處理失敗: {e}")

    def start(self):
        """啟動媒體鍵監聽"""
        if self._running:
            logger.warning("媒體鍵監聽器已經在運行")
            return

        try:
            # 創建鍵盤監聽器
            self.listener = keyboard.Listener(on_press=self._on_press)
            self.listener.start()
            self._running = True

            logger.info("媒體鍵監聽器已啟動")

        except Exception as e:
            logger.error(f"啟動媒體鍵監聽器失敗: {e}")
            self._running = False

    def stop(self):
        """停止媒體鍵監聽"""
        if not self._running:
            return

        try:
            if self.listener:
                self.listener.stop()
                self.listener = None

            self._running = False
            logger.info("媒體鍵監聽器已停止")

        except Exception as e:
            logger.error(f"停止媒體鍵監聽器失敗: {e}")

    def is_running(self) -> bool:
        """檢查監聽器是否運行中

        Returns:
            bool: 運行中返回 True
        """
        return self._running

    def clear_callbacks(self):
        """清除所有回調函數"""
        self.callbacks.clear()
        logger.info("已清除所有媒體鍵回調")
