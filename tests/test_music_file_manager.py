"""MusicFileManager 測試模組"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from music_file_manager import MusicFileManager


class TestMusicFileManager:
    """MusicFileManager 單元測試"""

    @pytest.fixture
    def temp_music_root(self):
        """建立臨時音樂根目錄"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # 清理
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def file_manager(self, temp_music_root):
        """建立 MusicFileManager 實例"""
        return MusicFileManager(temp_music_root)

    @pytest.fixture
    def sample_song(self, temp_music_root):
        """建立範例歌曲檔案"""
        category_path = os.path.join(temp_music_root, "測試分類")
        os.makedirs(category_path, exist_ok=True)

        # 建立音訊檔案
        audio_path = os.path.join(category_path, "test_song.mp3")
        with open(audio_path, "w") as f:
            f.write("dummy audio data")

        # 建立 JSON 檔案
        json_path = os.path.join(category_path, "test_song.json")
        with open(json_path, "w", encoding="utf-8") as f:
            f.write('{"title": "測試歌曲"}')

        return {
            "title": "測試歌曲",
            "category": "測試分類",
            "audio_path": audio_path,
            "json_path": json_path
        }

    def test_init(self, temp_music_root):
        """測試初始化"""
        manager = MusicFileManager(temp_music_root)
        assert manager.music_root_path == temp_music_root

    def test_create_folder_success(self, file_manager, temp_music_root):
        """測試成功建立資料夾"""
        folder_name = "新資料夾"
        result = file_manager.create_folder(folder_name)

        assert result is True
        folder_path = os.path.join(temp_music_root, folder_name)
        assert os.path.exists(folder_path)
        assert os.path.isdir(folder_path)

    def test_create_folder_empty_name(self, file_manager):
        """測試建立空名稱資料夾"""
        result = file_manager.create_folder("")
        assert result is False

    def test_create_folder_whitespace_name(self, file_manager):
        """測試建立空白名稱資料夾"""
        result = file_manager.create_folder("   ")
        assert result is False

    def test_create_folder_already_exists(self, file_manager, temp_music_root):
        """測試建立已存在的資料夾"""
        folder_name = "已存在資料夾"
        folder_path = os.path.join(temp_music_root, folder_name)
        os.makedirs(folder_path)

        result = file_manager.create_folder(folder_name)
        assert result is False

    def test_rename_folder_success(self, file_manager, temp_music_root):
        """測試成功重新命名資料夾"""
        old_name = "舊資料夾"
        new_name = "新資料夾"

        # 建立舊資料夾
        old_path = os.path.join(temp_music_root, old_name)
        os.makedirs(old_path)

        result = file_manager.rename_folder(old_name, new_name)

        assert result is True
        assert not os.path.exists(old_path)
        assert os.path.exists(os.path.join(temp_music_root, new_name))

    def test_rename_folder_empty_new_name(self, file_manager, temp_music_root):
        """測試重新命名為空名稱"""
        old_name = "舊資料夾"
        os.makedirs(os.path.join(temp_music_root, old_name))

        result = file_manager.rename_folder(old_name, "")
        assert result is False

    def test_rename_folder_same_name(self, file_manager, temp_music_root):
        """測試重新命名為相同名稱"""
        folder_name = "資料夾"
        os.makedirs(os.path.join(temp_music_root, folder_name))

        result = file_manager.rename_folder(folder_name, folder_name)
        assert result is False

    def test_rename_folder_not_exists(self, file_manager):
        """測試重新命名不存在的資料夾"""
        result = file_manager.rename_folder("不存在", "新名稱")
        assert result is False

    def test_rename_folder_target_exists(self, file_manager, temp_music_root):
        """測試重新命名為已存在的名稱"""
        old_name = "舊資料夾"
        new_name = "已存在資料夾"

        os.makedirs(os.path.join(temp_music_root, old_name))
        os.makedirs(os.path.join(temp_music_root, new_name))

        result = file_manager.rename_folder(old_name, new_name)
        assert result is False

    def test_delete_folder_success(self, file_manager, temp_music_root):
        """測試成功刪除資料夾"""
        folder_name = "待刪除資料夾"
        folder_path = os.path.join(temp_music_root, folder_name)
        os.makedirs(folder_path)

        # 在資料夾中建立一些檔案
        with open(os.path.join(folder_path, "test.txt"), "w") as f:
            f.write("test")

        result = file_manager.delete_folder(folder_name)

        assert result is True
        assert not os.path.exists(folder_path)

    def test_delete_folder_not_exists(self, file_manager):
        """測試刪除不存在的資料夾"""
        result = file_manager.delete_folder("不存在")
        assert result is False

    def test_delete_song_success(self, file_manager, sample_song):
        """測試成功刪除歌曲"""
        result = file_manager.delete_song(sample_song)

        assert result is True
        assert not os.path.exists(sample_song["audio_path"])
        assert not os.path.exists(sample_song["json_path"])

    def test_delete_song_only_audio(self, file_manager, sample_song):
        """測試刪除只有音訊檔案的歌曲"""
        # 刪除 JSON 檔案
        os.remove(sample_song["json_path"])

        result = file_manager.delete_song(sample_song)

        assert result is True
        assert not os.path.exists(sample_song["audio_path"])

    def test_delete_song_not_exists(self, file_manager, temp_music_root):
        """測試刪除不存在的歌曲"""
        fake_song = {
            "audio_path": os.path.join(temp_music_root, "不存在.mp3"),
            "json_path": os.path.join(temp_music_root, "不存在.json")
        }

        result = file_manager.delete_song(fake_song)
        assert result is False

    def test_move_song_success(self, file_manager, sample_song, temp_music_root):
        """測試成功移動歌曲"""
        target_category = "目標分類"
        os.makedirs(os.path.join(temp_music_root, target_category))

        result = file_manager.move_song(sample_song, target_category)

        assert result is True

        # 檢查檔案已移動到目標分類
        target_audio = os.path.join(temp_music_root, target_category, "test_song.mp3")
        target_json = os.path.join(temp_music_root, target_category, "test_song.json")

        assert os.path.exists(target_audio)
        assert os.path.exists(target_json)
        assert not os.path.exists(sample_song["audio_path"])
        assert not os.path.exists(sample_song["json_path"])

    def test_move_song_target_not_exists(self, file_manager, sample_song):
        """測試移動到不存在的目標分類"""
        result = file_manager.move_song(sample_song, "不存在的分類")
        assert result is False

    def test_move_song_target_file_exists(self, file_manager, sample_song, temp_music_root):
        """測試移動到已存在同名檔案的目標分類"""
        target_category = "目標分類"
        target_path = os.path.join(temp_music_root, target_category)
        os.makedirs(target_path)

        # 在目標分類建立同名檔案
        with open(os.path.join(target_path, "test_song.mp3"), "w") as f:
            f.write("existing file")

        result = file_manager.move_song(sample_song, target_category)
        assert result is False

    def test_move_song_only_audio(self, file_manager, sample_song, temp_music_root):
        """測試移動只有音訊檔案的歌曲"""
        # 刪除 JSON 檔案
        os.remove(sample_song["json_path"])

        target_category = "目標分類"
        os.makedirs(os.path.join(temp_music_root, target_category))

        result = file_manager.move_song(sample_song, target_category)

        assert result is True
        target_audio = os.path.join(temp_music_root, target_category, "test_song.mp3")
        assert os.path.exists(target_audio)

    def test_folder_exists(self, file_manager, temp_music_root):
        """測試檢查資料夾是否存在"""
        folder_name = "測試資料夾"
        os.makedirs(os.path.join(temp_music_root, folder_name))

        assert file_manager.folder_exists(folder_name) is True
        assert file_manager.folder_exists("不存在") is False

    def test_get_folder_path(self, file_manager, temp_music_root):
        """測試取得資料夾路徑"""
        folder_name = "測試資料夾"
        expected_path = os.path.join(temp_music_root, folder_name)

        assert file_manager.get_folder_path(folder_name) == expected_path
