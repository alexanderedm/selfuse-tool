"""測試歌詞解析器"""
import unittest
from unittest.mock import patch, mock_open
import tempfile
import os
from src.music.utils.lyrics_parser import LyricsParser


class TestLyricsParser(unittest.TestCase):
    """歌詞解析器測試類別"""

    def setUp(self):
        """測試前準備"""
        self.parser = LyricsParser()

    def test_parse_simple_lrc_content(self):
        """測試解析簡單的 LRC 內容"""
        lrc_content = """[00:12.00]第一句歌詞
[00:17.20]第二句歌詞
[00:21.10]第三句歌詞"""

        result = self.parser.parse_lrc_content(lrc_content)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['time'], 12.0)
        self.assertEqual(result[0]['text'], '第一句歌詞')
        self.assertEqual(result[1]['time'], 17.2)
        self.assertEqual(result[1]['text'], '第二句歌詞')
        self.assertEqual(result[2]['time'], 21.1)
        self.assertEqual(result[2]['text'], '第三句歌詞')

    def test_parse_lrc_with_metadata(self):
        """測試解析包含元數據的 LRC"""
        lrc_content = """[ar:歌手名稱]
[ti:歌曲名稱]
[al:專輯名稱]
[by:製作者]
[00:12.00]歌詞開始"""

        result = self.parser.parse_lrc_content(lrc_content)

        # 元數據應該被忽略,只返回歌詞行
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['time'], 12.0)
        self.assertEqual(result[0]['text'], '歌詞開始')

    def test_parse_lrc_with_empty_lines(self):
        """測試解析包含空行的 LRC"""
        lrc_content = """[00:12.00]第一句

[00:17.20]第二句

[00:21.10]第三句"""

        result = self.parser.parse_lrc_content(lrc_content)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['text'], '第一句')
        self.assertEqual(result[1]['text'], '第二句')
        self.assertEqual(result[2]['text'], '第三句')

    def test_parse_lrc_with_milliseconds(self):
        """測試解析精確到毫秒的時間"""
        lrc_content = """[00:12.345]精確時間"""

        result = self.parser.parse_lrc_content(lrc_content)

        self.assertEqual(len(result), 1)
        # 00:12.345 = 12.345 秒
        self.assertAlmostEqual(result[0]['time'], 12.345, places=2)

    def test_parse_lrc_with_minutes(self):
        """測試解析分鐘格式"""
        lrc_content = """[01:30.00]一分三十秒
[02:45.50]兩分四十五秒半"""

        result = self.parser.parse_lrc_content(lrc_content)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['time'], 90.0)  # 1:30 = 90 秒
        self.assertEqual(result[1]['time'], 165.5)  # 2:45.5 = 165.5 秒

    def test_parse_empty_lrc_content(self):
        """測試解析空內容"""
        result = self.parser.parse_lrc_content("")

        self.assertEqual(len(result), 0)

    def test_parse_invalid_lrc_format(self):
        """測試解析無效格式"""
        lrc_content = """這不是正確的 LRC 格式
沒有時間標記
[invalid]格式錯誤"""

        result = self.parser.parse_lrc_content(lrc_content)

        # 無效行應該被忽略
        self.assertEqual(len(result), 0)

    def test_parse_lrc_sorted_by_time(self):
        """測試返回結果按時間排序"""
        lrc_content = """[00:30.00]第二句
[00:10.00]第一句
[00:50.00]第三句"""

        result = self.parser.parse_lrc_content(lrc_content)

        # 應該按時間排序
        self.assertEqual(result[0]['time'], 10.0)
        self.assertEqual(result[1]['time'], 30.0)
        self.assertEqual(result[2]['time'], 50.0)

    def test_parse_lrc_file_not_found(self):
        """測試解析不存在的文件"""
        result = self.parser.parse_lrc_file("/path/to/nonexistent.lrc")

        self.assertIsNone(result)

    def test_parse_lrc_file_success(self):
        """測試解析 LRC 文件成功"""
        # 創建臨時 LRC 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lrc', delete=False, encoding='utf-8') as f:
            f.write("[00:12.00]測試歌詞\n")
            f.write("[00:17.20]第二句\n")
            temp_file = f.name

        try:
            result = self.parser.parse_lrc_file(temp_file)

            self.assertIsNotNone(result)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['text'], '測試歌詞')
        finally:
            # 清理臨時文件
            os.unlink(temp_file)

    def test_get_lyric_at_time_exact_match(self):
        """測試獲取精確時間的歌詞"""
        lyrics = [
            {'time': 10.0, 'text': '第一句'},
            {'time': 20.0, 'text': '第二句'},
            {'time': 30.0, 'text': '第三句'}
        ]

        result = self.parser.get_lyric_at_time(lyrics, 20.0)

        self.assertEqual(result, '第二句')

    def test_get_lyric_at_time_between(self):
        """測試獲取兩個時間點之間的歌詞"""
        lyrics = [
            {'time': 10.0, 'text': '第一句'},
            {'time': 20.0, 'text': '第二句'},
            {'time': 30.0, 'text': '第三句'}
        ]

        # 15 秒時應該顯示第一句(最近的歌詞)
        result = self.parser.get_lyric_at_time(lyrics, 15.0)

        self.assertEqual(result, '第一句')

    def test_get_lyric_at_time_before_first(self):
        """測試在第一句歌詞之前"""
        lyrics = [
            {'time': 10.0, 'text': '第一句'},
            {'time': 20.0, 'text': '第二句'}
        ]

        # 5 秒時還沒有歌詞
        result = self.parser.get_lyric_at_time(lyrics, 5.0)

        self.assertEqual(result, '')

    def test_get_lyric_at_time_after_last(self):
        """測試在最後一句歌詞之後"""
        lyrics = [
            {'time': 10.0, 'text': '第一句'},
            {'time': 20.0, 'text': '第二句'}
        ]

        # 30 秒時應該顯示最後一句
        result = self.parser.get_lyric_at_time(lyrics, 30.0)

        self.assertEqual(result, '第二句')

    def test_get_lyric_at_time_empty_lyrics(self):
        """測試空歌詞列表"""
        result = self.parser.get_lyric_at_time([], 10.0)

        self.assertEqual(result, '')

    def test_get_lyric_index_at_time(self):
        """測試獲取當前歌詞的索引"""
        lyrics = [
            {'time': 10.0, 'text': '第一句'},
            {'time': 20.0, 'text': '第二句'},
            {'time': 30.0, 'text': '第三句'}
        ]

        # 15 秒時應該是索引 0 (第一句)
        index = self.parser.get_lyric_index_at_time(lyrics, 15.0)
        self.assertEqual(index, 0)

        # 25 秒時應該是索引 1 (第二句)
        index = self.parser.get_lyric_index_at_time(lyrics, 25.0)
        self.assertEqual(index, 1)

        # 5 秒時還沒有歌詞,返回 -1
        index = self.parser.get_lyric_index_at_time(lyrics, 5.0)
        self.assertEqual(index, -1)

    def test_parse_lrc_with_special_characters(self):
        """測試解析包含特殊字符的歌詞"""
        lrc_content = """[00:12.00]測試 "引號" 和 '單引號'
[00:17.20]特殊符號 @#$%^&*()
[00:21.10]中英混合 English & 中文"""

        result = self.parser.parse_lrc_content(lrc_content)

        self.assertEqual(len(result), 3)
        self.assertIn('"引號"', result[0]['text'])
        self.assertIn('@#$%^&*()', result[1]['text'])
        self.assertIn('English', result[2]['text'])


if __name__ == '__main__':
    unittest.main()
