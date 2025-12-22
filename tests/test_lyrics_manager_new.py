"""測試 LyricsManager 歌詞管理器

測試項目：
- LRC 格式解析
- 同步歌詞滾動
- 歌詞載入和儲存
"""
import pytest
from pathlib import Path
from src.music.managers.lyrics_manager import LyricsManager


class TestLyricsManager:
    """測試歌詞管理器"""

    @pytest.fixture
    def manager(self):
        """創建測試用的歌詞管理器"""
        return LyricsManager()

    @pytest.fixture
    def sample_lrc(self):
        """創建測試用的 LRC 歌詞"""
        return """[ti:Test Song]
[ar:Test Artist]
[al:Test Album]
[00:12.00]First line of lyrics
[00:17.20]Second line of lyrics
[00:21.10]Third line of lyrics
[00:24.00][00:28.00]Repeated line
"""

    def test_parse_lrc(self, manager, sample_lrc):
        """測試 LRC 解析"""
        result = manager.parse_lrc(sample_lrc)

        assert result['has_sync'] is True
        assert len(result['synced']) == 5  # 4 unique lines + 1 repeated
        assert result['synced'][0][0] == 12000  # 12 秒 = 12000 毫秒
        assert 'First line of lyrics' in result['plain']

    def test_get_current_lyric_line(self, manager, sample_lrc):
        """測試取得當前歌詞行"""
        lyrics_data = manager.parse_lrc(sample_lrc)
        manager.current_lyrics = lyrics_data

        # 測試不同時間點
        line = manager.get_current_lyric_line(15000)  # 15 秒
        assert line == 'First line of lyrics'

        line = manager.get_current_lyric_line(18000)  # 18 秒
        assert line == 'Second line of lyrics'

    def test_get_surrounding_lyrics(self, manager, sample_lrc):
        """測試取得周圍歌詞"""
        lyrics_data = manager.parse_lrc(sample_lrc)
        manager.current_lyrics = lyrics_data

        # 取得周圍歌詞
        result = manager.get_surrounding_lyrics(18000, before=1, after=1)

        # 應該包含當前行和前後各一行
        assert len(result) >= 2
        assert any(is_current for _, _, is_current in result)

    def test_save_and_load_lyrics(self, manager, tmp_path):
        """測試儲存和載入歌詞"""
        # 創建測試音訊檔案路徑
        audio_path = tmp_path / "test_song.mp3"
        audio_path.touch()

        song_info = {
            'id': 'test123',
            'title': 'Test Song',
            'audio_path': str(audio_path)
        }

        # 儲存歌詞
        lyrics_content = "[00:00.00]Test lyrics"
        result = manager.save_lyrics(song_info, lyrics_content)
        assert result is True

        # 檢查檔案是否存在
        lrc_path = audio_path.with_suffix('.lrc')
        assert lrc_path.exists()

        # 載入歌詞
        loaded = manager.load_lyrics(song_info)
        assert loaded is not None
        assert loaded['has_sync'] is True

    def test_has_lyrics(self, manager, tmp_path):
        """測試檢查歌詞是否存在"""
        audio_path = tmp_path / "test_song.mp3"
        audio_path.touch()

        song_info = {
            'audio_path': str(audio_path)
        }

        # 沒有歌詞
        assert manager.has_lyrics(song_info) is False

        # 創建歌詞檔案
        lrc_path = audio_path.with_suffix('.lrc')
        lrc_path.write_text('[00:00.00]Test', encoding='utf-8')

        # 有歌詞
        assert manager.has_lyrics(song_info) is True

    def test_clear_current_lyrics(self, manager, sample_lrc):
        """測試清除當前歌詞"""
        lyrics_data = manager.parse_lrc(sample_lrc)
        manager.current_lyrics = lyrics_data
        manager.current_song_id = 'test123'

        manager.clear_current_lyrics()

        assert manager.current_lyrics is None
        assert manager.current_song_id is None

    def test_parse_lrc_without_timestamps(self, manager):
        """測試解析沒有時間戳的歌詞"""
        plain_lyrics = """First line
Second line
Third line"""

        result = manager.parse_lrc(plain_lyrics)

        assert result['has_sync'] is False
        assert result['synced'] is None
        assert 'First line' in result['plain']
