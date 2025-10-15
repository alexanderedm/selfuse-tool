"""音訊播放器模組

基於 sounddevice 的音訊播放器，支援即時音訊處理和等化器。
"""
import threading
import time
from typing import Optional, Callable
import numpy as np
from logger import logger

try:
    import sounddevice as sd
    import librosa
    import soundfile as sf
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    logger.warning("sounddevice 相關套件未安裝，AudioPlayer 無法使用")


class AudioPlayer:
    """基於 sounddevice 的音訊播放器

    功能:
    - 音訊檔案載入和解碼 (支援 MP3, WAV, FLAC, OGG)
    - 播放控制: play(), pause(), resume(), stop()
    - 跳轉控制: seek(position_seconds)
    - 音量控制: set_volume(0.0 - 1.0)
    - 即時音訊處理: 整合 AudioProcessor
    - 播放狀態查詢: is_playing(), is_paused(), get_position(), get_duration()
    - 播放結束回調: on_playback_end
    """

    def __init__(self, audio_processor=None):
        """初始化音訊播放器

        Args:
            audio_processor: AudioProcessor 實例，用於即時音訊處理
        """
        if not SOUNDDEVICE_AVAILABLE:
            raise ImportError(
                "sounddevice, librosa, soundfile 未安裝。"
                "請執行: pip install sounddevice librosa soundfile"
            )

        self.audio_processor = audio_processor
        self.stream = None
        self.audio_data = None  # shape: (frames, channels)
        self.sample_rate = 44100
        self.current_frame = 0
        self._is_playing = False
        self._is_paused = False
        self.volume = 1.0

        # 線程鎖 (保護共享狀態)
        self._lock = threading.Lock()

        # 播放結束回調
        self.on_playback_end: Optional[Callable[[], None]] = None

    def _load_audio(self, file_path: str) -> tuple:
        """載入音訊檔案

        Args:
            file_path: 音訊檔案路徑

        Returns:
            tuple: (audio_data, sample_rate)
                   audio_data shape 為 (frames, channels)

        Raises:
            FileNotFoundError: 檔案不存在
            Exception: 解碼失敗
        """
        try:
            # 優先嘗試使用 soundfile (更快，支援 WAV, FLAC, OGG)
            try:
                audio_data, sample_rate = sf.read(file_path, always_2d=True)
                logger.info(f"使用 soundfile 載入音訊: {file_path}")
            except Exception:
                # 如果失敗，使用 librosa (支援 MP3)
                audio_data, sample_rate = librosa.load(
                    file_path,
                    sr=None,  # 保持原始採樣率
                    mono=False  # 保持立體聲
                )
                # librosa 返回 shape (channels, frames)，需轉置
                if audio_data.ndim == 2:
                    audio_data = audio_data.T
                else:
                    # 單聲道，擴展為 (frames, 1)
                    audio_data = audio_data.reshape(-1, 1)

                logger.info(f"使用 librosa 載入音訊: {file_path}")

            # 確保是 float32 類型
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # 確保是立體聲 (frames, 2)
            if audio_data.shape[1] == 1:
                # 單聲道，複製到兩個通道
                audio_data = np.repeat(audio_data, 2, axis=1)

            logger.info(
                f"音訊載入成功: {audio_data.shape[0]} frames, "
                f"{audio_data.shape[1]} channels, {sample_rate} Hz"
            )

            return audio_data, sample_rate

        except FileNotFoundError:
            logger.error(f"音訊檔案不存在: {file_path}")
            raise
        except Exception as e:
            logger.error(f"載入音訊檔案失敗: {e}")
            raise

    def _audio_callback(self, outdata, frames, time_info, status):
        """sounddevice 回調函數 (在獨立線程執行)

        Args:
            outdata: 輸出緩衝區
            frames: 需要的音訊幀數
            time_info: 時間資訊
            status: 狀態旗標
        """
        if status:
            logger.warning(f"Audio callback status: {status}")

        with self._lock:
            # 檢查是否暫停
            if self._is_paused:
                # 輸出靜音
                outdata[:] = 0
                return

            # 讀取音訊數據
            start = self.current_frame
            end = start + frames

            if end > len(self.audio_data):
                # 播放結束
                chunk = self.audio_data[start:]
                outdata[:len(chunk)] = chunk

                # 填充靜音
                if len(chunk) < frames:
                    outdata[len(chunk):] = 0

                # 標記播放結束
                self._is_playing = False

                # 觸發回調 (在主線程)
                if self.on_playback_end:
                    threading.Thread(
                        target=self._on_playback_end,
                        daemon=True
                    ).start()

                return

            # 取得音訊塊
            chunk = self.audio_data[start:end].copy()

            # 應用音訊處理 (等化器 + 音量)
            if self.audio_processor:
                try:
                    chunk = self.audio_processor.process(chunk)
                except Exception as e:
                    logger.error(f"音訊處理失敗: {e}")

            # 應用音量
            if abs(self.volume - 1.0) > 1e-6:
                chunk = chunk * self.volume

            # 防止削波
            chunk = np.clip(chunk, -1.0, 1.0)

            # 輸出音訊
            outdata[:] = chunk

            # 更新當前幀位置
            self.current_frame = end

    def _on_playback_end(self):
        """播放結束回調 (內部使用)"""
        if self.on_playback_end:
            try:
                self.on_playback_end()
            except Exception as e:
                logger.error(f"播放結束回調執行失敗: {e}")

    def play(self, file_path: str) -> bool:
        """載入並播放音訊檔案

        Args:
            file_path: 音訊檔案路徑

        Returns:
            bool: 成功返回 True，失敗返回 False
        """
        try:
            # 停止當前播放
            self.stop()

            # 載入音訊
            self.audio_data, self.sample_rate = self._load_audio(file_path)
            self.current_frame = 0

            # 建立 sounddevice 串流
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.audio_data.shape[1],
                callback=self._audio_callback,
                blocksize=2048,  # 適中的緩衝區大小
                dtype='float32'
            )

            # 啟動串流
            self.stream.start()

            with self._lock:
                self._is_playing = True
                self._is_paused = False

            logger.info(f"開始播放: {file_path}")
            return True

        except Exception as e:
            logger.error(f"播放失敗: {e}")
            return False

    def pause(self):
        """暫停播放"""
        with self._lock:
            if self._is_playing and not self._is_paused:
                self._is_paused = True
                logger.info("播放已暫停")

    def resume(self):
        """恢復播放"""
        with self._lock:
            if self._is_playing and self._is_paused:
                self._is_paused = False
                logger.info("播放已恢復")

    def stop(self):
        """停止播放"""
        with self._lock:
            if self.stream:
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception as e:
                    logger.error(f"關閉音訊串流失敗: {e}")

                self.stream = None

            self._is_playing = False
            self._is_paused = False
            self.current_frame = 0

            logger.info("播放已停止")

    def seek(self, position_seconds: float):
        """跳轉到指定位置

        Args:
            position_seconds: 跳轉位置 (秒)
        """
        with self._lock:
            if self.audio_data is None:
                return

            # 計算幀位置
            frame = int(position_seconds * self.sample_rate)

            # 限制範圍
            frame = max(0, min(frame, len(self.audio_data)))

            self.current_frame = frame

            logger.info(f"跳轉到位置: {position_seconds:.2f} 秒")

    def set_volume(self, volume: float):
        """設定音量

        Args:
            volume: 音量 (0.0 - 1.0)
        """
        self.volume = max(0.0, min(1.0, float(volume)))

    def get_volume(self) -> float:
        """取得當前音量

        Returns:
            float: 音量 (0.0 - 1.0)
        """
        return self.volume

    def is_playing(self) -> bool:
        """檢查是否正在播放

        Returns:
            bool: 播放中返回 True
        """
        with self._lock:
            return self._is_playing

    def is_paused(self) -> bool:
        """檢查是否暫停

        Returns:
            bool: 暫停返回 True
        """
        with self._lock:
            return self._is_paused

    def get_position(self) -> float:
        """取得當前播放位置

        Returns:
            float: 位置 (秒)
        """
        with self._lock:
            if self.audio_data is None or self.sample_rate == 0:
                return 0.0
            return self.current_frame / self.sample_rate

    def get_duration(self) -> float:
        """取得音訊總時長

        Returns:
            float: 時長 (秒)
        """
        with self._lock:
            if self.audio_data is None or self.sample_rate == 0:
                return 0.0
            return len(self.audio_data) / self.sample_rate
