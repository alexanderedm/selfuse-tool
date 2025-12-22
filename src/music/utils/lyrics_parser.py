"""LRC 歌詞解析器模組"""
import re
from src.core.logger import logger


class LyricsParser:
    """解析 LRC 格式歌詞文件"""

    def __init__(self):
        """初始化歌詞解析器"""
        # LRC 時間標記格式: [mm:ss.xx] 或 [mm:ss.xxx]
        self.time_pattern = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)$')

    def parse_lrc_content(self, lrc_content):
        """解析 LRC 內容

        Args:
            lrc_content (str): LRC 文件內容

        Returns:
            list: 歌詞列表,每個元素為 {'time': float, 'text': str}
                  按時間排序
        """
        if not lrc_content:
            return []

        lyrics = []
        lines = lrc_content.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 嘗試匹配時間標記
            match = self.time_pattern.match(line)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                milliseconds_str = match.group(3)
                text = match.group(4).strip()

                # 處理毫秒(可能是 2 位或 3 位)
                if len(milliseconds_str) == 2:
                    milliseconds = int(milliseconds_str) * 10
                else:
                    milliseconds = int(milliseconds_str)

                # 計算總秒數
                total_seconds = minutes * 60 + seconds + milliseconds / 1000.0

                lyrics.append({
                    'time': total_seconds,
                    'text': text
                })

        # 按時間排序
        lyrics.sort(key=lambda x: x['time'])

        return lyrics

    def parse_lrc_file(self, lrc_file_path):
        """解析 LRC 文件

        Args:
            lrc_file_path (str): LRC 文件路徑

        Returns:
            list: 歌詞列表,失敗則返回 None
        """
        try:
            with open(lrc_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_lrc_content(content)
        except FileNotFoundError:
            logger.warning(f"LRC 文件不存在: {lrc_file_path}")
            return None
        except Exception as e:
            logger.error(f"解析 LRC 文件失敗: {e}")
            return None

    def get_lyric_at_time(self, lyrics, current_time):
        """根據當前時間獲取應該顯示的歌詞

        Args:
            lyrics (list): 歌詞列表
            current_time (float): 當前播放時間(秒)

        Returns:
            str: 當前應該顯示的歌詞文字
        """
        if not lyrics:
            return ''

        # 找出當前時間之前最近的歌詞
        current_lyric = ''
        for lyric in lyrics:
            if lyric['time'] <= current_time:
                current_lyric = lyric['text']
            else:
                break

        return current_lyric

    def get_lyric_index_at_time(self, lyrics, current_time):
        """根據當前時間獲取歌詞索引

        Args:
            lyrics (list): 歌詞列表
            current_time (float): 當前播放時間(秒)

        Returns:
            int: 當前歌詞的索引,-1 表示還沒有歌詞
        """
        if not lyrics:
            return -1

        # 找出當前時間之前最近的歌詞索引
        current_index = -1
        for i, lyric in enumerate(lyrics):
            if lyric['time'] <= current_time:
                current_index = i
            else:
                break

        return current_index
