"""字幕格式轉換器模組

支援將 VTT、SRT 等字幕格式轉換為 LRC 格式
"""
import re
from logger import logger


class SubtitleConverter:
    """字幕格式轉換器"""

    @staticmethod
    def parse_vtt_timestamp(timestamp):
        """解析 VTT 時間戳記格式 (00:00:00.000)

        Args:
            timestamp (str): VTT 格式時間戳記

        Returns:
            float: 時間（秒）
        """
        # VTT 格式: 00:00:00.000 或 00:00.000
        parts = timestamp.strip().split(':')

        if len(parts) == 3:
            hours, minutes, seconds = parts
        elif len(parts) == 2:
            hours = '0'
            minutes, seconds = parts
        else:
            return 0.0

        seconds_parts = seconds.split('.')
        secs = int(seconds_parts[0])
        millisecs = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0

        total_seconds = int(hours) * 3600 + int(minutes) * 60 + secs + millisecs / 1000.0
        return total_seconds

    @staticmethod
    def parse_srt_timestamp(timestamp):
        """解析 SRT 時間戳記格式 (00:00:00,000)

        Args:
            timestamp (str): SRT 格式時間戳記

        Returns:
            float: 時間（秒）
        """
        # SRT 格式: 00:00:00,000
        time_part = timestamp.strip().replace(',', '.')
        parts = time_part.split(':')

        if len(parts) != 3:
            return 0.0

        hours, minutes, seconds = parts
        seconds_parts = seconds.split('.')
        secs = int(seconds_parts[0])
        millisecs = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0

        total_seconds = int(hours) * 3600 + int(minutes) * 60 + secs + millisecs / 1000.0
        return total_seconds

    @staticmethod
    def seconds_to_lrc_timestamp(seconds):
        """將秒數轉換為 LRC 時間戳記格式 [mm:ss.xx]

        Args:
            seconds (float): 時間（秒）

        Returns:
            str: LRC 格式時間戳記
        """
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"[{minutes:02d}:{remaining_seconds:05.2f}]"

    def vtt_to_lrc(self, vtt_content):
        """將 VTT 字幕轉換為 LRC 格式

        Args:
            vtt_content (str): VTT 字幕內容

        Returns:
            str: LRC 格式字幕內容
        """
        lrc_lines = []

        # VTT 格式示例:
        # WEBVTT
        #
        # 00:00:00.000 --> 00:00:03.000
        # First line of lyrics

        lines = vtt_content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # 檢查是否為時間戳記行
            if '-->' in line:
                # 提取開始時間
                timestamp_match = re.match(r'([\d:.]+)\s*-->\s*([\d:.]+)', line)
                if timestamp_match:
                    start_time_str = timestamp_match.group(1)
                    start_seconds = self.parse_vtt_timestamp(start_time_str)

                    # 取得下一行的歌詞文字
                    i += 1
                    if i < len(lines):
                        lyric_text = lines[i].strip()

                        # 移除 HTML 標籤和格式
                        lyric_text = re.sub(r'<[^>]+>', '', lyric_text)
                        lyric_text = lyric_text.strip()

                        if lyric_text:
                            lrc_timestamp = self.seconds_to_lrc_timestamp(start_seconds)
                            lrc_lines.append(f"{lrc_timestamp}{lyric_text}")

            i += 1

        logger.info(f"VTT 轉 LRC 完成，共 {len(lrc_lines)} 行歌詞")
        return '\n'.join(lrc_lines)

    def srt_to_lrc(self, srt_content):
        """將 SRT 字幕轉換為 LRC 格式

        Args:
            srt_content (str): SRT 字幕內容

        Returns:
            str: LRC 格式字幕內容
        """
        lrc_lines = []

        # SRT 格式示例:
        # 1
        # 00:00:00,000 --> 00:00:03,000
        # First line of lyrics

        lines = srt_content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # 檢查是否為時間戳記行
            if '-->' in line:
                # 提取開始時間
                timestamp_match = re.match(r'([\d:,]+)\s*-->\s*([\d:,]+)', line)
                if timestamp_match:
                    start_time_str = timestamp_match.group(1)
                    start_seconds = self.parse_srt_timestamp(start_time_str)

                    # 取得下一行的歌詞文字
                    i += 1
                    lyric_lines = []
                    while i < len(lines) and lines[i].strip():
                        lyric_text = lines[i].strip()

                        # 移除 HTML 標籤和格式
                        lyric_text = re.sub(r'<[^>]+>', '', lyric_text)
                        lyric_text = lyric_text.strip()

                        if lyric_text and not lyric_text.isdigit():
                            lyric_lines.append(lyric_text)
                        i += 1

                    if lyric_lines:
                        lrc_timestamp = self.seconds_to_lrc_timestamp(start_seconds)
                        combined_text = ' '.join(lyric_lines)
                        lrc_lines.append(f"{lrc_timestamp}{combined_text}")

            i += 1

        logger.info(f"SRT 轉 LRC 完成，共 {len(lrc_lines)} 行歌詞")
        return '\n'.join(lrc_lines)

    def convert_to_lrc(self, subtitle_content, subtitle_format='vtt'):
        """將字幕轉換為 LRC 格式

        Args:
            subtitle_content (str): 字幕內容
            subtitle_format (str): 字幕格式 ('vtt' 或 'srt')

        Returns:
            str: LRC 格式字幕內容，失敗返回 None
        """
        try:
            if subtitle_format.lower() == 'vtt':
                return self.vtt_to_lrc(subtitle_content)
            elif subtitle_format.lower() == 'srt':
                return self.srt_to_lrc(subtitle_content)
            else:
                logger.error(f"不支援的字幕格式: {subtitle_format}")
                return None
        except Exception as e:
            logger.error(f"字幕轉換失敗: {e}")
            return None
