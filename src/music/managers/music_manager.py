"""本地音樂管理模組"""
import os
import json
import glob
from pathlib import Path
from threading import Thread, Lock
from src.core.constants import DEFAULT_MUSIC_ROOT_PATH
from src.core.logger import logger
from src.utils.path_utils import normalize_network_path, path_exists_safe, is_network_path


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
        self.song_id_index = {}  # 歌曲 ID 索引 {song_id: song_dict}
        self._lock = Lock()  # 用於執行緒安全
        self._scan_in_progress = False  # 掃描進行中標記

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

            with self._lock:
                self.categories = {}
                self.all_songs = []
                self.song_id_index = {}

            # 掃描所有子資料夾作為分類
            for category_dir in os.listdir(self.music_root_path):
                category_path = os.path.join(self.music_root_path, category_dir)

                # 跳過非目錄
                if not os.path.isdir(category_path):
                    continue

                # 讀取該分類下的所有歌曲
                songs = self._scan_category(category_path, category_dir)

                if songs:
                    with self._lock:
                        self.categories[category_dir] = songs
                        self.all_songs.extend(songs)
                        # 建立歌曲 ID 索引
                        for song in songs:
                            if song.get('id'):
                                self.song_id_index[song['id']] = song

            logger.info(f'成功掃描 {len(self.categories)} 個分類, {len(self.all_songs)} 首歌曲')
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

    def scan_music_library_async(self, callback=None, on_progress=None):
        """異步掃描音樂庫，不會阻塞 UI

        Args:
            callback: 完成時的回調函數 callback(result)
            on_progress: 進度回調函數 on_progress(current, total, message)
        """
        if self._scan_in_progress:
            logger.warning("掃描已在進行中，跳過重複掃描")
            if callback:
                callback({'success': False, 'message': '掃描已在進行中'})
            return

        def _scan_worker():
            """背景執行緒工作函數"""
            self._scan_in_progress = True
            try:
                logger.info("開始異步掃描音樂庫...")
                result = self.scan_music_library()

                if callback:
                    callback(result)

                logger.info("異步掃描完成")
            except Exception as e:
                logger.error(f"異步掃描失敗: {e}", exc_info=True)
                if callback:
                    callback({
                        'success': False,
                        'categories': {},
                        'message': f'異步掃描失敗: {str(e)}'
                    })
            finally:
                self._scan_in_progress = False

        thread = Thread(target=_scan_worker, daemon=True, name="MusicLibraryScanner")
        thread.start()
        logger.info("異步掃描執行緒已啟動")

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
        """根據 ID 取得歌曲資訊（使用索引，O(1) 查詢）

        Args:
            song_id (str): 歌曲 ID

        Returns:
            dict: 歌曲資訊,找不到則回傳 None
        """
        with self._lock:
            return self.song_id_index.get(song_id)

    def _remove_song_from_category(self, category, song_id):
        """從指定分類移除歌曲（輔助方法）"""
        if category not in self.categories:
            return

        self.categories[category] = [
            s for s in self.categories[category] if s['id'] != song_id
        ]

        # 如果分類變空了，刪除該分類
        if not self.categories[category]:
            del self.categories[category]

    def _add_song_to_category(self, category, song):
        """將歌曲添加到指定分類（輔助方法）"""
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(song)

    def _update_song_in_all_songs(self, song_id, updated_song):
        """更新 all_songs 列表中的歌曲（輔助方法）"""
        for i, s in enumerate(self.all_songs):
            if s['id'] == song_id:
                self.all_songs[i] = updated_song
                return True
        return False

    def update_song_category(self, song, new_category):
        """增量更新：移動歌曲到新分類（不重新掃描整個庫）

        Args:
            song (dict): 歌曲資訊
            new_category (str): 新分類名稱

        Returns:
            bool: 是否成功
        """
        try:
            with self._lock:
                old_category = song.get('category')
                song_id = song.get('id')

                if not old_category or not song_id:
                    return False

                # 從舊分類移除
                self._remove_song_from_category(old_category, song_id)

                # 更新歌曲資訊
                song['category'] = new_category

                # 添加到新分類
                self._add_song_to_category(new_category, song)

                # 更新 all_songs 列表中的歌曲引用
                self._update_song_in_all_songs(song_id, song)

                # 更新索引
                self.song_id_index[song_id] = song

                logger.info(f"歌曲 '{song['title']}' 已從 '{old_category}' 移動到 '{new_category}'")
                return True

        except Exception as e:
            logger.error(f"更新歌曲分類失敗: {e}", exc_info=True)
            return False

    def remove_song(self, song):
        """增量更新：移除歌曲（不重新掃描整個庫）

        Args:
            song (dict): 歌曲資訊

        Returns:
            bool: 是否成功
        """
        try:
            with self._lock:
                song_id = song.get('id')
                category = song.get('category')

                if not song_id:
                    return False

                # 從分類移除
                if category:
                    self._remove_song_from_category(category, song_id)

                # 從 all_songs 移除
                self.all_songs = [s for s in self.all_songs if s['id'] != song_id]

                # 從索引移除
                if song_id in self.song_id_index:
                    del self.song_id_index[song_id]

                logger.info(f"歌曲 '{song['title']}' 已從音樂庫移除")
                return True

        except Exception as e:
            logger.error(f"移除歌曲失敗: {e}", exc_info=True)
            return False

    def rename_category(self, old_name, new_name):
        """增量更新：重命名分類（不重新掃描整個庫）

        Args:
            old_name (str): 舊分類名稱
            new_name (str): 新分類名稱

        Returns:
            bool: 是否成功
        """
        try:
            with self._lock:
                if old_name not in self.categories:
                    return False

                # 獲取該分類的所有歌曲
                songs = self.categories[old_name]

                # 更新每首歌的分類資訊
                for song in songs:
                    song['category'] = new_name
                    # 更新 all_songs 中的引用
                    for i, s in enumerate(self.all_songs):
                        if s['id'] == song['id']:
                            self.all_songs[i] = song
                            break
                    # 更新索引
                    if song.get('id'):
                        self.song_id_index[song['id']] = song

                # 重命名分類
                self.categories[new_name] = songs
                del self.categories[old_name]

                logger.info(f"分類 '{old_name}' 已重命名為 '{new_name}'")
                return True

        except Exception as e:
            logger.error(f"重命名分類失敗: {e}", exc_info=True)
            return False

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
