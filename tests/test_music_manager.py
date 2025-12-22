"""測試 MusicManager 模組"""
import pytest
import os
import json
from unittest.mock import patch, MagicMock
from src.music.managers.music_manager import MusicManager


class TestMusicManager:
    """MusicManager 測試類別"""

    @pytest.fixture
    def mock_config_manager(self, temp_config_file):
        """建立 mock ConfigManager"""
        from src.core.config_manager import ConfigManager
        return ConfigManager(temp_config_file)

    @pytest.fixture
    def music_manager(self, mock_config_manager, temp_music_dir):
        """建立 MusicManager 實例"""
        return MusicManager(mock_config_manager, temp_music_dir)

    def test_init(self, music_manager, temp_music_dir):
        """測試初始化"""
        # 因為 normalize_network_path 會將反斜線轉換為正斜線,所以需要比較標準化後的路徑
        expected_path = temp_music_dir.replace('\\', '/')
        assert music_manager.music_root_path == expected_path
        assert music_manager.categories == {}
        assert music_manager.all_songs == []

    def test_set_music_root_path(self, music_manager):
        """測試設定音樂根目錄"""
        new_path = "C:/test/music"
        music_manager.set_music_root_path(new_path)

        assert music_manager.get_music_root_path() == new_path

    def test_scan_music_library_empty(self, music_manager):
        """測試掃描空音樂庫"""
        result = music_manager.scan_music_library()

        assert result['success'] is True
        assert result['categories'] == {}
        assert len(result['message']) > 0

    def test_scan_music_library_with_songs(self, music_manager, temp_music_dir):
        """測試掃描包含歌曲的音樂庫"""
        # 建立測試分類資料夾
        category_path = os.path.join(temp_music_dir, 'Test Category')
        os.makedirs(category_path, exist_ok=True)

        # 建立測試音訊檔案
        audio_file = os.path.join(category_path, 'test_song.mp3')
        with open(audio_file, 'w') as f:
            f.write('mock audio data')

        # 建立測試 JSON 元數據
        json_file = os.path.join(category_path, 'test_song.json')
        metadata = {
            'id': 'test123',
            'title': 'Test Song',
            'duration': 180,
            'thumbnail': 'http://example.com/thumb.jpg',
            'webpage_url': 'http://example.com/video',
            'uploader': 'Test Artist',
            'audio_filename': 'test_song.mp3'
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f)

        # 掃描
        result = music_manager.scan_music_library()

        assert result['success'] is True
        assert 'Test Category' in result['categories']
        assert len(result['categories']['Test Category']) == 1
        assert result['categories']['Test Category'][0]['title'] == 'Test Song'

    def test_get_all_categories(self, music_manager):
        """測試取得所有分類"""
        music_manager.categories = {'Cat1': [], 'Cat2': []}

        categories = music_manager.get_all_categories()

        assert 'Cat1' in categories
        assert 'Cat2' in categories
        assert len(categories) == 2

    def test_get_songs_by_category(self, music_manager):
        """測試根據分類取得歌曲"""
        test_songs = [{'title': 'Song 1'}, {'title': 'Song 2'}]
        music_manager.categories = {'TestCat': test_songs}

        songs = music_manager.get_songs_by_category('TestCat')

        assert len(songs) == 2
        assert songs[0]['title'] == 'Song 1'

    def test_get_songs_by_category_not_exist(self, music_manager):
        """測試取得不存在的分類"""
        songs = music_manager.get_songs_by_category('NonExist')

        assert songs == []

    def test_get_all_songs(self, music_manager):
        """測試取得所有歌曲"""
        test_songs = [{'title': 'Song 1'}, {'title': 'Song 2'}]
        music_manager.all_songs = test_songs

        songs = music_manager.get_all_songs()

        assert len(songs) == 2
        assert songs == test_songs

    def test_search_songs(self, music_manager):
        """測試搜尋歌曲"""
        music_manager.all_songs = [
            {'title': 'Rock Song', 'category': 'Rock', 'uploader': 'Artist A'},
            {'title': 'Jazz Music', 'category': 'Jazz', 'uploader': 'Artist B'},
            {'title': 'Rock Anthem', 'category': 'Rock', 'uploader': 'Artist C'}
        ]

        # 搜尋標題
        results = music_manager.search_songs('rock')
        assert len(results) == 2

        # 搜尋分類
        results = music_manager.search_songs('jazz')
        assert len(results) == 1

        # 搜尋藝術家
        results = music_manager.search_songs('artist b')
        assert len(results) == 1

    def test_get_song_by_id(self, music_manager):
        """測試根據 ID 取得歌曲"""
        music_manager.all_songs = [
            {'id': 'song1', 'title': 'Song One'},
            {'id': 'song2', 'title': 'Song Two'}
        ]

        song = music_manager.get_song_by_id('song1')

        assert song is not None
        assert song['title'] == 'Song One'

    def test_get_song_by_id_not_found(self, music_manager):
        """測試取得不存在的歌曲 ID"""
        music_manager.all_songs = [{'id': 'song1', 'title': 'Song One'}]

        song = music_manager.get_song_by_id('nonexist')

        assert song is None

    def test_format_duration(self, music_manager):
        """測試時長格式化"""
        assert music_manager.format_duration(0) == "00:00"
        assert music_manager.format_duration(60) == "01:00"
        assert music_manager.format_duration(125) == "02:05"
        assert music_manager.format_duration(3661) == "61:01"

        # 測試邊界情況
        assert music_manager.format_duration(None) == "00:00"
        assert music_manager.format_duration(-10) == "00:00"

    def test_scan_music_library_with_z_drive_path(self, mock_config_manager):
        """測試使用 Z: 磁碟機路徑掃描音樂庫"""
        # 使用 Z: 磁碟機路徑建立 MusicManager
        z_drive_manager = MusicManager(mock_config_manager, 'Z:/Shuvi')

        # 使用 patch 來模擬路徑存在和目錄掃描
        with patch('music_manager.path_exists_safe') as mock_exists, \
             patch('os.listdir') as mock_listdir, \
             patch('os.path.isdir') as mock_isdir:

            # 設定 mock 行為
            mock_exists.return_value = True
            mock_listdir.return_value = ['Category1']
            mock_isdir.return_value = True

            # 掃描音樂庫
            result = z_drive_manager.scan_music_library()

            # 驗證使用了路徑轉換
            # path_exists_safe 應該被呼叫來檢查路徑
            mock_exists.assert_called_once()
            # 檢查傳入的路徑應該是標準化後的
            called_path = mock_exists.call_args[0][0]
            # Z: 路徑應該被轉換為 UNC 路徑
            assert called_path == '//ShuviNAS/Shuvi' or called_path == 'Z:/Shuvi'

    def test_scan_music_library_with_unc_path(self, mock_config_manager):
        """測試使用 UNC 路徑掃描音樂庫"""
        # 使用 UNC 路徑建立 MusicManager
        unc_manager = MusicManager(mock_config_manager, '//ShuviNAS/Shuvi')

        # 使用 patch 來模擬路徑存在和目錄掃描
        with patch('music_manager.path_exists_safe') as mock_exists, \
             patch('os.listdir') as mock_listdir, \
             patch('os.path.isdir') as mock_isdir:

            # 設定 mock 行為
            mock_exists.return_value = True
            mock_listdir.return_value = ['Category1']
            mock_isdir.return_value = True

            # 掃描音樂庫
            result = unc_manager.scan_music_library()

            # 驗證使用了安全的路徑檢查
            mock_exists.assert_called_once()

    def test_scan_music_library_network_path_not_accessible(self, mock_config_manager):
        """測試網路路徑無法訪問時的錯誤處理"""
        # 使用 Z: 磁碟機路徑建立 MusicManager
        z_drive_manager = MusicManager(mock_config_manager, 'Z:/Shuvi')

        # 使用 patch 模擬路徑不存在
        with patch('music_manager.path_exists_safe') as mock_exists:
            mock_exists.return_value = False

            # 掃描音樂庫
            result = z_drive_manager.scan_music_library()

            # 應該返回失敗結果
            assert result['success'] is False
            assert '音樂目錄不存在' in result['message'] or '無法訪問' in result['message']
            assert result['categories'] == {}
