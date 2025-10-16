"""YouTube Downloader 測試模組"""
import pytest
import os
import json
import subprocess
from unittest.mock import Mock, patch, MagicMock, mock_open
from src.music.utils.youtube_downloader import YouTubeDownloader


class TestYouTubeDownloader:
    """YouTubeDownloader 測試類別"""

    # ==================== 基礎測試 ====================

    def test_initialization(self, tmp_path):
        """測試初始化"""
        downloader = YouTubeDownloader(output_dir=str(tmp_path))
        assert downloader.output_dir == str(tmp_path)
        assert os.path.exists(tmp_path)

    def test_initialization_default_path(self):
        """測試預設路徑初始化"""
        with patch('os.makedirs'):
            downloader = YouTubeDownloader()
            assert downloader.output_dir is not None

    @patch('subprocess.run')
    def test_check_ytdlp_installed_true(self, mock_run):
        """測試 yt-dlp 已安裝"""
        mock_run.return_value = Mock(returncode=0)
        downloader = YouTubeDownloader()
        assert downloader.check_ytdlp_installed() is True
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_check_ytdlp_installed_false(self, mock_run):
        """測試 yt-dlp 未安裝"""
        mock_run.side_effect = FileNotFoundError()
        downloader = YouTubeDownloader()
        assert downloader.check_ytdlp_installed() is False

    # ==================== URL 解析測試 ====================

    def test_extract_video_id_full_url(self):
        """測試解析完整 YouTube URL"""
        downloader = YouTubeDownloader()
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = downloader.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_short_url(self):
        """測試解析短網址"""
        downloader = YouTubeDownloader()
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = downloader.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_embed_url(self):
        """測試解析嵌入 URL"""
        downloader = YouTubeDownloader()
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = downloader.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_music_url(self):
        """測試解析 YouTube Music URL"""
        downloader = YouTubeDownloader()
        url = "https://music.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = downloader.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_invalid_url(self):
        """測試解析無效 URL"""
        downloader = YouTubeDownloader()
        url = "https://invalid-url.com/watch"
        video_id = downloader.extract_video_id(url)
        assert video_id is None

    # ==================== 搜尋功能測試 ====================

    @patch('subprocess.run')
    def test_search_youtube_success(self, mock_run):
        """測試搜尋成功"""
        # Mock 成功的搜尋結果
        mock_output = json.dumps({
            'id': 'test_id_1',
            'title': 'Test Video 1',
            'duration': 180,
            'thumbnail': 'http://example.com/thumb.jpg',
            'webpage_url': 'https://youtube.com/watch?v=test_id_1',
            'uploader': 'Test Channel'
        }) + '\n' + json.dumps({
            'id': 'test_id_2',
            'title': 'Test Video 2',
            'duration': 240,
            'thumbnail': 'http://example.com/thumb2.jpg',
            'webpage_url': 'https://youtube.com/watch?v=test_id_2',
            'uploader': 'Test Channel 2'
        })

        mock_run.return_value = Mock(
            returncode=0,
            stdout=mock_output.encode('utf-8'),
            stderr=b''
        )

        downloader = YouTubeDownloader()
        results = downloader.search_youtube('test query', max_results=2)

        assert len(results) == 2
        assert results[0]['id'] == 'test_id_1'
        assert results[0]['title'] == 'Test Video 1'
        assert results[1]['id'] == 'test_id_2'

    @patch('subprocess.run')
    def test_search_youtube_no_results(self, mock_run):
        """測試搜尋無結果"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=b'',
            stderr=b''
        )

        downloader = YouTubeDownloader()
        results = downloader.search_youtube('nonexistent query')

        assert results == []

    @patch('subprocess.run')
    def test_search_youtube_network_error(self, mock_run):
        """測試搜尋網路錯誤"""
        mock_run.return_value = Mock(
            returncode=1,
            stdout=b'',
            stderr=b'Network error occurred'
        )

        downloader = YouTubeDownloader()
        results = downloader.search_youtube('test query')

        assert results == []

    @patch('subprocess.run')
    def test_search_youtube_json_parse_error(self, mock_run):
        """測試搜尋 JSON 解析錯誤"""
        # Mock 無效的 JSON 輸出
        mock_run.return_value = Mock(
            returncode=0,
            stdout=b'invalid json\n{broken json',
            stderr=b''
        )

        downloader = YouTubeDownloader()
        results = downloader.search_youtube('test query')

        # 應該返回空列表，因為所有 JSON 都無效
        assert results == []

    @patch('subprocess.run')
    def test_search_youtube_timeout(self, mock_run):
        """測試搜尋超時"""
        mock_run.side_effect = subprocess.TimeoutExpired('yt-dlp', 30)

        downloader = YouTubeDownloader()
        results = downloader.search_youtube('test query')

        assert results == []

    # ==================== 下載功能測試 ====================

    @patch('subprocess.run')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_audio_success(self, mock_file, mock_exists, mock_makedirs, mock_run):
        """測試下載成功"""
        # Mock 不存在檔案（需要下載）
        mock_exists.return_value = False

        # Mock 影片資訊查詢成功
        video_info = {
            'id': 'test_id',
            'title': 'Test Video',
            'webpage_url': 'https://youtube.com/watch?v=test_id',
            'duration': 180,
            'thumbnail': 'http://example.com/thumb.jpg',
            'uploader': 'Test Channel',
            'upload_date': '20250101',
            'description': 'Test description'
        }

        def mock_run_side_effect(*args, **kwargs):
            # 第一次呼叫：查詢影片資訊
            if '--dump-json' in args[0]:
                return Mock(
                    returncode=0,
                    stdout=json.dumps(video_info).encode('utf-8'),
                    stderr=b''
                )
            # 第二次呼叫：檢查 cookies（失敗）
            elif '--cookies-from-browser' in args[0] and '--skip-download' in args[0]:
                return Mock(returncode=1)
            # 第三次呼叫：實際下載
            else:
                return Mock(returncode=0, stdout=b'', stderr=b'')

        mock_run.side_effect = mock_run_side_effect

        downloader = YouTubeDownloader()
        result = downloader.download_audio('https://youtube.com/watch?v=test_id')

        assert result['success'] is True
        assert result['message'] == '下載成功'
        assert result['song_info'] is not None
        assert 'metadata' in result['song_info']

    @patch('subprocess.run')
    def test_download_audio_info_failed(self, mock_run):
        """測試下載失敗（無法獲取影片資訊）"""
        mock_run.return_value = Mock(
            returncode=1,
            stdout=b'',
            stderr=b'Video unavailable'
        )

        downloader = YouTubeDownloader()
        result = downloader.download_audio('https://youtube.com/watch?v=invalid_id')

        assert result['success'] is False
        assert '無法獲取影片資訊' in result['message']
        assert result['song_info'] is None

    @patch('subprocess.run')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_download_audio_already_exists(self, mock_exists, mock_makedirs, mock_run):
        """測試檔案已存在"""
        # Mock 檔案已存在
        mock_exists.return_value = True

        # Mock 影片資訊查詢成功
        video_info = {
            'id': 'test_id',
            'title': 'Test Video'
        }
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(video_info).encode('utf-8'),
            stderr=b''
        )

        downloader = YouTubeDownloader()
        result = downloader.download_audio('https://youtube.com/watch?v=test_id')

        assert result['success'] is True
        assert result['message'] == '檔案已存在'
        assert result['song_info'] is not None

    @patch('subprocess.run')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_audio_download_failed(self, mock_file, mock_exists, mock_makedirs, mock_run):
        """測試下載失敗（實際下載失敗）"""
        mock_exists.return_value = False

        video_info = {
            'id': 'test_id',
            'title': 'Test Video',
            'webpage_url': 'https://youtube.com/watch?v=test_id',
            'duration': 180,
            'thumbnail': 'http://example.com/thumb.jpg',
            'uploader': 'Test Channel'
        }

        def mock_run_side_effect(*args, **kwargs):
            # 第一次呼叫：查詢影片資訊（成功）
            if '--dump-json' in args[0]:
                return Mock(
                    returncode=0,
                    stdout=json.dumps(video_info).encode('utf-8'),
                    stderr=b''
                )
            # 第二次呼叫：檢查 cookies（失敗）
            elif '--cookies-from-browser' in args[0] and '--skip-download' in args[0]:
                return Mock(returncode=1)
            # 第三次呼叫：實際下載（失敗）
            else:
                return Mock(
                    returncode=1,
                    stdout=b'',
                    stderr=b'Download failed'
                )

        mock_run.side_effect = mock_run_side_effect

        downloader = YouTubeDownloader()
        result = downloader.download_audio('https://youtube.com/watch?v=test_id')

        assert result['success'] is False
        assert '下載失敗' in result['message']
        assert result['song_info'] is None

    @patch('subprocess.run')
    def test_download_audio_timeout(self, mock_run):
        """測試下載超時"""
        # Mock 影片資訊查詢超時
        mock_run.side_effect = subprocess.TimeoutExpired('yt-dlp', 120)

        downloader = YouTubeDownloader()
        result = downloader.download_audio('https://youtube.com/watch?v=test_id')

        assert result['success'] is False
        assert '超時' in result['message']
        assert result['song_info'] is None

    @patch('subprocess.run')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_audio_with_category(self, mock_file, mock_exists, mock_makedirs, mock_run):
        """測試下載到指定分類"""
        mock_exists.return_value = False

        video_info = {
            'id': 'test_id',
            'title': 'Test Video',
            'webpage_url': 'https://youtube.com/watch?v=test_id',
            'duration': 180,
            'thumbnail': 'http://example.com/thumb.jpg',
            'uploader': 'Test Channel',
            'upload_date': '20250101',
            'description': 'Test description'
        }

        def mock_run_side_effect(*args, **kwargs):
            if '--dump-json' in args[0]:
                return Mock(
                    returncode=0,
                    stdout=json.dumps(video_info).encode('utf-8'),
                    stderr=b''
                )
            elif '--cookies-from-browser' in args[0] and '--skip-download' in args[0]:
                return Mock(returncode=1)
            else:
                return Mock(returncode=0, stdout=b'', stderr=b'')

        mock_run.side_effect = mock_run_side_effect

        downloader = YouTubeDownloader()
        result = downloader.download_audio(
            'https://youtube.com/watch?v=test_id',
            category='測試分類'
        )

        assert result['success'] is True
        # 驗證有呼叫 makedirs 建立分類目錄
        mock_makedirs.assert_called()

    @patch('subprocess.run')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_audio_with_cookies(self, mock_file, mock_exists, mock_makedirs, mock_run):
        """測試使用 cookies 下載"""
        mock_exists.return_value = False

        video_info = {
            'id': 'test_id',
            'title': 'Test Video',
            'webpage_url': 'https://youtube.com/watch?v=test_id',
            'duration': 180,
            'thumbnail': 'http://example.com/thumb.jpg',
            'uploader': 'Test Channel',
            'upload_date': '20250101',
            'description': 'Test description'
        }

        call_count = 0

        def mock_run_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            # 第一次呼叫：查詢影片資訊
            if call_count == 1:
                return Mock(
                    returncode=0,
                    stdout=json.dumps(video_info).encode('utf-8'),
                    stderr=b''
                )
            # 第二次呼叫：測試 chrome cookies（成功）
            elif call_count == 2:
                return Mock(returncode=0)
            # 第三次呼叫：實際下載（帶 cookies）
            else:
                # 驗證有帶 --cookies-from-browser chrome
                if '--cookies-from-browser' in args[0] and 'chrome' in args[0]:
                    return Mock(returncode=0, stdout=b'', stderr=b'')
                return Mock(returncode=0, stdout=b'', stderr=b'')

        mock_run.side_effect = mock_run_side_effect

        downloader = YouTubeDownloader()
        result = downloader.download_audio('https://youtube.com/watch?v=test_id')

        assert result['success'] is True
        # 至少呼叫 3 次（info + cookie test + download）
        assert call_count >= 3
