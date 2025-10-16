# -*- coding: utf-8 -*-
"""
MusicMetadataFetcher 測試套件

測試音樂元數據自動補全功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
import json
import requests


@pytest.fixture
def mock_music_manager():
    """建立 mock MusicManager"""
    manager = Mock()
    return manager


@pytest.fixture
def mock_config_manager():
    """建立 mock ConfigManager"""
    manager = Mock()
    manager.get.return_value = True
    return manager


@pytest.fixture
def fetcher(mock_music_manager, mock_config_manager, tmp_path):
    """建立測試用的 MusicMetadataFetcher"""
    from src.music.utils.music_metadata_fetcher import MusicMetadataFetcher

    fetcher = MusicMetadataFetcher(mock_music_manager, mock_config_manager)
    fetcher.cache_dir = tmp_path / "thumbnails"
    fetcher.cache_dir.mkdir()

    return fetcher


@pytest.fixture
def sample_song(tmp_path):
    """建立測試用的歌曲資料"""
    song_path = tmp_path / "test_song.mp3"
    song_path.touch()

    return {
        "id": "test123",
        "title": "Test Song",
        "artist": "Test Artist",
        "album": "Test Album",
        "path": str(song_path),
        "thumbnail": str(tmp_path / "thumbnails" / "test123.jpg")
    }


class TestMusicMetadataFetcherInit:
    """初始化測試"""

    def test_init(self, mock_music_manager, mock_config_manager):
        """測試初始化"""
        from src.music.utils.music_metadata_fetcher import MusicMetadataFetcher

        fetcher = MusicMetadataFetcher(mock_music_manager, mock_config_manager)

        assert fetcher.music_manager == mock_music_manager
        assert fetcher.config_manager == mock_config_manager
        assert fetcher.enabled is True
        assert fetcher.cache_dir == Path("thumbnails")
        assert fetcher.timeout == 10

    def test_cache_dir_created(self, fetcher):
        """測試快取目錄會自動建立"""
        assert fetcher.cache_dir.exists()
        assert fetcher.cache_dir.is_dir()


class TestMusicMetadataFetcherEnabled:
    """啟用/停用功能測試"""

    def test_is_enabled_default_true(self, fetcher):
        """測試預設啟用"""
        assert fetcher.is_enabled() is True

    def test_is_enabled_false(self, fetcher):
        """測試停用狀態"""
        fetcher.enabled = False
        assert fetcher.is_enabled() is False

    def test_set_enabled_true(self, fetcher, mock_config_manager):
        """測試設定為啟用"""
        fetcher.set_enabled(True)

        assert fetcher.enabled is True
        mock_config_manager.set.assert_called_once_with("auto_fetch_metadata", True)

    def test_set_enabled_false(self, fetcher, mock_config_manager):
        """測試設定為停用"""
        fetcher.set_enabled(False)

        assert fetcher.enabled is False
        mock_config_manager.set.assert_called_once_with("auto_fetch_metadata", False)


class TestMusicMetadataFetcherCheckMissing:
    """檢查缺失元數據測試"""

    def test_check_missing_metadata_all_complete(self, fetcher, sample_song):
        """測試完整的元數據"""
        # 建立縮圖檔案
        thumbnail_path = Path(sample_song["thumbnail"])
        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        thumbnail_path.touch()

        missing = fetcher.check_missing_metadata(sample_song)

        assert missing == []

    def test_check_missing_metadata_missing_thumbnail(self, fetcher, sample_song):
        """測試缺少縮圖"""
        sample_song["thumbnail"] = ""

        missing = fetcher.check_missing_metadata(sample_song)

        assert "thumbnail" in missing
        assert "artist" not in missing
        assert "album" not in missing

    def test_check_missing_metadata_thumbnail_file_not_exist(self, fetcher, sample_song):
        """測試縮圖欄位有值但檔案不存在"""
        # 不建立實際檔案
        missing = fetcher.check_missing_metadata(sample_song)

        assert "thumbnail" in missing

    def test_check_missing_metadata_missing_artist(self, fetcher, sample_song):
        """測試缺少藝術家"""
        # 建立縮圖
        thumbnail_path = Path(sample_song["thumbnail"])
        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        thumbnail_path.touch()

        sample_song["artist"] = ""

        missing = fetcher.check_missing_metadata(sample_song)

        assert "artist" in missing
        assert "thumbnail" not in missing

    def test_check_missing_metadata_unknown_artist(self, fetcher, sample_song):
        """測試未知藝術家"""
        # 建立縮圖
        thumbnail_path = Path(sample_song["thumbnail"])
        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        thumbnail_path.touch()

        sample_song["artist"] = "未知藝術家"

        missing = fetcher.check_missing_metadata(sample_song)

        assert "artist" in missing

    def test_check_missing_metadata_missing_album(self, fetcher, sample_song):
        """測試缺少專輯"""
        # 建立縮圖
        thumbnail_path = Path(sample_song["thumbnail"])
        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        thumbnail_path.touch()

        sample_song["album"] = ""

        missing = fetcher.check_missing_metadata(sample_song)

        assert "album" in missing

    def test_check_missing_metadata_all_missing(self, fetcher):
        """測試全部缺失"""
        song = {
            "id": "test",
            "title": "Test",
            "artist": "",
            "album": "",
            "thumbnail": ""
        }

        missing = fetcher.check_missing_metadata(song)

        assert "thumbnail" in missing
        assert "artist" in missing
        assert "album" in missing
        assert len(missing) == 3


class TestMusicMetadataFetcherItunesAPI:
    """iTunes API 抓取測試"""

    @patch('requests.get')
    def test_fetch_from_itunes_success(self, mock_get, fetcher):
        """測試 iTunes API 成功"""
        # Mock 回應
        mock_response = Mock()
        mock_response.json.return_value = {
            "resultCount": 1,
            "results": [{
                "trackName": "Test Song",
                "artistName": "Test Artist",
                "collectionName": "Test Album",
                "artworkUrl100": "https://example.com/cover100x100bb.jpg"
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetcher.fetch_from_itunes("Test Song", "Test Artist")

        assert result is not None
        assert result["title"] == "Test Song"
        assert result["artist"] == "Test Artist"
        assert result["album"] == "Test Album"
        assert "600x600bb" in result["artworkUrl"]

        # 驗證 API 呼叫
        mock_get.assert_called_once()
        call_url = mock_get.call_args[0][0]
        assert "Test%20Artist%20Test%20Song" in call_url

    @patch('requests.get')
    def test_fetch_from_itunes_with_artist(self, mock_get, fetcher):
        """測試帶藝術家名稱搜尋"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "resultCount": 1,
            "results": [{
                "trackName": "Song",
                "artistName": "Artist",
                "collectionName": "Album",
                "artworkUrl100": "https://example.com/art.jpg"
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher.fetch_from_itunes("Song", "Artist")

        call_url = mock_get.call_args[0][0]
        assert "Artist%20Song" in call_url

    @patch('requests.get')
    def test_fetch_from_itunes_without_artist(self, mock_get, fetcher):
        """測試不帶藝術家搜尋"""
        mock_response = Mock()
        mock_response.json.return_value = {"resultCount": 0}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher.fetch_from_itunes("Song", "")

        call_url = mock_get.call_args[0][0]
        assert "Song" in call_url
        assert "Artist" not in call_url

    @patch('requests.get')
    def test_fetch_from_itunes_unknown_artist(self, mock_get, fetcher):
        """測試未知藝術家不加入搜尋"""
        mock_response = Mock()
        mock_response.json.return_value = {"resultCount": 0}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher.fetch_from_itunes("Song", "未知藝術家")

        call_url = mock_get.call_args[0][0]
        assert "Song" in call_url
        assert "%E6%9C%AA%E7%9F%A5" not in call_url  # "未知" 的 URL 編碼

    @patch('requests.get')
    def test_fetch_from_itunes_no_results(self, mock_get, fetcher):
        """測試 iTunes API 無結果"""
        mock_response = Mock()
        mock_response.json.return_value = {"resultCount": 0}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetcher.fetch_from_itunes("Nonexistent Song")

        assert result is None

    @patch('requests.get')
    def test_fetch_from_itunes_network_error(self, mock_get, fetcher):
        """測試網路錯誤"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = fetcher.fetch_from_itunes("Test Song")

        assert result is None

    @patch('requests.get')
    def test_fetch_from_itunes_timeout(self, mock_get, fetcher):
        """測試請求超時"""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        result = fetcher.fetch_from_itunes("Test Song")

        assert result is None

    @patch('requests.get')
    def test_fetch_from_itunes_invalid_json(self, mock_get, fetcher):
        """測試無效的 JSON 回應"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetcher.fetch_from_itunes("Test Song")

        assert result is None


class TestMusicMetadataFetcherDownloadCover:
    """下載封面測試"""

    @patch('requests.get')
    def test_download_cover_success(self, mock_get, fetcher):
        """測試成功下載封面"""
        mock_response = Mock()
        mock_response.content = b"fake_image_data"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetcher.download_cover("https://example.com/cover.jpg", "test123")

        assert result is not None
        cover_path = Path(result)
        assert cover_path.exists()
        assert cover_path.name == "test123.jpg"
        assert cover_path.read_bytes() == b"fake_image_data"

    @patch('requests.get')
    def test_download_cover_network_error(self, mock_get, fetcher):
        """測試下載封面網路錯誤"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = fetcher.download_cover("https://example.com/cover.jpg", "test123")

        assert result is None

    @patch('requests.get')
    def test_download_cover_timeout(self, mock_get, fetcher):
        """測試下載封面超時"""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        result = fetcher.download_cover("https://example.com/cover.jpg", "test123")

        assert result is None

    def test_download_cover_empty_url(self, fetcher):
        """測試空 URL"""
        result = fetcher.download_cover("", "test123")

        assert result is None

    def test_download_cover_none_url(self, fetcher):
        """測試 None URL"""
        result = fetcher.download_cover(None, "test123")

        assert result is None


class TestMusicMetadataFetcherUpdateJSON:
    """更新 JSON 測試"""

    def test_update_song_metadata_success(self, fetcher, sample_song, tmp_path):
        """測試成功更新 JSON"""
        # 建立現有 JSON
        json_path = Path(sample_song["path"]).with_suffix(".json")
        existing_data = {
            "id": "test123",
            "title": "Test Song",
            "path": sample_song["path"]
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f)

        new_metadata = {
            "artist": "New Artist",
            "album": "New Album",
            "thumbnail": "thumbnails/test123.jpg"
        }
        missing_fields = ["artist", "album", "thumbnail"]

        result = fetcher.update_song_metadata(sample_song, new_metadata, missing_fields)

        assert result is True

        # 驗證檔案內容
        with open(json_path, "r", encoding="utf-8") as f:
            updated_data = json.load(f)

        assert updated_data["artist"] == "New Artist"
        assert updated_data["album"] == "New Album"
        assert updated_data["thumbnail"] == "thumbnails/test123.jpg"
        assert updated_data["title"] == "Test Song"  # 原有資料保留

    def test_update_song_metadata_create_new_json(self, fetcher, sample_song):
        """測試建立新 JSON"""
        json_path = Path(sample_song["path"]).with_suffix(".json")
        # 確保檔案不存在
        if json_path.exists():
            json_path.unlink()

        new_metadata = {
            "artist": "New Artist",
            "album": "New Album"
        }
        missing_fields = ["artist", "album"]

        result = fetcher.update_song_metadata(sample_song, new_metadata, missing_fields)

        assert result is True
        assert json_path.exists()

        # 驗證內容
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["id"] == "test123"
        assert data["artist"] == "New Artist"
        assert data["album"] == "New Album"

    def test_update_song_metadata_file_not_exist(self, fetcher):
        """測試歌曲檔案不存在"""
        song = {
            "id": "test",
            "title": "Test",
            "path": "E:/nonexistent/song.mp3"
        }
        new_metadata = {"artist": "Artist"}
        missing_fields = ["artist"]

        result = fetcher.update_song_metadata(song, new_metadata, missing_fields)

        assert result is False

    def test_update_song_metadata_only_missing_fields(self, fetcher, sample_song, tmp_path):
        """測試只更新缺失的欄位"""
        json_path = Path(sample_song["path"]).with_suffix(".json")
        existing_data = {
            "id": "test123",
            "title": "Original Title",
            "artist": "Original Artist",
            "path": sample_song["path"]
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f)

        # 新資料包含 title 和 artist,但只有 album 在 missing_fields
        new_metadata = {
            "title": "New Title",
            "artist": "New Artist",
            "album": "New Album"
        }
        missing_fields = ["album"]  # 只更新 album

        result = fetcher.update_song_metadata(sample_song, new_metadata, missing_fields)

        assert result is True

        with open(json_path, "r", encoding="utf-8") as f:
            updated_data = json.load(f)

        assert updated_data["title"] == "Original Title"  # 未更新
        assert updated_data["artist"] == "Original Artist"  # 未更新
        assert updated_data["album"] == "New Album"  # 已更新

    def test_update_song_metadata_no_fields_to_update(self, fetcher, sample_song, tmp_path):
        """測試沒有欄位需要更新"""
        json_path = Path(sample_song["path"]).with_suffix(".json")
        existing_data = {"id": "test123", "title": "Test"}
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f)

        new_metadata = {}
        missing_fields = ["artist"]

        result = fetcher.update_song_metadata(sample_song, new_metadata, missing_fields)

        assert result is False

    def test_update_song_metadata_with_dot_path(self, fetcher, caplog):
        """測試 song_path 是 '.' 時的處理 - Bug 修復

        重現錯誤：
        [2025-10-14 01:56:16] [ERROR] - 更新 JSON 檔案失敗: WindowsPath('.') has an empty name
        ValueError: WindowsPath('.') has an empty name

        修復後應該：
        - 在呼叫 with_suffix() 前驗證路徑
        - 記錄 WARNING 而非 ERROR
        - 優雅地返回 False，不拋出異常
        """
        import logging

        song = {
            "id": "test",
            "title": "Test",
            "path": "."  # WindowsPath('.') name='' -> with_suffix() 會拋出 ValueError
        }
        new_metadata = {"artist": "Artist"}
        missing_fields = ["artist"]

        # 應該優雅地返回 False，不拋出 ValueError
        with caplog.at_level(logging.WARNING):
            result = fetcher.update_song_metadata(song, new_metadata, missing_fields)

        # 驗證結果
        assert result is False

        # 驗證有記錄警告（而非錯誤）
        # 修復後應該看到 WARNING 而非 ERROR with traceback
        assert any("無效" in record.message or "路徑" in record.message
                   for record in caplog.records
                   if record.levelname in ["WARNING", "ERROR"])

    def test_update_song_metadata_with_empty_path(self, fetcher):
        """測試 song_path 是空字串時的處理 - Bug 修復"""
        song = {
            "id": "test",
            "title": "Test",
            "path": ""  # Path('') -> WindowsPath('.')
        }
        new_metadata = {"artist": "Artist"}
        missing_fields = ["artist"]

        # 應該優雅地返回 False，不拋出異常
        result = fetcher.update_song_metadata(song, new_metadata, missing_fields)

        assert result is False

    def test_update_song_metadata_with_directory_path(self, fetcher, tmp_path):
        """測試 song_path 是目錄而非檔案時的處理 - Bug 修復"""
        # 建立一個存在的目錄
        test_dir = tmp_path / "test_directory"
        test_dir.mkdir()

        song = {
            "id": "test",
            "title": "Test",
            "path": str(test_dir)  # 指向目錄，不是檔案
        }
        new_metadata = {"artist": "Artist"}
        missing_fields = ["artist"]

        # 應該優雅地返回 False，不拋出異常
        result = fetcher.update_song_metadata(song, new_metadata, missing_fields)

        assert result is False


class TestMusicMetadataFetcherIntegration:
    """整合測試"""

    @patch('requests.get')
    def test_fetch_metadata_full_flow(self, mock_get, fetcher, sample_song):
        """測試完整流程"""
        # 設定歌曲缺少資訊
        sample_song["artist"] = ""
        sample_song["album"] = ""
        sample_song["thumbnail"] = ""

        # Mock iTunes API
        mock_itunes_response = Mock()
        mock_itunes_response.json.return_value = {
            "resultCount": 1,
            "results": [{
                "trackName": "Test Song",
                "artistName": "Fetched Artist",
                "collectionName": "Fetched Album",
                "artworkUrl100": "https://example.com/cover100x100bb.jpg"
            }]
        }
        mock_itunes_response.raise_for_status = Mock()

        # Mock 封面下載
        mock_cover_response = Mock()
        mock_cover_response.content = b"cover_data"
        mock_cover_response.raise_for_status = Mock()

        mock_get.side_effect = [mock_itunes_response, mock_cover_response]

        missing_fields = fetcher.check_missing_metadata(sample_song)
        result = fetcher.fetch_metadata(sample_song, missing_fields)

        assert result is not None
        assert result["artist"] == "Fetched Artist"
        assert result["album"] == "Fetched Album"
        assert "thumbnail" in result

        # 驗證 JSON 已更新
        json_path = Path(sample_song["path"]).with_suffix(".json")
        assert json_path.exists()

    def test_fetch_metadata_disabled(self, fetcher, sample_song):
        """測試功能停用時"""
        fetcher.enabled = False

        missing_fields = ["artist", "album"]
        result = fetcher.fetch_metadata(sample_song, missing_fields)

        assert result is None

    def test_fetch_metadata_no_missing_fields(self, fetcher, sample_song):
        """測試沒有缺失欄位"""
        missing_fields = []
        result = fetcher.fetch_metadata(sample_song, missing_fields)

        assert result is None

    def test_fetch_metadata_empty_title(self, fetcher, sample_song):
        """測試空標題"""
        sample_song["title"] = ""
        missing_fields = ["artist"]

        result = fetcher.fetch_metadata(sample_song, missing_fields)

        assert result is None


class TestMusicMetadataFetcherAsync:
    """非同步測試"""

    @patch('music_metadata_fetcher.MusicMetadataFetcher.fetch_metadata')
    def test_fetch_metadata_async_success(self, mock_fetch, fetcher, sample_song):
        """測試非同步抓取成功"""
        import threading
        import time

        mock_fetch.return_value = {"artist": "Test"}

        callback_called = threading.Event()
        callback_result = {}

        def callback(success, metadata):
            callback_result["success"] = success
            callback_result["metadata"] = metadata
            callback_called.set()

        fetcher.fetch_metadata_async(sample_song, callback)

        # 等待回調
        assert callback_called.wait(timeout=2)
        assert callback_result["success"] is True
        assert callback_result["metadata"] == {"artist": "Test"}

    @patch('music_metadata_fetcher.MusicMetadataFetcher.fetch_metadata')
    def test_fetch_metadata_async_no_missing(self, mock_fetch, fetcher, sample_song):
        """測試非同步抓取,無缺失欄位"""
        import threading

        # 建立縮圖
        thumbnail_path = Path(sample_song["thumbnail"])
        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        thumbnail_path.touch()

        callback_called = threading.Event()
        callback_result = {}

        def callback(success, metadata):
            callback_result["success"] = success
            callback_result["metadata"] = metadata
            callback_called.set()

        fetcher.fetch_metadata_async(sample_song, callback)

        assert callback_called.wait(timeout=2)
        assert callback_result["success"] is True
        assert callback_result["metadata"] is None

    @patch('music_metadata_fetcher.MusicMetadataFetcher.check_missing_metadata')
    def test_fetch_metadata_async_error(self, mock_check, fetcher, sample_song):
        """測試非同步抓取錯誤"""
        import threading

        mock_check.side_effect = Exception("Test error")

        callback_called = threading.Event()
        callback_result = {}

        def callback(success, metadata):
            callback_result["success"] = success
            callback_result["metadata"] = metadata
            callback_called.set()

        fetcher.fetch_metadata_async(sample_song, callback)

        assert callback_called.wait(timeout=2)
        assert callback_result["success"] is False
        assert callback_result["metadata"] is None
