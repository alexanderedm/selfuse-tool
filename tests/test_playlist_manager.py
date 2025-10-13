"""
播放列表管理器測試
"""

import pytest
import json
import tempfile
from pathlib import Path
from playlist_manager import PlaylistManager


class TestPlaylistManager:
    """PlaylistManager 測試類別"""

    @pytest.fixture
    def temp_playlist_file(self):
        """建立臨時播放列表檔案"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        # 清理
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def playlist_manager(self, temp_playlist_file):
        """建立 PlaylistManager 實例"""
        return PlaylistManager(playlist_file=temp_playlist_file)

    def test_init_with_new_file(self, temp_playlist_file):
        """測試初始化 - 新檔案"""
        manager = PlaylistManager(playlist_file=temp_playlist_file)
        assert manager.playlists == {}

    def test_init_with_existing_file(self, temp_playlist_file):
        """測試初始化 - 已存在的檔案"""
        # 先建立有資料的檔案
        test_data = {
            "My Playlist": {
                "description": "Test Description",
                "songs": ["song1", "song2"],
                "song_count": 2
            }
        }
        with open(temp_playlist_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        # 載入檔案
        manager = PlaylistManager(playlist_file=temp_playlist_file)
        assert "My Playlist" in manager.playlists
        assert manager.playlists["My Playlist"]["song_count"] == 2

    def test_create_playlist(self, playlist_manager):
        """測試建立播放列表"""
        result = playlist_manager.create_playlist("Favorites", "My favorite songs")

        assert result is True
        assert "Favorites" in playlist_manager.playlists
        assert playlist_manager.playlists["Favorites"]["description"] == "My favorite songs"
        assert playlist_manager.playlists["Favorites"]["songs"] == []
        assert playlist_manager.playlists["Favorites"]["song_count"] == 0

    def test_create_playlist_empty_name(self, playlist_manager):
        """測試建立播放列表 - 空名稱"""
        result = playlist_manager.create_playlist("", "Description")
        assert result is False

    def test_create_playlist_duplicate_name(self, playlist_manager):
        """測試建立播放列表 - 重複名稱"""
        playlist_manager.create_playlist("Test", "First")
        result = playlist_manager.create_playlist("Test", "Second")
        assert result is False

    def test_delete_playlist(self, playlist_manager):
        """測試刪除播放列表"""
        playlist_manager.create_playlist("Test", "")
        result = playlist_manager.delete_playlist("Test")

        assert result is True
        assert "Test" not in playlist_manager.playlists

    def test_delete_playlist_not_exist(self, playlist_manager):
        """測試刪除播放列表 - 不存在"""
        result = playlist_manager.delete_playlist("NonExistent")
        assert result is False

    def test_rename_playlist(self, playlist_manager):
        """測試重新命名播放列表"""
        playlist_manager.create_playlist("Old Name", "Description")
        result = playlist_manager.rename_playlist("Old Name", "New Name")

        assert result is True
        assert "Old Name" not in playlist_manager.playlists
        assert "New Name" in playlist_manager.playlists
        assert playlist_manager.playlists["New Name"]["description"] == "Description"

    def test_rename_playlist_not_exist(self, playlist_manager):
        """測試重新命名播放列表 - 不存在"""
        result = playlist_manager.rename_playlist("NonExistent", "New Name")
        assert result is False

    def test_rename_playlist_duplicate_name(self, playlist_manager):
        """測試重新命名播放列表 - 重複名稱"""
        playlist_manager.create_playlist("First", "")
        playlist_manager.create_playlist("Second", "")
        result = playlist_manager.rename_playlist("First", "Second")
        assert result is False

    def test_rename_playlist_empty_name(self, playlist_manager):
        """測試重新命名播放列表 - 空名稱"""
        playlist_manager.create_playlist("Test", "")
        result = playlist_manager.rename_playlist("Test", "")
        assert result is False

    def test_get_all_playlists(self, playlist_manager):
        """測試取得所有播放列表"""
        playlist_manager.create_playlist("Playlist 1", "Description 1")
        playlist_manager.create_playlist("Playlist 2", "Description 2")

        playlists = playlist_manager.get_all_playlists()
        assert len(playlists) == 2
        assert any(p["name"] == "Playlist 1" for p in playlists)
        assert any(p["name"] == "Playlist 2" for p in playlists)

    def test_get_all_playlists_empty(self, playlist_manager):
        """測試取得所有播放列表 - 空列表"""
        playlists = playlist_manager.get_all_playlists()
        assert playlists == []

    def test_get_playlist(self, playlist_manager):
        """測試取得特定播放列表"""
        playlist_manager.create_playlist("Test", "Description")
        playlist = playlist_manager.get_playlist("Test")

        assert playlist is not None
        assert playlist["name"] == "Test"
        assert playlist["description"] == "Description"
        assert playlist["songs"] == []
        assert playlist["song_count"] == 0

    def test_get_playlist_not_exist(self, playlist_manager):
        """測試取得特定播放列表 - 不存在"""
        playlist = playlist_manager.get_playlist("NonExistent")
        assert playlist is None

    def test_add_song(self, playlist_manager):
        """測試加入歌曲到播放列表"""
        playlist_manager.create_playlist("Test", "")
        result = playlist_manager.add_song("Test", "song1")

        assert result is True
        playlist = playlist_manager.get_playlist("Test")
        assert "song1" in playlist["songs"]
        assert playlist["song_count"] == 1

    def test_add_song_multiple(self, playlist_manager):
        """測試加入多首歌曲到播放列表"""
        playlist_manager.create_playlist("Test", "")
        playlist_manager.add_song("Test", "song1")
        playlist_manager.add_song("Test", "song2")
        playlist_manager.add_song("Test", "song3")

        playlist = playlist_manager.get_playlist("Test")
        assert len(playlist["songs"]) == 3
        assert playlist["song_count"] == 3

    def test_add_song_duplicate(self, playlist_manager):
        """測試加入重複歌曲"""
        playlist_manager.create_playlist("Test", "")
        playlist_manager.add_song("Test", "song1")
        result = playlist_manager.add_song("Test", "song1")

        assert result is False
        playlist = playlist_manager.get_playlist("Test")
        assert playlist["song_count"] == 1

    def test_add_song_playlist_not_exist(self, playlist_manager):
        """測試加入歌曲到不存在的播放列表"""
        result = playlist_manager.add_song("NonExistent", "song1")
        assert result is False

    def test_remove_song(self, playlist_manager):
        """測試從播放列表移除歌曲"""
        playlist_manager.create_playlist("Test", "")
        playlist_manager.add_song("Test", "song1")
        result = playlist_manager.remove_song("Test", "song1")

        assert result is True
        playlist = playlist_manager.get_playlist("Test")
        assert "song1" not in playlist["songs"]
        assert playlist["song_count"] == 0

    def test_remove_song_not_exist(self, playlist_manager):
        """測試移除不存在的歌曲"""
        playlist_manager.create_playlist("Test", "")
        result = playlist_manager.remove_song("Test", "song1")
        assert result is False

    def test_remove_song_playlist_not_exist(self, playlist_manager):
        """測試從不存在的播放列表移除歌曲"""
        result = playlist_manager.remove_song("NonExistent", "song1")
        assert result is False

    def test_move_song(self, playlist_manager):
        """測試調整歌曲位置"""
        playlist_manager.create_playlist("Test", "")
        playlist_manager.add_song("Test", "song1")
        playlist_manager.add_song("Test", "song2")
        playlist_manager.add_song("Test", "song3")

        # 將 song1 移到位置 2 (最後)
        result = playlist_manager.move_song("Test", "song1", 2)

        assert result is True
        playlist = playlist_manager.get_playlist("Test")
        assert playlist["songs"] == ["song2", "song3", "song1"]

    def test_move_song_invalid_position(self, playlist_manager):
        """測試調整歌曲位置 - 無效位置"""
        playlist_manager.create_playlist("Test", "")
        playlist_manager.add_song("Test", "song1")

        result = playlist_manager.move_song("Test", "song1", 5)
        assert result is False

    def test_move_song_not_exist(self, playlist_manager):
        """測試調整不存在的歌曲位置"""
        playlist_manager.create_playlist("Test", "")
        result = playlist_manager.move_song("Test", "song1", 0)
        assert result is False

    def test_clear_playlist(self, playlist_manager):
        """測試清空播放列表"""
        playlist_manager.create_playlist("Test", "")
        playlist_manager.add_song("Test", "song1")
        playlist_manager.add_song("Test", "song2")

        result = playlist_manager.clear_playlist("Test")

        assert result is True
        playlist = playlist_manager.get_playlist("Test")
        assert playlist["songs"] == []
        assert playlist["song_count"] == 0

    def test_clear_playlist_not_exist(self, playlist_manager):
        """測試清空不存在的播放列表"""
        result = playlist_manager.clear_playlist("NonExistent")
        assert result is False

    def test_update_description(self, playlist_manager):
        """測試更新播放列表描述"""
        playlist_manager.create_playlist("Test", "Old Description")
        result = playlist_manager.update_description("Test", "New Description")

        assert result is True
        playlist = playlist_manager.get_playlist("Test")
        assert playlist["description"] == "New Description"

    def test_update_description_not_exist(self, playlist_manager):
        """測試更新不存在的播放列表描述"""
        result = playlist_manager.update_description("NonExistent", "Description")
        assert result is False

    def test_save_and_load_persistence(self, temp_playlist_file):
        """測試儲存與載入的持久性"""
        # 建立第一個管理器並創建播放列表
        manager1 = PlaylistManager(playlist_file=temp_playlist_file)
        manager1.create_playlist("Test", "Description")
        manager1.add_song("Test", "song1")
        manager1.add_song("Test", "song2")

        # 建立第二個管理器載入相同檔案
        manager2 = PlaylistManager(playlist_file=temp_playlist_file)

        # 確認資料正確載入
        playlist = manager2.get_playlist("Test")
        assert playlist is not None
        assert playlist["song_count"] == 2
        assert "song1" in playlist["songs"]
        assert "song2" in playlist["songs"]
