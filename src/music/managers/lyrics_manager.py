"""歌詞管理模組

提供歌詞功能：
- 歌詞載入和儲存
- LRC 格式解析
- 同步歌詞滾動
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from src.core.logger import logger


class LyricsManager:
    """歌詞管理器"""

    def __init__(self):
        """初始化歌詞管理器"""
        self.current_lyrics = None
        self.current_song_id = None

    def load_lyrics(self, song_info: Dict) -> Optional[Dict]:
        """載入歌曲歌詞

        Args:
            song_info: 歌曲資訊

        Returns:
            歌詞資料 {
                'plain': 純文字歌詞,
                'synced': 同步歌詞 [(time_ms, line), ...],
                'has_sync': 是否有同步歌詞
            }
        """
        try:
            # 取得歌詞檔案路徑
            audio_path = song_info.get('audio_path')
            if not audio_path:
                return None

            # 尋找 .lrc 檔案
            lrc_path = Path(audio_path).with_suffix('.lrc')

            if not lrc_path.exists():
                logger.debug(f"歌詞檔案不存在: {lrc_path}")
                return None

            # 讀取歌詞檔案
            with open(lrc_path, 'r', encoding='utf-8') as f:
                lrc_content = f.read()

            # 解析歌詞
            lyrics_data = self.parse_lrc(lrc_content)

            self.current_lyrics = lyrics_data
            self.current_song_id = song_info.get('id')

            logger.info(f"載入歌詞: {song_info.get('title')}")
            return lyrics_data

        except Exception as e:
            logger.error(f"載入歌詞失敗: {e}")
            return None

    def parse_lrc(self, lrc_content: str) -> Dict:
        """解析 LRC 格式歌詞

        Args:
            lrc_content: LRC 格式歌詞內容

        Returns:
            解析後的歌詞資料
        """
        # LRC 時間格式: [mm:ss.xx]
        time_pattern = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\]')

        plain_lyrics = []
        synced_lyrics = []
        has_sync = False

        for line in lrc_content.split('\n'):
            line = line.strip()

            if not line:
                continue

            # 尋找時間標記
            time_matches = time_pattern.findall(line)

            if time_matches:
                has_sync = True

                # 取得歌詞文字（移除時間標記）
                lyrics_text = time_pattern.sub('', line).strip()

                # 為每個時間標記創建同步歌詞
                for match in time_matches:
                    minutes = int(match[0])
                    seconds = int(match[1])
                    centiseconds = int(match[2][:2])  # 只取前兩位

                    # 轉換為毫秒
                    time_ms = (minutes * 60 + seconds) * 1000 + centiseconds * 10

                    synced_lyrics.append((time_ms, lyrics_text))
                    plain_lyrics.append(lyrics_text)
            else:
                # 無時間標記的行（可能是元數據）
                if line.startswith('['):
                    # 跳過元數據標記
                    continue
                else:
                    plain_lyrics.append(line)

        # 排序同步歌詞
        synced_lyrics.sort(key=lambda x: x[0])

        return {
            'plain': '\n'.join(plain_lyrics),
            'synced': synced_lyrics if has_sync else None,
            'has_sync': has_sync
        }

    def get_current_lyric_line(self, position_ms: int) -> Optional[str]:
        """取得當前播放位置的歌詞行

        Args:
            position_ms: 當前播放位置（毫秒）

        Returns:
            當前歌詞行
        """
        if not self.current_lyrics or not self.current_lyrics['has_sync']:
            return None

        synced_lyrics = self.current_lyrics['synced']

        # 找到最接近的歌詞行
        for i in range(len(synced_lyrics) - 1, -1, -1):
            time_ms, line = synced_lyrics[i]
            if position_ms >= time_ms:
                return line

        return None

    def get_surrounding_lyrics(self, position_ms: int, before: int = 2, after: int = 2) -> List[Tuple[int, str, bool]]:
        """取得當前位置周圍的歌詞行

        Args:
            position_ms: 當前播放位置（毫秒）
            before: 前面幾行
            after: 後面幾行

        Returns:
            歌詞行列表 [(time_ms, line, is_current), ...]
        """
        if not self.current_lyrics or not self.current_lyrics['has_sync']:
            return []

        synced_lyrics = self.current_lyrics['synced']

        # 找到當前歌詞索引
        current_index = 0
        for i, (time_ms, _) in enumerate(synced_lyrics):
            if position_ms >= time_ms:
                current_index = i
            else:
                break

        # 取得周圍歌詞
        start_index = max(0, current_index - before)
        end_index = min(len(synced_lyrics), current_index + after + 1)

        result = []
        for i in range(start_index, end_index):
            time_ms, line = synced_lyrics[i]
            is_current = (i == current_index)
            result.append((time_ms, line, is_current))

        return result

    def save_lyrics(self, song_info: Dict, lyrics_content: str) -> bool:
        """儲存歌詞到檔案

        Args:
            song_info: 歌曲資訊
            lyrics_content: 歌詞內容

        Returns:
            是否儲存成功
        """
        try:
            audio_path = song_info.get('audio_path')
            if not audio_path:
                return False

            lrc_path = Path(audio_path).with_suffix('.lrc')

            with open(lrc_path, 'w', encoding='utf-8') as f:
                f.write(lyrics_content)

            logger.info(f"儲存歌詞: {lrc_path}")
            return True

        except Exception as e:
            logger.error(f"儲存歌詞失敗: {e}")
            return False

    def has_lyrics(self, song_info: Dict) -> bool:
        """檢查歌曲是否有歌詞檔案

        Args:
            song_info: 歌曲資訊

        Returns:
            是否有歌詞檔案
        """
        audio_path = song_info.get('audio_path')
        if not audio_path:
            return False

        lrc_path = Path(audio_path).with_suffix('.lrc')
        return lrc_path.exists()

    def clear_current_lyrics(self):
        """清除當前歌詞"""
        self.current_lyrics = None
        self.current_song_id = None
