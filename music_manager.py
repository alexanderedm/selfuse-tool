"""本地音樂管理模組"""
import os
import json
import glob
from pathlib import Path
from constants import DEFAULT_MUSIC_ROOT_PATH
from logger import logger
from path_utils import normalize_network_path, path_exists_safe, is_network_path


class MusicManager:
    """管理本地音樂的類別"""

    def __init__(self, config_manager, music_root_path=None):
        """初始化音樂管理器

        Args:
            config_manager: 設定管理器實例
            music_root_path (str): 音樂根目錄路徑
        """
        self.config_manager = config_manager
        raw_path = music_root_path or self.config_manager.config.get('music_root_path', DEFAULT_MUSIC_ROOT_PATH)
        # 標準化網路路徑 (將 Z: 轉換為 UNC 格式)
        self.music_root_path = normalize_network_path(raw_path)
        self.categories = {}  # 分類字典 {category_name: [song_list]}
        self.all_songs = []  # 所有歌曲列表

    def set_music_root_path(self, path):
        """設定音樂根目錄

        Args:
            path (str): 音樂根目錄路徑
        """
        # 標準化網路路徑
        normalized_path = normalize_network_path(path)
        self.music_root_path = normalized_path
        # 儲存標準化後的路徑到配置
        self.config_manager.config['music_root_path'] = normalized_path
        self.config_manager.save_config()

    def get_music_root_path(self):
        """取得音樂根目錄

        Returns:
            str: 音樂根目錄路徑
        """
        return self.music_root_path

    def scan_music_library(self):
        """掃描音樂庫,讀取所有分類和歌曲

        Returns:
            dict: {'success': bool, 'categories': dict, 'message': str}
        """
        try:
            # 使用安全的路徑檢查函數,支援網路路徑
            if not path_exists_safe(self.music_root_path):
                # 如果是網路路徑,提供更友善的錯誤訊息
                if is_network_path(self.music_root_path):
                    return {
                        'success': False,
                        'categories': {},
                        'message': f'無法訪問網路音樂目錄: {self.music_root_path}\n請確認網路連線和權限設定'
                    }
                else:
                    return {
                        'success': False,
                        'categories': {},
                        'message': f'音樂目錄不存在: {self.music_root_path}'
                    }

            self.categories = {}
            self.all_songs = []

            # 掃描所有子資料夾作為分類
            for category_dir in os.listdir(self.music_root_path):
                category_path = os.path.join(self.music_root_path, category_dir)

                # 跳過非目錄
                if not os.path.isdir(category_path):
                    continue

                # 讀取該分類下的所有歌曲
                songs = self._scan_category(category_path, category_dir)

                if songs:
                    self.categories[category_dir] = songs
                    self.all_songs.extend(songs)

            return {
                'success': True,
                'categories': self.categories,
                'message': f'成功掃描 {len(self.categories)} 個分類, {len(self.all_songs)} 首歌曲'
            }

        except Exception as e:
            return {
                'success': False,
                'categories': {},
                'message': f'掃描音樂庫時發生錯誤: {str(e)}'
            }

    def _scan_category(self, category_path, category_name):
        """掃描指定分類資料夾

        Args:
            category_path (str): 分類資料夾路徑
            category_name (str): 分類名稱

        Returns:
            list: 歌曲資訊列表
        """
        songs = []

        try:
            # 查找所有 JSON 檔案
            json_files = glob.glob(os.path.join(category_path, '*.json'))

            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        song_data = json.load(f)

                    # 跳過不是字典的 JSON (如陣列)
                    if not isinstance(song_data, dict):
                        continue

                    # 檢查是否有音訊檔案
                    audio_filename = song_data.get('audio_filename')
                    if not audio_filename:
                        continue

                    audio_path = os.path.join(category_path, audio_filename)
                    if not os.path.exists(audio_path):
                        continue

                    # 建立歌曲資訊
                    song_info = {
                        'title': song_data.get('title', '未知歌曲'),
                        'id': song_data.get('id', ''),
                        'duration': song_data.get('duration', 0),
                        'thumbnail': song_data.get('thumbnail', ''),
                        'webpage_url': song_data.get('webpage_url', ''),
                        'uploader': song_data.get('uploader', '未知'),
                        'audio_path': audio_path,
                        'category': category_name,
                        'json_path': json_file
                    }

                    songs.append(song_info)

                except json.JSONDecodeError as e:
                    logger.warning(f"JSON 解析失敗: {json_file}, 錯誤: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"讀取歌曲元數據失敗: {json_file}, 錯誤: {e}")
                    continue

        except Exception as e:
            logger.error(f"掃描分類資料夾失敗: {category_path}, 錯誤: {e}", exc_info=True)

        return songs

    def get_all_categories(self):
        """取得所有分類

        Returns:
            list: 分類名稱列表
        """
        return list(self.categories.keys())

    def get_songs_by_category(self, category_name):
        """取得指定分類的歌曲列表

        Args:
            category_name (str): 分類名稱

        Returns:
            list: 歌曲列表
        """
        return self.categories.get(category_name, [])

    def get_all_songs(self):
        """取得所有歌曲

        Returns:
            list: 所有歌曲列表
        """
        return self.all_songs

    def search_songs(self, keyword):
        """搜尋歌曲

        Args:
            keyword (str): 搜尋關鍵字

        Returns:
            list: 符合的歌曲列表
        """
        keyword = keyword.lower()
        results = []

        for song in self.all_songs:
            # 搜尋標題、分類和藝術家
            if (keyword in song['title'].lower() or
                keyword in song['category'].lower() or
                keyword in song.get('uploader', '').lower()):
                results.append(song)

        return results

    def get_song_by_id(self, song_id):
        """根據 ID 取得歌曲資訊

        Args:
            song_id (str): 歌曲 ID

        Returns:
            dict: 歌曲資訊,找不到則回傳 None
        """
        for song in self.all_songs:
            if song['id'] == song_id:
                return song
        return None

    def format_duration(self, seconds):
        """格式化時間長度

        Args:
            seconds (int): 秒數

        Returns:
            str: 格式化的時間字串 (mm:ss)
        """
        if not seconds or seconds <= 0:
            return "00:00"

        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
