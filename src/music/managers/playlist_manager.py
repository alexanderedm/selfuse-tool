"""
播放列表管理模組
管理自訂播放列表的建立、刪除、重新命名、歌曲管理等功能
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PlaylistManager:
    """播放列表管理器"""

    def __init__(self, playlist_file: str = "playlists.json"):
        """
        初始化播放列表管理器

        Args:
            playlist_file: 播放列表檔案路徑
        """
        self.playlist_file = Path(playlist_file)
        self.playlists = self._load_playlists()
        logger.info(f"播放列表管理器已初始化,檔案: {playlist_file}")

    def _load_playlists(self) -> Dict:
        """載入播放列表"""
        if not self.playlist_file.exists():
            return {}

        try:
            with open(self.playlist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"成功載入播放列表,共 {len(data)} 個列表")
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"載入播放列表失敗: {e}", exc_info=True)
            return {}

    def _save_playlists(self) -> bool:
        """儲存播放列表"""
        try:
            self.playlist_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.playlist_file, 'w', encoding='utf-8') as f:
                json.dump(self.playlists, f, ensure_ascii=False, indent=2)
            logger.debug("播放列表已儲存")
            return True
        except IOError as e:
            logger.error(f"儲存播放列表失敗: {e}", exc_info=True)
            return False

    def create_playlist(self, name: str, description: str = "") -> bool:
        """
        建立新的播放列表

        Args:
            name: 播放列表名稱
            description: 播放列表描述

        Returns:
            是否建立成功
        """
        if not name or name.strip() == "":
            logger.warning("播放列表名稱不能為空")
            return False

        if name in self.playlists:
            logger.warning(f"播放列表已存在: {name}")
            return False

        self.playlists[name] = {
            "description": description,
            "songs": [],
            "song_count": 0
        }
        logger.info(f"建立播放列表: {name}")
        return self._save_playlists()

    def delete_playlist(self, name: str) -> bool:
        """
        刪除播放列表

        Args:
            name: 播放列表名稱

        Returns:
            是否刪除成功
        """
        if name not in self.playlists:
            logger.warning(f"播放列表不存在: {name}")
            return False

        del self.playlists[name]
        logger.info(f"刪除播放列表: {name}")
        return self._save_playlists()

    def rename_playlist(self, old_name: str, new_name: str) -> bool:
        """
        重新命名播放列表

        Args:
            old_name: 舊名稱
            new_name: 新名稱

        Returns:
            是否重新命名成功
        """
        if old_name not in self.playlists:
            logger.warning(f"播放列表不存在: {old_name}")
            return False

        if new_name in self.playlists:
            logger.warning(f"播放列表名稱已存在: {new_name}")
            return False

        if not new_name or new_name.strip() == "":
            logger.warning("新名稱不能為空")
            return False

        self.playlists[new_name] = self.playlists.pop(old_name)
        logger.info(f"重新命名播放列表: {old_name} -> {new_name}")
        return self._save_playlists()

    def get_all_playlists(self) -> List[Dict]:
        """
        取得所有播放列表

        Returns:
            播放列表列表 (包含名稱、描述、歌曲數量)
        """
        return [
            {
                "name": name,
                "description": info["description"],
                "song_count": info["song_count"]
            }
            for name, info in self.playlists.items()
        ]

    def get_playlist(self, name: str) -> Optional[Dict]:
        """
        取得特定播放列表

        Args:
            name: 播放列表名稱

        Returns:
            播放列表資訊,不存在則返回 None
        """
        if name not in self.playlists:
            return None

        playlist = self.playlists[name]
        return {
            "name": name,
            "description": playlist["description"],
            "songs": playlist["songs"],
            "song_count": playlist["song_count"]
        }

    def add_song(self, playlist_name: str, song_id: str) -> bool:
        """
        加入歌曲到播放列表

        Args:
            playlist_name: 播放列表名稱
            song_id: 歌曲 ID

        Returns:
            是否加入成功
        """
        if playlist_name not in self.playlists:
            logger.warning(f"播放列表不存在: {playlist_name}")
            return False

        playlist = self.playlists[playlist_name]

        # 檢查歌曲是否已存在
        if song_id in playlist["songs"]:
            logger.warning(f"歌曲已在播放列表中: {song_id}")
            return False

        playlist["songs"].append(song_id)
        playlist["song_count"] = len(playlist["songs"])
        logger.info(f"加入歌曲到播放列表 {playlist_name}: {song_id}")
        return self._save_playlists()

    def remove_song(self, playlist_name: str, song_id: str) -> bool:
        """
        從播放列表移除歌曲

        Args:
            playlist_name: 播放列表名稱
            song_id: 歌曲 ID

        Returns:
            是否移除成功
        """
        if playlist_name not in self.playlists:
            logger.warning(f"播放列表不存在: {playlist_name}")
            return False

        playlist = self.playlists[playlist_name]

        if song_id not in playlist["songs"]:
            logger.warning(f"歌曲不在播放列表中: {song_id}")
            return False

        playlist["songs"].remove(song_id)
        playlist["song_count"] = len(playlist["songs"])
        logger.info(f"從播放列表 {playlist_name} 移除歌曲: {song_id}")
        return self._save_playlists()

    def move_song(self, playlist_name: str, song_id: str, new_position: int) -> bool:
        """
        調整歌曲在播放列表中的位置

        Args:
            playlist_name: 播放列表名稱
            song_id: 歌曲 ID
            new_position: 新位置 (0-based index)

        Returns:
            是否調整成功
        """
        if playlist_name not in self.playlists:
            logger.warning(f"播放列表不存在: {playlist_name}")
            return False

        playlist = self.playlists[playlist_name]

        if song_id not in playlist["songs"]:
            logger.warning(f"歌曲不在播放列表中: {song_id}")
            return False

        if new_position < 0 or new_position >= len(playlist["songs"]):
            logger.warning(f"位置超出範圍: {new_position}")
            return False

        # 移除舊位置
        playlist["songs"].remove(song_id)
        # 插入新位置
        playlist["songs"].insert(new_position, song_id)

        logger.info(f"調整歌曲位置: {song_id} -> {new_position}")
        return self._save_playlists()

    def clear_playlist(self, playlist_name: str) -> bool:
        """
        清空播放列表中的所有歌曲

        Args:
            playlist_name: 播放列表名稱

        Returns:
            是否清空成功
        """
        if playlist_name not in self.playlists:
            logger.warning(f"播放列表不存在: {playlist_name}")
            return False

        self.playlists[playlist_name]["songs"] = []
        self.playlists[playlist_name]["song_count"] = 0
        logger.info(f"清空播放列表: {playlist_name}")
        return self._save_playlists()

    def update_description(self, playlist_name: str, description: str) -> bool:
        """
        更新播放列表描述

        Args:
            playlist_name: 播放列表名稱
            description: 新的描述

        Returns:
            是否更新成功
        """
        if playlist_name not in self.playlists:
            logger.warning(f"播放列表不存在: {playlist_name}")
            return False

        self.playlists[playlist_name]["description"] = description
        logger.info(f"更新播放列表描述: {playlist_name}")
        return self._save_playlists()

    def swap_songs(self, playlist_name: str, index1: int, index2: int) -> bool:
        """
        交換播放列表中兩首歌曲的位置

        Args:
            playlist_name: 播放列表名稱
            index1: 第一首歌曲的索引
            index2: 第二首歌曲的索引

        Returns:
            是否交換成功
        """
        if playlist_name not in self.playlists:
            logger.warning(f"播放列表不存在: {playlist_name}")
            return False

        playlist = self.playlists[playlist_name]
        songs = playlist["songs"]

        if index1 < 0 or index1 >= len(songs) or index2 < 0 or index2 >= len(songs):
            logger.warning(f"索引超出範圍: {index1}, {index2}")
            return False

        # 交換位置
        songs[index1], songs[index2] = songs[index2], songs[index1]

        logger.info(f"交換歌曲位置: {index1} <-> {index2}")
        return self._save_playlists()

    def move_songs_batch(self, playlist_name: str, song_ids: List[str], target_position: int) -> bool:
        """
        批次移動多首歌曲到指定位置

        Args:
            playlist_name: 播放列表名稱
            song_ids: 要移動的歌曲 ID 列表
            target_position: 目標位置

        Returns:
            是否移動成功
        """
        if playlist_name not in self.playlists:
            logger.warning(f"播放列表不存在: {playlist_name}")
            return False

        playlist = self.playlists[playlist_name]
        songs = playlist["songs"]

        # 驗證所有歌曲都在播放列表中
        for song_id in song_ids:
            if song_id not in songs:
                logger.warning(f"歌曲不在播放列表中: {song_id}")
                return False

        if target_position < 0 or target_position > len(songs):
            logger.warning(f"目標位置超出範圍: {target_position}")
            return False

        # 移除所有要移動的歌曲
        for song_id in song_ids:
            songs.remove(song_id)

        # 調整目標位置（因為移除了歌曲）
        adjusted_position = min(target_position, len(songs))

        # 在目標位置插入歌曲
        for i, song_id in enumerate(song_ids):
            songs.insert(adjusted_position + i, song_id)

        logger.info(f"批次移動 {len(song_ids)} 首歌曲到位置 {target_position}")
        return self._save_playlists()

    def shuffle_playlist(self, playlist_name: str) -> bool:
        """
        隨機排序播放列表

        Args:
            playlist_name: 播放列表名稱

        Returns:
            是否排序成功
        """
        import random

        if playlist_name not in self.playlists:
            logger.warning(f"播放列表不存在: {playlist_name}")
            return False

        playlist = self.playlists[playlist_name]
        random.shuffle(playlist["songs"])

        logger.info(f"隨機排序播放列表: {playlist_name}")
        return self._save_playlists()

    def sort_playlist(self, playlist_name: str, song_info_getter, key: str, reverse: bool = False) -> bool:
        """
        依照指定條件排序播放列表

        Args:
            playlist_name: 播放列表名稱
            song_info_getter: 取得歌曲資訊的函數 (song_id -> song_dict)
            key: 排序鍵 ('title', 'duration', 'uploader', 等)
            reverse: 是否反向排序

        Returns:
            是否排序成功
        """
        if playlist_name not in self.playlists:
            logger.warning(f"播放列表不存在: {playlist_name}")
            return False

        playlist = self.playlists[playlist_name]
        songs = playlist["songs"]

        # 取得所有歌曲資訊
        song_info_list = []
        for song_id in songs:
            song_info = song_info_getter(song_id)
            if song_info:
                song_info_list.append(song_info)

        # 依照指定鍵排序
        try:
            song_info_list.sort(key=lambda s: s.get(key, ''), reverse=reverse)
            playlist["songs"] = [s['id'] for s in song_info_list]

            logger.info(f"排序播放列表 {playlist_name} (key={key}, reverse={reverse})")
            return self._save_playlists()

        except Exception as e:
            logger.error(f"排序播放列表失敗: {e}", exc_info=True)
            return False

    def reverse_playlist(self, playlist_name: str) -> bool:
        """
        反轉播放列表順序

        Args:
            playlist_name: 播放列表名稱

        Returns:
            是否反轉成功
        """
        if playlist_name not in self.playlists:
            logger.warning(f"播放列表不存在: {playlist_name}")
            return False

        playlist = self.playlists[playlist_name]
        playlist["songs"].reverse()

        logger.info(f"反轉播放列表: {playlist_name}")
        return self._save_playlists()
