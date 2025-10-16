"""
播放記錄管理器測試
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from src.music.managers.play_history_manager import PlayHistoryManager


class TestPlayHistoryManager:
    """PlayHistoryManager 測試類別"""

    @pytest.fixture
    def temp_history_file(self):
        """建立臨時播放記錄檔案"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        # 清理
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def history_manager(self, temp_history_file):
        """建立 PlayHistoryManager 實例"""
        return PlayHistoryManager(history_file=temp_history_file)

    def test_init_with_new_file(self, temp_history_file):
        """測試初始化 - 新檔案"""
        manager = PlayHistoryManager(history_file=temp_history_file)
        assert manager.history_data["recent_plays"] == []
        assert manager.history_data["play_counts"] == {}
        assert manager.history_data["total_plays"] == 0

    def test_init_with_existing_file(self, temp_history_file):
        """測試初始化 - 已存在的檔案"""
        # 先建立有資料的檔案
        test_data = {
            "recent_plays": [
                {
                    "song_id": "song1",
                    "title": "Test Song",
                    "artist": "Test Artist",
                    "category": "Test Category",
                    "played_at": "2025-01-01T12:00:00"
                }
            ],
            "play_counts": {"song1": 5},
            "total_plays": 5
        }
        with open(temp_history_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        # 載入檔案
        manager = PlayHistoryManager(history_file=temp_history_file)
        assert len(manager.history_data["recent_plays"]) == 1
        assert manager.history_data["play_counts"]["song1"] == 5
        assert manager.history_data["total_plays"] == 5

    def test_record_play_new_song(self, history_manager):
        """測試記錄播放 - 新歌曲"""
        song_info = {
            "title": "Test Song",
            "artist": "Test Artist",
            "category": "Pop"
        }

        result = history_manager.record_play("song1", song_info)

        assert result is True
        assert history_manager.get_total_plays() == 1
        assert history_manager.get_play_count("song1") == 1
        assert len(history_manager.get_recent_plays()) == 1

    def test_record_play_existing_song(self, history_manager):
        """測試記錄播放 - 已存在的歌曲"""
        song_info = {
            "title": "Test Song",
            "artist": "Test Artist",
            "category": "Pop"
        }

        # 記錄第一次播放
        history_manager.record_play("song1", song_info)
        # 記錄第二次播放
        history_manager.record_play("song1", song_info)

        assert history_manager.get_total_plays() == 2
        assert history_manager.get_play_count("song1") == 2
        assert len(history_manager.get_recent_plays()) == 2

    def test_record_play_multiple_songs(self, history_manager):
        """測試記錄播放 - 多首歌曲"""
        songs = [
            {"id": "song1", "title": "Song 1", "artist": "Artist 1", "category": "Pop"},
            {"id": "song2", "title": "Song 2", "artist": "Artist 2", "category": "Rock"},
            {"id": "song3", "title": "Song 3", "artist": "Artist 3", "category": "Jazz"}
        ]

        for song in songs:
            history_manager.record_play(song["id"], song)

        assert history_manager.get_total_plays() == 3
        assert len(history_manager.get_recent_plays()) == 3

    def test_get_recent_plays_limit(self, history_manager):
        """測試取得最近播放 - 限制數量"""
        # 記錄 10 次播放
        for i in range(10):
            song_info = {"title": f"Song {i}", "artist": "Artist", "category": "Pop"}
            history_manager.record_play(f"song{i}", song_info)

        # 取得最近 5 筆
        recent = history_manager.get_recent_plays(limit=5)
        assert len(recent) == 5
        # 確認順序 (最新的在前面)
        assert recent[0]["title"] == "Song 9"
        assert recent[4]["title"] == "Song 5"

    def test_get_recent_plays_max_100(self, history_manager):
        """測試最近播放列表最多保留 100 筆"""
        # 記錄 150 次播放
        for i in range(150):
            song_info = {"title": f"Song {i}", "artist": "Artist", "category": "Pop"}
            history_manager.record_play(f"song{i}", song_info)

        # 確認只保留 100 筆
        assert len(history_manager.history_data["recent_plays"]) == 100
        # 確認最舊的記錄被移除
        assert history_manager.history_data["recent_plays"][-1]["title"] == "Song 50"

    def test_get_play_count_new_song(self, history_manager):
        """測試取得播放次數 - 未播放過的歌曲"""
        assert history_manager.get_play_count("nonexistent") == 0

    def test_get_play_count_existing_song(self, history_manager):
        """測試取得播放次數 - 已播放過的歌曲"""
        song_info = {"title": "Test Song", "artist": "Artist", "category": "Pop"}

        # 播放 3 次
        for _ in range(3):
            history_manager.record_play("song1", song_info)

        assert history_manager.get_play_count("song1") == 3

    def test_get_most_played(self, history_manager):
        """測試取得最常播放排行榜"""
        # 建立不同播放次數的歌曲
        songs = [
            ("song1", 5),
            ("song2", 10),
            ("song3", 3),
            ("song4", 8)
        ]

        for song_id, count in songs:
            song_info = {"title": f"Title {song_id}", "artist": "Artist", "category": "Pop"}
            for _ in range(count):
                history_manager.record_play(song_id, song_info)

        most_played = history_manager.get_most_played(limit=3)

        # 確認排序正確
        assert len(most_played) == 3
        assert most_played[0]["song_id"] == "song2"
        assert most_played[0]["play_count"] == 10
        assert most_played[1]["song_id"] == "song4"
        assert most_played[1]["play_count"] == 8
        assert most_played[2]["song_id"] == "song1"
        assert most_played[2]["play_count"] == 5

    def test_get_most_played_empty(self, history_manager):
        """測試取得最常播放排行榜 - 無播放記錄"""
        most_played = history_manager.get_most_played()
        assert most_played == []

    def test_get_total_plays(self, history_manager):
        """測試取得總播放次數"""
        assert history_manager.get_total_plays() == 0

        # 記錄 5 次播放
        song_info = {"title": "Test", "artist": "Artist", "category": "Pop"}
        for i in range(5):
            history_manager.record_play(f"song{i}", song_info)

        assert history_manager.get_total_plays() == 5

    def test_clear_history(self, history_manager):
        """測試清除所有播放記錄"""
        # 先記錄一些播放
        song_info = {"title": "Test", "artist": "Artist", "category": "Pop"}
        history_manager.record_play("song1", song_info)
        history_manager.record_play("song2", song_info)

        # 清除記錄
        result = history_manager.clear_history()

        assert result is True
        assert history_manager.get_total_plays() == 0
        assert len(history_manager.get_recent_plays()) == 0
        assert history_manager.get_play_count("song1") == 0

    def test_clear_recent_plays(self, history_manager):
        """測試清除最近播放列表 (保留播放次數統計)"""
        # 記錄一些播放
        song_info = {"title": "Test", "artist": "Artist", "category": "Pop"}
        for _ in range(3):
            history_manager.record_play("song1", song_info)

        # 清除最近播放列表
        result = history_manager.clear_recent_plays()

        assert result is True
        assert len(history_manager.get_recent_plays()) == 0
        # 播放次數統計應該保留
        assert history_manager.get_play_count("song1") == 3
        assert history_manager.get_total_plays() == 3

    def test_save_and_load_persistence(self, temp_history_file):
        """測試儲存與載入的持久性"""
        # 建立第一個管理器並記錄播放
        manager1 = PlayHistoryManager(history_file=temp_history_file)
        song_info = {"title": "Test", "artist": "Artist", "category": "Pop"}
        manager1.record_play("song1", song_info)

        # 建立第二個管理器載入相同檔案
        manager2 = PlayHistoryManager(history_file=temp_history_file)

        # 確認資料正確載入
        assert manager2.get_total_plays() == 1
        assert manager2.get_play_count("song1") == 1

    def test_record_play_with_timestamp(self, history_manager):
        """測試播放記錄包含時間戳記"""
        song_info = {"title": "Test", "artist": "Artist", "category": "Pop"}
        history_manager.record_play("song1", song_info)

        recent = history_manager.get_recent_plays()[0]
        assert "played_at" in recent

        # 確認時間戳記格式正確
        played_at = datetime.fromisoformat(recent["played_at"])
        assert isinstance(played_at, datetime)
