"""
播放記錄管理模組
管理音樂播放記錄、播放次數統計、最近播放列表等功能
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PlayHistoryManager:
    """播放記錄管理器"""

    def __init__(self, history_file: str = "play_history.json"):
        """
        初始化播放記錄管理器

        Args:
            history_file: 播放記錄檔案路徑
        """
        self.history_file = Path(history_file)
        self.history_data = self._load_history()
        logger.info(f"播放記錄管理器已初始化,記錄檔案: {history_file}")

    def _load_history(self) -> Dict:
        """載入播放記錄"""
        if not self.history_file.exists():
            return {
                "recent_plays": [],  # 最近播放列表
                "play_counts": {},   # 播放次數統計 {song_id: count}
                "total_plays": 0     # 總播放次數
            }

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"成功載入播放記錄,共 {data.get('total_plays', 0)} 次播放")
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"載入播放記錄失敗: {e}", exc_info=True)
            return {
                "recent_plays": [],
                "play_counts": {},
                "total_plays": 0
            }

    def _save_history(self) -> bool:
        """儲存播放記錄"""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
            logger.debug("播放記錄已儲存")
            return True
        except IOError as e:
            logger.error(f"儲存播放記錄失敗: {e}", exc_info=True)
            return False

    def record_play(self, song_id: str, song_info: Dict) -> bool:
        """
        記錄一次播放

        Args:
            song_id: 歌曲 ID
            song_info: 歌曲資訊 (包含 title, artist, category 等)

        Returns:
            是否記錄成功
        """
        try:
            # 記錄到最近播放
            play_record = {
                "song_id": song_id,
                "title": song_info.get("title", "Unknown"),
                "artist": song_info.get("artist", "Unknown"),
                "category": song_info.get("category", "Unknown"),
                "played_at": datetime.now().isoformat()
            }

            # 加入最近播放列表 (最多保留 100 筆)
            self.history_data["recent_plays"].insert(0, play_record)
            if len(self.history_data["recent_plays"]) > 100:
                self.history_data["recent_plays"] = self.history_data["recent_plays"][:100]

            # 更新播放次數
            if song_id not in self.history_data["play_counts"]:
                self.history_data["play_counts"][song_id] = 0
            self.history_data["play_counts"][song_id] += 1

            # 更新總播放次數
            self.history_data["total_plays"] += 1

            logger.info(f"記錄播放: {song_info.get('title')} (總播放次數: {self.history_data['total_plays']})")

            return self._save_history()
        except Exception as e:
            logger.error(f"記錄播放失敗: {e}", exc_info=True)
            return False

    def get_recent_plays(self, limit: int = 20) -> List[Dict]:
        """
        取得最近播放列表

        Args:
            limit: 返回的記錄數量上限

        Returns:
            最近播放的歌曲列表
        """
        return self.history_data["recent_plays"][:limit]

    def get_play_count(self, song_id: str) -> int:
        """
        取得歌曲播放次數

        Args:
            song_id: 歌曲 ID

        Returns:
            播放次數
        """
        return self.history_data["play_counts"].get(song_id, 0)

    def get_most_played(self, limit: int = 20) -> List[Dict]:
        """
        取得最常播放的歌曲排行榜

        Args:
            limit: 返回的記錄數量上限

        Returns:
            最常播放的歌曲列表 (包含 song_id 和 play_count)
        """
        play_counts = self.history_data["play_counts"]
        sorted_songs = sorted(
            play_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {"song_id": song_id, "play_count": count}
            for song_id, count in sorted_songs
        ]

    def get_total_plays(self) -> int:
        """
        取得總播放次數

        Returns:
            總播放次數
        """
        return self.history_data["total_plays"]

    def clear_history(self) -> bool:
        """
        清除所有播放記錄

        Returns:
            是否清除成功
        """
        self.history_data = {
            "recent_plays": [],
            "play_counts": {},
            "total_plays": 0
        }
        logger.info("已清除所有播放記錄")
        return self._save_history()

    def clear_recent_plays(self) -> bool:
        """
        清除最近播放列表 (保留播放次數統計)

        Returns:
            是否清除成功
        """
        self.history_data["recent_plays"] = []
        logger.info("已清除最近播放列表")
        return self._save_history()
