# -*- coding: utf-8 -*-
"""
MusicMetadataFetcher - 音樂元數據自動補全

功能:
- 檢測缺失的音樂資訊 (封面/藝術家/專輯)
- 從多個來源抓取資訊 (YouTube Music, iTunes, Spotify)
- 下載並儲存專輯封面
- 更新歌曲 JSON 元數據檔案
- 背景執行不阻塞 UI
"""

import requests
import json
import threading
from pathlib import Path
from logger import logger
import urllib.parse
from music_metadata_multi_source import MusicMetadataMultiSource


class MusicMetadataFetcher:
    """自動補全音樂元數據"""

    def __init__(self, music_manager, config_manager):
        """初始化

        Args:
            music_manager: MusicManager 實例
            config_manager: ConfigManager 實例
        """
        self.music_manager = music_manager
        self.config_manager = config_manager
        self.enabled = config_manager.get("auto_fetch_metadata", True)
        self.cache_dir = Path("thumbnails")
        self.cache_dir.mkdir(exist_ok=True)
        self.timeout = 10  # API 請求超時時間

        # 初始化多來源元數據補全器 (YouTube Music -> iTunes -> Spotify)
        self.multi_source = MusicMetadataMultiSource(
            sources=['ytmusic', 'itunes'],
            timeout=self.timeout
        )

    def is_enabled(self):
        """檢查功能是否啟用

        Returns:
            bool: 是否啟用
        """
        return self.enabled

    def set_enabled(self, enabled):
        """設定功能啟用狀態

        Args:
            enabled: 是否啟用
        """
        self.enabled = enabled
        self.config_manager.set("auto_fetch_metadata", enabled)

    def check_missing_metadata(self, song):
        """檢查歌曲缺失的元數據

        Args:
            song: 歌曲資料字典

        Returns:
            list: 缺失的欄位列表,例如 ['thumbnail', 'artist', 'album']
        """
        missing = []

        # 檢查縮圖
        thumbnail = song.get("thumbnail", "")
        if not thumbnail or thumbnail == "":
            missing.append("thumbnail")
        else:
            # 檢查檔案是否真的存在
            thumb_path = Path(thumbnail)
            if not thumb_path.exists():
                missing.append("thumbnail")

        # 檢查藝術家
        artist = song.get("artist", "")
        if not artist or artist in ["未知藝術家", "Unknown Artist", ""]:
            missing.append("artist")

        # 檢查專輯
        album = song.get("album", "")
        if not album or album == "":
            missing.append("album")

        return missing

    def fetch_metadata_async(self, song, callback=None):
        """非同步抓取元數據

        Args:
            song: 歌曲資料字典
            callback: 完成後的回調函數 callback(success, metadata)
        """
        def _fetch():
            try:
                missing = self.check_missing_metadata(song)
                if missing:
                    metadata = self.fetch_metadata(song, missing)
                    if callback:
                        callback(True, metadata)
                else:
                    if callback:
                        callback(True, None)
            except Exception as e:
                logger.error(f"非同步抓取元數據失敗: {e}")
                if callback:
                    callback(False, None)

        thread = threading.Thread(target=_fetch, daemon=True)
        thread.start()

    def fetch_metadata(self, song, missing_fields):
        """抓取缺失的元數據 (同步版本)

        Args:
            song: 歌曲資料字典
            missing_fields: 缺失的欄位列表

        Returns:
            dict: 新的元數據,如果失敗返回 None
        """
        # 驗證請求
        if not self._validate_fetch_request(missing_fields):
            return None

        try:
            title = song.get("title", "")
            artist = song.get("artist", "")

            if not title:
                logger.warning("歌曲標題為空,無法抓取元數據")
                return None

            logger.info(f"開始抓取元數據: {title} - {artist}, 缺失: {missing_fields}")

            # 從多來源抓取 (優先 YouTube Music，fallback 到 iTunes)
            metadata = self.multi_source.fetch_metadata(title, artist)

            # 如果多來源失敗，嘗試使用 iTunes (向後相容)
            if not metadata:
                logger.info("多來源抓取失敗，嘗試直接使用 iTunes API")
                metadata = self.fetch_from_itunes(title, artist)

            if metadata:
                # 處理縮圖
                self._process_thumbnail_metadata(metadata, song, missing_fields)

                # 更新歌曲檔案
                return self._apply_and_update_metadata(song, metadata, missing_fields, title)

        except Exception as e:
            logger.error(f"抓取元數據失敗: {e}", exc_info=True)

        return None

    def _validate_fetch_request(self, missing_fields):
        """驗證抓取請求是否有效

        Args:
            missing_fields: 缺失的欄位列表

        Returns:
            bool: 是否有效
        """
        if not self.enabled:
            logger.debug("自動補全功能已停用")
            return False

        if not missing_fields:
            logger.debug("沒有缺失的元數據")
            return False

        return True

    def _process_thumbnail_metadata(self, metadata, song, missing_fields):
        """處理縮圖元數據下載

        Args:
            metadata: 元數據字典 (會被修改)
            song: 歌曲資料字典
            missing_fields: 缺失的欄位列表
        """
        if "thumbnail" not in missing_fields:
            return

        # 優先使用 thumbnail URL (多來源返回)
        thumbnail_url = metadata.get("thumbnail") or metadata.get("artworkUrl")
        if not thumbnail_url:
            return

        cover_path = self.download_cover(
            thumbnail_url,
            song.get("id")
        )

        if cover_path:
            metadata["thumbnail"] = cover_path
        else:
            # 下載失敗,移除 thumbnail 避免寫入無效值
            metadata.pop("thumbnail", None)

    def _apply_and_update_metadata(self, song, metadata, missing_fields, title):
        """應用並更新元數據到歌曲檔案

        Args:
            song: 歌曲資料字典
            metadata: 新的元數據
            missing_fields: 缺失的欄位列表
            title: 歌曲標題

        Returns:
            dict: 元數據如果成功,否則 None
        """
        if self.update_song_metadata(song, metadata, missing_fields):
            logger.info(f"✅ 成功補全元數據: {title}")
            return metadata
        else:
            logger.warning(f"更新 JSON 失敗: {title}")
            return None

    def fetch_from_itunes(self, title, artist=""):
        """從 iTunes Search API 抓取資訊

        Args:
            title: 歌曲標題
            artist: 藝術家名稱 (可選)

        Returns:
            dict: 元數據字典,如果沒找到返回 None
        """
        try:
            # 建構搜尋查詢
            if artist and artist not in ["未知藝術家", "Unknown Artist"]:
                query = f"{artist} {title}"
            else:
                query = title

            # URL 編碼
            query_encoded = urllib.parse.quote(query)

            # API 請求
            url = f"https://itunes.apple.com/search?term={query_encoded}&media=music&limit=1"

            logger.debug(f"iTunes API 請求: {url}")

            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if data.get("resultCount", 0) > 0:
                result = data["results"][0]

                # 使用高解析度封面 (600x600)
                artwork_url = result.get("artworkUrl100", "")
                if artwork_url:
                    artwork_url = artwork_url.replace("100x100bb", "600x600bb")

                metadata = {
                    "title": result.get("trackName"),
                    "artist": result.get("artistName"),
                    "album": result.get("collectionName"),
                    "artworkUrl": artwork_url,
                }

                logger.info(f"iTunes API 找到結果: {metadata.get('artist')} - {metadata.get('title')}")
                return metadata
            else:
                logger.info(f"iTunes API 沒有找到結果: {query}")

        except requests.exceptions.Timeout:
            logger.error(f"iTunes API 請求超時 ({self.timeout}s)")
        except requests.exceptions.RequestException as e:
            logger.error(f"iTunes API 請求失敗: {e}")
        except Exception as e:
            logger.error(f"解析 iTunes API 回應失敗: {e}")

        return None

    def download_cover(self, url, song_id):
        """下載專輯封面

        Args:
            url: 圖片 URL
            song_id: 歌曲 ID

        Returns:
            str: 本地圖片路徑,失敗返回 None
        """
        if not url:
            return None

        try:
            logger.debug(f"開始下載封面: {url}")

            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            # 儲存圖片
            file_path = self.cache_dir / f"{song_id}.jpg"

            with open(file_path, "wb") as f:
                f.write(response.content)

            logger.info(f"✅ 成功下載封面: {file_path}")
            return str(file_path)

        except requests.exceptions.Timeout:
            logger.error(f"下載封面超時 ({self.timeout}s)")
        except requests.exceptions.RequestException as e:
            logger.error(f"下載封面失敗: {e}")
        except Exception as e:
            logger.error(f"儲存封面失敗: {e}")

        return None

    def _validate_song_path(self, song_path):
        """驗證歌曲路徑有效性

        Args:
            song_path: Path 物件

        Returns:
            bool: 路徑是否有效
        """
        if not song_path.name:
            logger.warning(f"無效的歌曲路徑 (路徑名稱為空): {song_path}")
            return False

        if not song_path.exists():
            logger.error(f"歌曲檔案不存在: {song_path}")
            return False

        if not song_path.is_file():
            logger.warning(f"路徑不是檔案: {song_path}")
            return False

        return True

    def _load_or_create_json_data(self, json_path, song, song_path):
        """載入或建立 JSON 資料

        Args:
            json_path: JSON 檔案路徑
            song: 歌曲資料
            song_path: 歌曲檔案路徑

        Returns:
            dict: JSON 資料
        """
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # 如果 JSON 不存在,建立基本結構
            return {
                "id": song.get("id"),
                "title": song.get("title"),
                "path": str(song_path),
            }

    def _update_missing_fields(self, data, new_metadata, missing_fields):
        """更新缺失的欄位

        Args:
            data: 現有資料字典
            new_metadata: 新的元數據
            missing_fields: 缺失的欄位列表

        Returns:
            list: 已更新的欄位列表
        """
        updated_fields = []
        for field in missing_fields:
            if field in new_metadata and new_metadata[field]:
                data[field] = new_metadata[field]
                updated_fields.append(field)
        return updated_fields

    def _write_json_file(self, json_path, data):
        """寫入 JSON 檔案

        Args:
            json_path: JSON 檔案路徑
            data: 要寫入的資料

        Returns:
            bool: 是否成功寫入
        """
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"寫入 JSON 檔案失敗: {e}", exc_info=True)
            return False

    def update_song_metadata(self, song, new_metadata, missing_fields):
        """更新歌曲 JSON 檔案

        Args:
            song: 原始歌曲資料
            new_metadata: 新的元數據
            missing_fields: 缺失的欄位列表 (只更新這些欄位)

        Returns:
            bool: 是否成功更新
        """
        try:
            # 取得並驗證路徑
            song_path = Path(song.get("path", ""))
            if not self._validate_song_path(song_path):
                return False

            json_path = song_path.with_suffix(".json")

            # 載入或建立資料
            data = self._load_or_create_json_data(json_path, song, song_path)

            # 更新缺失的欄位
            updated_fields = self._update_missing_fields(data, new_metadata, missing_fields)

            if not updated_fields:
                logger.debug("沒有欄位需要更新")
                return False

            # 寫入檔案
            if not self._write_json_file(json_path, data):
                return False

            logger.info(f"✅ 更新 JSON: {json_path.name}, 欄位: {updated_fields}")
            return True

        except Exception as e:
            logger.error(f"更新 JSON 檔案失敗: {e}", exc_info=True)
            return False
