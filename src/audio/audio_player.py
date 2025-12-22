"""音訊播放器模組

基於 sounddevice 的音訊播放器，支援即時音訊處理和等化器。
"""
import threading
import time
from typing import Optional, Callable
import numpy as np
from src.core.logger import logger

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

        # 淡入淡出設定
        self.fade_in_duration = 1.0  # 秒
        self.fade_out_duration = 1.0  # 秒
        self.fade_enabled = True
        self._fade_in_frames = 0
        self._fade_out_start_frame = 0

        # 播放速度設定
        self.playback_speed = 1.0  # 1.0 = 正常速度
        self._speed_adjustment_enabled = False

        # 睡眠定時器
        self._sleep_timer = None
        self._sleep_timer_thread = None
        self._sleep_timer_active = False

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

            # 應用淡入淡出
            if self.fade_enabled:
                chunk = self._apply_fade(chunk, start)

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

    def _apply_fade(self, chunk, start_frame):
        """應用淡入淡出效果

        Args:
            chunk: 音訊數據塊
            start_frame: 當前塊的起始幀位置

        Returns:
            np.ndarray: 應用淡入淡出後的音訊數據
        """
        frames = len(chunk)
        end_frame = start_frame + frames
        fade_chunk = chunk.copy()

        # 淡入效果
        if start_frame < self._fade_in_frames:
            fade_in_end = min(end_frame, self._fade_in_frames)
            fade_in_length = fade_in_end - start_frame

            if fade_in_length > 0:
                # 線性淡入曲線
                fade_in_curve = np.linspace(
                    start_frame / self._fade_in_frames,
                    fade_in_end / self._fade_in_frames,
                    fade_in_length
                ).reshape(-1, 1)

                # 應用淡入
                fade_chunk[:fade_in_length] *= fade_in_curve

        # 淡出效果
        if end_frame > self._fade_out_start_frame:
            fade_out_start = max(start_frame, self._fade_out_start_frame)
            fade_out_length = end_frame - fade_out_start
            fade_out_offset = fade_out_start - start_frame

            if fade_out_length > 0:
                total_frames = len(self.audio_data)
                fade_out_total = total_frames - self._fade_out_start_frame

                # 線性淡出曲線
                fade_out_curve = np.linspace(
                    1.0 - (fade_out_start - self._fade_out_start_frame) / fade_out_total,
                    1.0 - (end_frame - self._fade_out_start_frame) / fade_out_total,
                    fade_out_length
                ).reshape(-1, 1)

                # 應用淡出
                fade_chunk[fade_out_offset:fade_out_offset + fade_out_length] *= fade_out_curve

        return fade_chunk

    def _adjust_speed(self, audio_data, speed):
        """調整播放速度

        Args:
            audio_data: 音訊數據 (frames, channels)
            speed: 播放速度 (0.5 = 慢速, 1.0 = 正常, 2.0 = 快速)

        Returns:
            np.ndarray: 速度調整後的音訊數據
        """
        try:
            # 分離立體聲通道
            if audio_data.shape[1] == 2:
                left = audio_data[:, 0]
                right = audio_data[:, 1]

                # 使用 librosa 進行時間拉伸（不改變音高）
                left_stretched = librosa.effects.time_stretch(left, rate=speed)
                right_stretched = librosa.effects.time_stretch(right, rate=speed)

                # 合併通道
                stretched = np.column_stack((left_stretched, right_stretched))
            else:
                # 單聲道
                stretched = librosa.effects.time_stretch(audio_data[:, 0], rate=speed)
                stretched = stretched.reshape(-1, 1)

            return stretched.astype(np.float32)

        except Exception as e:
            logger.error(f"播放速度調整失敗: {e}")
            return audio_data

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

            # 應用播放速度調整
            if self._speed_adjustment_enabled and abs(self.playback_speed - 1.0) > 0.01:
                self.audio_data = self._adjust_speed(self.audio_data, self.playback_speed)

            self.current_frame = 0

            # 計算淡入淡出幀位置
            self._fade_in_frames = int(self.fade_in_duration * self.sample_rate)
            total_frames = len(self.audio_data)
            fade_out_frames = int(self.fade_out_duration * self.sample_rate)
            self._fade_out_start_frame = max(0, total_frames - fade_out_frames)

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

    def set_fade_enabled(self, enabled: bool):
        """設定是否啟用淡入淡出效果

        Args:
            enabled: True 為啟用，False 為停用
        """
        self.fade_enabled = enabled
        logger.info(f"淡入淡出效果: {'啟用' if enabled else '停用'}")

    def set_fade_duration(self, fade_in: float = None, fade_out: float = None):
        """設定淡入淡出時長

        Args:
            fade_in: 淡入時長（秒），None 則不改變
            fade_out: 淡出時長（秒），None 則不改變
        """
        if fade_in is not None:
            self.fade_in_duration = max(0.0, float(fade_in))
            logger.info(f"淡入時長設為: {self.fade_in_duration} 秒")

        if fade_out is not None:
            self.fade_out_duration = max(0.0, float(fade_out))
            logger.info(f"淡出時長設為: {self.fade_out_duration} 秒")

    def set_playback_speed(self, speed: float):
        """設定播放速度

        Args:
            speed: 播放速度 (0.5 - 2.0)
                   0.5 = 半速, 1.0 = 正常, 2.0 = 雙速
        """
        speed = max(0.5, min(2.0, float(speed)))
        self.playback_speed = speed
        logger.info(f"播放速度設為: {speed}x")

    def enable_speed_adjustment(self, enabled: bool):
        """啟用/停用播放速度調整功能

        Args:
            enabled: True 為啟用，False 為停用

        注意: 速度調整會在載入音訊時進行處理，
              啟用此功能可能會增加載入時間
        """
        self._speed_adjustment_enabled = enabled
        logger.info(f"播放速度調整: {'啟用' if enabled else '停用'}")

    def get_playback_speed(self) -> float:
        """取得當前播放速度

        Returns:
            float: 播放速度
        """
        return self.playback_speed

    def _sleep_timer_worker(self, duration_seconds: float):
        """睡眠定時器工作線程

        Args:
            duration_seconds: 倒數時間（秒）
        """
        try:
            self._sleep_timer_active = True
            start_time = time.time()
            target_time = start_time + duration_seconds

            while self._sleep_timer_active:
                remaining = target_time - time.time()

                if remaining <= 0:
                    # 時間到，停止播放
                    logger.info("睡眠定時器時間到，停止播放")
                    self.stop()
                    break

                # 每 0.1 秒檢查一次
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"睡眠定時器執行失敗: {e}")
        finally:
            self._sleep_timer_active = False
            self._sleep_timer = None

    def set_sleep_timer(self, minutes: float) -> bool:
        """設定睡眠定時器

        Args:
            minutes: 倒數時間（分鐘）

        Returns:
            bool: 設定成功返回 True
        """
        try:
            # 取消現有的定時器
            self.cancel_sleep_timer()

            if minutes <= 0:
                logger.warning("睡眠定時器時間必須大於 0")
                return False

            duration_seconds = minutes * 60
            self._sleep_timer = time.time() + duration_seconds

            # 啟動定時器線程
            self._sleep_timer_thread = threading.Thread(
                target=self._sleep_timer_worker,
                args=(duration_seconds,),
                daemon=True,
                name="SleepTimer"
            )
            self._sleep_timer_thread.start()

            logger.info(f"睡眠定時器已設定: {minutes} 分鐘")
            return True

        except Exception as e:
            logger.error(f"設定睡眠定時器失敗: {e}")
            return False

    def cancel_sleep_timer(self):
        """取消睡眠定時器"""
        if self._sleep_timer_active:
            self._sleep_timer_active = False
            self._sleep_timer = None
            logger.info("睡眠定時器已取消")

    def get_sleep_timer_remaining(self) -> float:
        """取得睡眠定時器剩餘時間

        Returns:
            float: 剩餘時間（分鐘），0 表示未設定或已過期
        """
        if not self._sleep_timer_active or self._sleep_timer is None:
            return 0.0

        remaining_seconds = max(0, self._sleep_timer - time.time())
        return remaining_seconds / 60.0

    def has_sleep_timer(self) -> bool:
        """檢查是否有啟用的睡眠定時器

        Returns:
            bool: 有啟用的定時器返回 True
        """
        return self._sleep_timer_active
