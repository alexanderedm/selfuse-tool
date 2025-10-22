"""搜尋管理器模組

提供強化的音樂搜尋功能：
- 多條件篩選
- 智慧搜尋（模糊匹配）
- 搜尋歷史記錄
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Callable
from datetime import datetime
from src.core.logger import logger


class SearchManager:
    """音樂搜尋管理器"""

    def __init__(self, history_file: str = "search_history.json", max_history: int = 50):
        """初始化搜尋管理器

        Args:
            history_file: 搜尋歷史檔案路徑
            max_history: 最大歷史記錄數量
        """
        self.history_file = Path(history_file)
        self.max_history = max_history
        self.search_history = self._load_history()

    def _load_history(self) -> List[Dict]:
        """載入搜尋歷史"""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"成功載入搜尋歷史，共 {len(data)} 筆記錄")
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"載入搜尋歷史失敗: {e}")
            return []

    def _save_history(self) -> bool:
        """儲存搜尋歷史"""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_history, f, ensure_ascii=False, indent=2)
            logger.debug("搜尋歷史已儲存")
            return True
        except IOError as e:
            logger.error(f"儲存搜尋歷史失敗: {e}")
            return False

    def add_to_history(self, query: str, filters: Optional[Dict] = None) -> bool:
        """添加搜尋記錄到歷史

        Args:
            query: 搜尋關鍵字
            filters: 篩選條件

        Returns:
            是否添加成功
        """
        if not query or query.strip() == "":
            return False

        # 檢查是否已存在相同的搜尋
        for i, record in enumerate(self.search_history):
            if record['query'] == query and record.get('filters') == filters:
                # 移除舊記錄
                self.search_history.pop(i)
                break

        # 添加新記錄到開頭
        self.search_history.insert(0, {
            'query': query,
            'filters': filters or {},
            'timestamp': datetime.now().isoformat(),
            'result_count': 0  # 稍後更新
        })

        # 限制歷史記錄數量
        if len(self.search_history) > self.max_history:
            self.search_history = self.search_history[:self.max_history]

        return self._save_history()

    def update_history_result_count(self, query: str, count: int):
        """更新搜尋歷史的結果數量

        Args:
            query: 搜尋關鍵字
            count: 結果數量
        """
        for record in self.search_history:
            if record['query'] == query:
                record['result_count'] = count
                self._save_history()
                break

    def get_search_history(self, limit: int = 10) -> List[Dict]:
        """取得搜尋歷史

        Args:
            limit: 返回的記錄數量

        Returns:
            搜尋歷史列表
        """
        return self.search_history[:limit]

    def clear_search_history(self) -> bool:
        """清空搜尋歷史

        Returns:
            是否清空成功
        """
        self.search_history = []
        return self._save_history()

    def remove_from_history(self, query: str) -> bool:
        """從歷史中移除特定搜尋

        Args:
            query: 搜尋關鍵字

        Returns:
            是否移除成功
        """
        for i, record in enumerate(self.search_history):
            if record['query'] == query:
                self.search_history.pop(i)
                return self._save_history()

        return False

    @staticmethod
    def fuzzy_match(text: str, pattern: str) -> bool:
        """模糊匹配

        Args:
            text: 要匹配的文字
            pattern: 匹配模式

        Returns:
            是否匹配
        """
        # 移除空白並轉小寫
        text = text.lower().strip()
        pattern = pattern.lower().strip()

        # 完全匹配
        if pattern in text:
            return True

        # 字元距離匹配（允許少量字元差異）
        # 簡單實現：檢查 pattern 的所有字元是否按順序出現在 text 中
        pattern_idx = 0
        for char in text:
            if pattern_idx < len(pattern) and char == pattern[pattern_idx]:
                pattern_idx += 1

        return pattern_idx == len(pattern)

    def _filter_by_query(self, songs: List[Dict], query: str, fuzzy: bool) -> List[Dict]:
        """按關鍵字篩選歌曲（輔助方法）"""
        if not query or not query.strip():
            return songs

        query_lower = query.lower().strip()
        filtered = []

        for song in songs:
            title = song.get('title', '').lower()
            category = song.get('category', '').lower()
            uploader = song.get('uploader', '').lower()

            if fuzzy:
                if (self.fuzzy_match(title, query_lower) or
                    self.fuzzy_match(category, query_lower) or
                    self.fuzzy_match(uploader, query_lower)):
                    filtered.append(song)
            else:
                if (query_lower in title or
                    query_lower in category or
                    query_lower in uploader):
                    filtered.append(song)

        return filtered

    def _apply_filters(
        self,
        songs: List[Dict],
        categories: Optional[List[str]],
        duration_min: Optional[int],
        duration_max: Optional[int],
        uploaders: Optional[List[str]]
    ) -> List[Dict]:
        """應用多種篩選條件（輔助方法）"""
        results = songs

        # 分類篩選
        if categories:
            results = [s for s in results if s.get('category') in categories]

        # 時長篩選
        if duration_min is not None:
            results = [s for s in results if s.get('duration', 0) >= duration_min]

        if duration_max is not None:
            results = [s for s in results if s.get('duration', 0) <= duration_max]

        # 上傳者篩選
        if uploaders:
            results = [s for s in results if s.get('uploader') in uploaders]

        return results

    def search_songs(
        self,
        songs: List[Dict],
        query: str = "",
        categories: Optional[List[str]] = None,
        duration_min: Optional[int] = None,
        duration_max: Optional[int] = None,
        uploaders: Optional[List[str]] = None,
        fuzzy: bool = True,
        save_history: bool = True
    ) -> List[Dict]:
        """增強的歌曲搜尋

        Args:
            songs: 歌曲列表
            query: 搜尋關鍵字
            categories: 分類篩選列表
            duration_min: 最小時長（秒）
            duration_max: 最大時長（秒）
            uploaders: 上傳者篩選列表
            fuzzy: 是否使用模糊匹配
            save_history: 是否儲存到搜尋歷史

        Returns:
            符合條件的歌曲列表
        """
        # 1. 關鍵字搜尋
        results = self._filter_by_query(songs, query, fuzzy)

        # 2. 應用其他篩選條件
        results = self._apply_filters(results, categories, duration_min, duration_max, uploaders)

        # 3. 儲存搜尋歷史
        if save_history and query:
            filters = {}
            if categories:
                filters['categories'] = categories
            if duration_min is not None:
                filters['duration_min'] = duration_min
            if duration_max is not None:
                filters['duration_max'] = duration_max
            if uploaders:
                filters['uploaders'] = uploaders

            self.add_to_history(query, filters if filters else None)
            self.update_history_result_count(query, len(results))

        logger.info(f"搜尋完成: '{query}' 找到 {len(results)} 首歌曲")
        return results

    def get_available_categories(self, songs: List[Dict]) -> List[str]:
        """取得所有可用的分類

        Args:
            songs: 歌曲列表

        Returns:
            分類列表
        """
        categories = set()
        for song in songs:
            category = song.get('category')
            if category:
                categories.add(category)

        return sorted(list(categories))

    def get_available_uploaders(self, songs: List[Dict]) -> List[str]:
        """取得所有可用的上傳者

        Args:
            songs: 歌曲列表

        Returns:
            上傳者列表
        """
        uploaders = set()
        for song in songs:
            uploader = song.get('uploader')
            if uploader and uploader != '未知':
                uploaders.add(uploader)

        return sorted(list(uploaders))

    def get_duration_range(self, songs: List[Dict]) -> tuple:
        """取得歌曲時長範圍

        Args:
            songs: 歌曲列表

        Returns:
            (最小時長, 最大時長) 單位：秒
        """
        if not songs:
            return (0, 0)

        durations = [song.get('duration', 0) for song in songs if song.get('duration')]

        if not durations:
            return (0, 0)

        return (min(durations), max(durations))
