"""多來源音樂元數據補全模組

整合多個音樂元數據來源（YouTube Music、iTunes、Spotify 等）
提供 fallback 機制確保元數據補全成功率
"""
import logging
from typing import Optional, Dict, List
import requests

try:
    from ytmusicapi import YTMusic
    YTMUSIC_AVAILABLE = True
except ImportError:
    YTMUSIC_AVAILABLE = False
    YTMusic = None

logger = logging.getLogger(__name__)


class MusicMetadataMultiSource:
    """多來源音樂元數據補全器

    支援的來源：
    - YouTube Music (ytmusic)
    - iTunes API (itunes)
    - Spotify API (spotify) - 待實作
    """

    def __init__(self, sources: Optional[List[str]] = None, timeout: int = 10):
        """初始化多來源元數據補全器

        Args:
            sources: 來源列表，按優先級排序
                    預設: ['ytmusic', 'itunes']
            timeout: 請求逾時時間（秒）
        """
        self.sources = sources or ['ytmusic', 'itunes']
        self.timeout = timeout

        if not YTMUSIC_AVAILABLE and 'ytmusic' in self.sources:
            logger.warning("ytmusicapi 套件未安裝，YouTube Music 來源無法使用")
            self.sources.remove('ytmusic')

    def fetch_metadata(
        self,
        song_name: str,
        artist_name: Optional[str] = None
    ) -> Optional[Dict]:
        """從多個來源抓取音樂元數據

        按照優先級順序嘗試各個來源，直到成功為止

        Args:
            song_name: 歌曲名稱
            artist_name: 藝術家名稱（選用）

        Returns:
            Dict: 包含 title, artist, album, thumbnail 的字典
                 如果所有來源都失敗則返回 None
        """
        logger.info(f"從多來源抓取元數據: {song_name} - {artist_name}")

        for source in self.sources:
            try:
                metadata = self._fetch_from_source(source, song_name, artist_name)
                if metadata:
                    metadata['source'] = source
                    logger.info(f"成功從 {source} 抓取元數據")
                    return metadata
            except Exception as e:
                logger.error(f"從 {source} 抓取失敗: {e}")
                continue

        logger.warning(f"所有來源都無法抓取元數據: {song_name}")
        return None

    def _fetch_from_source(
        self,
        source: str,
        song_name: str,
        artist_name: Optional[str]
    ) -> Optional[Dict]:
        """從指定來源抓取元數據

        Args:
            source: 來源名稱 ('ytmusic', 'itunes', 'spotify')
            song_name: 歌曲名稱
            artist_name: 藝術家名稱

        Returns:
            Dict: 元數據字典，失敗返回 None
        """
        if source == 'ytmusic':
            return self._fetch_from_ytmusic(song_name, artist_name)
        elif source == 'itunes':
            return self._fetch_from_itunes(song_name, artist_name)
        elif source == 'spotify':
            return self._fetch_from_spotify(song_name, artist_name)
        else:
            logger.warning(f"不支援的來源: {source}")
            return None

    def _fetch_from_ytmusic(
        self,
        song_name: str,
        artist_name: Optional[str]
    ) -> Optional[Dict]:
        """從 YouTube Music 抓取元數據

        Args:
            song_name: 歌曲名稱
            artist_name: 藝術家名稱

        Returns:
            Dict: 元數據字典，失敗返回 None
        """
        if not YTMUSIC_AVAILABLE:
            return None

        try:
            ytmusic = YTMusic()

            # 建構搜尋查詢
            query = f"{song_name} {artist_name}" if artist_name else song_name

            # 搜尋歌曲
            results = ytmusic.search(query, filter='songs', limit=1)

            if not results:
                return None

            # 取得第一個結果
            result = results[0]

            # 提取元數據
            metadata = {
                'title': result.get('title', song_name),
                'artist': result['artists'][0]['name'] if result.get('artists') else artist_name,
                'album': result['album']['name'] if result.get('album') else None,
                'thumbnail': self._choose_best_thumbnail(result.get('thumbnails', []))
            }

            return metadata

        except Exception as e:
            logger.error(f"YouTube Music 抓取失敗: {e}")
            return None

    def _fetch_from_itunes(
        self,
        song_name: str,
        artist_name: Optional[str]
    ) -> Optional[Dict]:
        """從 iTunes API 抓取元數據

        Args:
            song_name: 歌曲名稱
            artist_name: 藝術家名稱

        Returns:
            Dict: 元數據字典，失敗返回 None
        """
        try:
            # 建構搜尋查詢
            query = f"{song_name} {artist_name}" if artist_name else song_name

            # 呼叫 iTunes Search API
            url = "https://itunes.apple.com/search"
            params = {
                'term': query,
                'media': 'music',
                'entity': 'song',
                'limit': 1
            }

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            results = data.get('results', [])

            if not results:
                return None

            # 取得第一個結果
            result = results[0]

            # 提取元數據並轉換封面為高解析度
            artwork_url = result.get('artworkUrl100', '')
            if artwork_url:
                # 將 100x100 替換成 600x600 獲取高解析度封面
                artwork_url = artwork_url.replace('100x100bb', '600x600bb')
                if '100x100bb' not in result.get('artworkUrl100', ''):
                    artwork_url = artwork_url.replace('100x100', '600x600')

            metadata = {
                'title': result.get('trackName', song_name),
                'artist': result.get('artistName', artist_name),
                'album': result.get('collectionName', None),
                'thumbnail': artwork_url
            }

            return metadata

        except Exception as e:
            logger.error(f"iTunes 抓取失敗: {e}")
            return None

    def _fetch_from_spotify(
        self,
        song_name: str,
        artist_name: Optional[str]
    ) -> Optional[Dict]:
        """從 Spotify API 抓取元數據（待實作）

        Args:
            song_name: 歌曲名稱
            artist_name: 藝術家名稱

        Returns:
            Dict: 元數據字典，失敗返回 None
        """
        # TODO: 實作 Spotify API 整合
        logger.warning("Spotify 來源尚未實作")
        return None

    def _choose_best_thumbnail(self, thumbnails: List[Dict]) -> Optional[str]:
        """從縮圖列表中選擇最高解析度的縮圖

        Args:
            thumbnails: 縮圖列表，每個項目包含 url 和 width/height

        Returns:
            str: 最高解析度縮圖的 URL，如果列表為空則返回 None
        """
        if not thumbnails:
            return None

        # 找出最大寬度的縮圖
        best_thumbnail = max(thumbnails, key=lambda t: t.get('width', 0))
        return best_thumbnail.get('url')

    def _merge_metadata(self, metadata_list: List[Dict]) -> Optional[Dict]:
        """合併多個來源的元數據

        優先使用排序靠前來源的資訊

        Args:
            metadata_list: 元數據列表

        Returns:
            Dict: 合併後的元數據
        """
        if not metadata_list:
            return None

        if len(metadata_list) == 1:
            return metadata_list[0]

        # 使用第一個（優先級最高）作為基礎
        merged = metadata_list[0].copy()

        # 如果某些欄位缺失，從其他來源補充
        for metadata in metadata_list[1:]:
            for key in ['title', 'artist', 'album', 'thumbnail']:
                if not merged.get(key) and metadata.get(key):
                    merged[key] = metadata[key]

        return merged

    def fetch_metadata_from_all_sources(
        self,
        song_name: str,
        artist_name: Optional[str] = None
    ) -> List[Dict]:
        """從所有來源抓取元數據（不使用 fallback）

        用於比較不同來源的結果

        Args:
            song_name: 歌曲名稱
            artist_name: 藝術家名稱

        Returns:
            List[Dict]: 所有來源的元數據列表
        """
        results = []

        for source in self.sources:
            try:
                metadata = self._fetch_from_source(source, song_name, artist_name)
                if metadata:
                    metadata['source'] = source
                    results.append(metadata)
            except Exception as e:
                logger.error(f"從 {source} 抓取失敗: {e}")

        return results
