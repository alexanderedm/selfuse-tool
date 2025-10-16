"""測試多來源音樂元數據補全模組"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.music.utils.music_metadata_multi_source import MusicMetadataMultiSource  # noqa: E402


class TestMusicMetadataMultiSourceInit:
    """測試初始化"""

    @patch('music_metadata_multi_source.YTMUSIC_AVAILABLE', True)
    def test_init_default(self):
        """測試預設初始化"""
        fetcher = MusicMetadataMultiSource()
        assert 'itunes' in fetcher.sources
        assert fetcher.timeout == 10

    @patch('music_metadata_multi_source.YTMUSIC_AVAILABLE', True)
    def test_init_custom_sources(self):
        """測試自訂來源"""
        fetcher = MusicMetadataMultiSource(sources=['itunes'])
        assert 'itunes' in fetcher.sources

    def test_init_custom_timeout(self):
        """測試自訂逾時時間"""
        fetcher = MusicMetadataMultiSource(timeout=20)
        assert fetcher.timeout == 20


class TestFetchFromYTMusic:
    """測試從 YouTube Music 抓取"""

    @patch('music_metadata_multi_source.YTMUSIC_AVAILABLE', True)
    @patch('music_metadata_multi_source.YTMusic')
    def test_fetch_success(self, mock_ytmusic_class):
        """測試成功抓取"""
        # Mock YTMusic 回應
        mock_ytmusic = MagicMock()
        mock_ytmusic.search.return_value = [
            {
                'title': 'Test Song',
                'artists': [{'name': 'Test Artist'}],
                'album': {'name': 'Test Album'},
                'thumbnails': [
                    {'url': 'http://example.com/thumb1.jpg', 'width': 60},
                    {'url': 'http://example.com/thumb2.jpg', 'width': 480},
                    {'url': 'http://example.com/thumb3.jpg', 'width': 1280}
                ]
            }
        ]
        mock_ytmusic_class.return_value = mock_ytmusic

        fetcher = MusicMetadataMultiSource()
        result = fetcher._fetch_from_ytmusic('Test Song', 'Test Artist')

        assert result is not None
        assert result['title'] == 'Test Song'
        assert result['artist'] == 'Test Artist'
        assert result['album'] == 'Test Album'
        assert 'thumb3.jpg' in result['thumbnail']  # 應選擇最大的縮圖

    @patch('music_metadata_multi_source.YTMusic')
    def test_fetch_no_results(self, mock_ytmusic_class):
        """測試沒有搜尋結果"""
        mock_ytmusic = MagicMock()
        mock_ytmusic.search.return_value = []
        mock_ytmusic_class.return_value = mock_ytmusic

        fetcher = MusicMetadataMultiSource()
        result = fetcher._fetch_from_ytmusic('NonExistentSong', 'NonExistentArtist')

        assert result is None

    @patch('music_metadata_multi_source.YTMusic')
    def test_fetch_exception(self, mock_ytmusic_class):
        """測試抓取時發生異常"""
        mock_ytmusic_class.side_effect = Exception("Network error")

        fetcher = MusicMetadataMultiSource()
        result = fetcher._fetch_from_ytmusic('Test Song', 'Test Artist')

        assert result is None


class TestFetchFromITunes:
    """測試從 iTunes 抓取"""

    @patch('music_metadata_multi_source.requests.get')
    def test_fetch_success(self, mock_get):
        """測試成功抓取"""
        # Mock iTunes API 回應
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [
                {
                    'trackName': 'Test Song',
                    'artistName': 'Test Artist',
                    'collectionName': 'Test Album',
                    'artworkUrl100': 'http://example.com/artwork100x100bb.jpg'
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        fetcher = MusicMetadataMultiSource()
        result = fetcher._fetch_from_itunes('Test Song', 'Test Artist')

        assert result is not None
        assert result['title'] == 'Test Song'
        assert result['artist'] == 'Test Artist'
        assert result['album'] == 'Test Album'
        assert 'artwork600x600bb.jpg' in result['thumbnail']  # 應轉換成高解析度

    @patch('music_metadata_multi_source.requests.get')
    def test_fetch_no_results(self, mock_get):
        """測試沒有搜尋結果"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'results': []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        fetcher = MusicMetadataMultiSource()
        result = fetcher._fetch_from_itunes('NonExistentSong', 'NonExistentArtist')

        assert result is None


class TestFetchMetadata:
    """測試主要的 fetch_metadata 方法"""

    @patch('music_metadata_multi_source.YTMUSIC_AVAILABLE', True)
    @patch('music_metadata_multi_source.requests.get')
    @patch('music_metadata_multi_source.YTMusic')
    def test_fetch_ytmusic_first(self, mock_ytmusic_class, mock_get):
        """測試優先從 YTMusic 抓取"""
        # Mock YTMusic 成功
        mock_ytmusic = MagicMock()
        mock_ytmusic.search.return_value = [
            {
                'title': 'YTMusic Song',
                'artists': [{'name': 'YTMusic Artist'}],
                'album': {'name': 'YTMusic Album'},
                'thumbnails': [{'url': 'http://example.com/yt.jpg', 'width': 1280}]
            }
        ]
        mock_ytmusic_class.return_value = mock_ytmusic

        fetcher = MusicMetadataMultiSource(sources=['ytmusic', 'itunes'])
        result = fetcher.fetch_metadata('Test Song', 'Test Artist')

        assert result is not None
        assert result['artist'] == 'YTMusic Artist'
        # iTunes 不應該被呼叫
        mock_get.assert_not_called()

    @patch('music_metadata_multi_source.requests.get')
    @patch('music_metadata_multi_source.YTMusic')
    def test_fallback_to_itunes(self, mock_ytmusic_class, mock_get):
        """測試 YTMusic 失敗時回退到 iTunes"""
        # Mock YTMusic 失敗
        mock_ytmusic = MagicMock()
        mock_ytmusic.search.return_value = []
        mock_ytmusic_class.return_value = mock_ytmusic

        # Mock iTunes 成功
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [
                {
                    'trackName': 'iTunes Song',
                    'artistName': 'iTunes Artist',
                    'collectionName': 'iTunes Album',
                    'artworkUrl100': 'http://example.com/itunes.jpg'
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        fetcher = MusicMetadataMultiSource(sources=['ytmusic', 'itunes'])
        result = fetcher.fetch_metadata('Test Song', 'Test Artist')

        assert result is not None
        assert result['artist'] == 'iTunes Artist'

    @patch('music_metadata_multi_source.requests.get')
    @patch('music_metadata_multi_source.YTMusic')
    def test_all_sources_fail(self, mock_ytmusic_class, mock_get):
        """測試所有來源都失敗"""
        # Mock YTMusic 失敗
        mock_ytmusic = MagicMock()
        mock_ytmusic.search.return_value = []
        mock_ytmusic_class.return_value = mock_ytmusic

        # Mock iTunes 失敗
        mock_response = MagicMock()
        mock_response.json.return_value = {'results': []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        fetcher = MusicMetadataMultiSource(sources=['ytmusic', 'itunes'])
        result = fetcher.fetch_metadata('NonExistent', 'NonExistent')

        assert result is None


class TestMergeMetadata:
    """測試合併多個來源的元數據"""

    def test_merge_empty_list(self):
        """測試合併空列表"""
        fetcher = MusicMetadataMultiSource()
        result = fetcher._merge_metadata([])
        assert result is None

    def test_merge_single_source(self):
        """測試合併單一來源"""
        fetcher = MusicMetadataMultiSource()
        metadata = {
            'title': 'Test',
            'artist': 'Artist',
            'thumbnail': 'http://example.com/thumb.jpg'
        }
        result = fetcher._merge_metadata([metadata])
        assert result == metadata

    def test_merge_prefer_ytmusic(self):
        """測試合併時優先使用 YTMusic 的資訊"""
        fetcher = MusicMetadataMultiSource()
        ytmusic_data = {
            'title': 'YTMusic',
            'artist': 'YTMusic Artist',
            'album': 'YTMusic Album',
            'thumbnail': 'http://yt.com/thumb.jpg',
            'source': 'ytmusic'
        }
        itunes_data = {
            'title': 'iTunes',
            'artist': 'iTunes Artist',
            'album': 'iTunes Album',
            'thumbnail': 'http://itunes.com/thumb.jpg',
            'source': 'itunes'
        }

        result = fetcher._merge_metadata([ytmusic_data, itunes_data])

        # 應優先使用 YTMusic 的資訊
        assert result['artist'] == 'YTMusic Artist'
        assert result['source'] == 'ytmusic'


class TestChooseBestThumbnail:
    """測試選擇最佳縮圖"""

    def test_choose_highest_resolution(self):
        """測試選擇最高解析度"""
        fetcher = MusicMetadataMultiSource()
        thumbnails = [
            {'url': 'http://example.com/small.jpg', 'width': 120},
            {'url': 'http://example.com/large.jpg', 'width': 1280},
            {'url': 'http://example.com/medium.jpg', 'width': 480}
        ]

        result = fetcher._choose_best_thumbnail(thumbnails)
        assert 'large.jpg' in result

    def test_choose_from_empty_list(self):
        """測試從空列表選擇"""
        fetcher = MusicMetadataMultiSource()
        result = fetcher._choose_best_thumbnail([])
        assert result is None
