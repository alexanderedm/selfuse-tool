"""RSS Filter Manager 模組 - 文章篩選邏輯

重構自 rss_window.py 的 _filter_entries() 方法
原始複雜度: CC=26 (極高)
目標複雜度: 每個方法 CC<10

設計原則:
1. 單一職責：每個方法只做一件事
2. 拆分邏輯：將大方法拆成多個小方法
3. 提高可測試性：每個小方法都可獨立測試
"""
from src.core.logger import logger


class RSSFilterManager:
    """RSS 文章篩選管理器

    負責處理文章的篩選邏輯：
    - 按模式篩選 (全部/未讀/收藏)
    - 按關鍵字搜尋
    - 組合篩選
    """

    def __init__(self, rss_manager):
        """初始化篩選管理器

        Args:
            rss_manager: RSS 管理器實例
        """
        self.rss_manager = rss_manager
        self.all_entries = []  # 所有未過濾的文章
        self.current_entries = []  # 當前篩選後的文章

    def set_all_entries(self, entries):
        """設定所有文章

        Args:
            entries (list): 文章列表
        """
        self.all_entries = entries
        self.current_entries = entries

    def set_entries(self, entries):
        """設定所有文章 (別名方法,與 set_all_entries 相同)

        Args:
            entries (list): 文章列表
        """
        self.set_all_entries(entries)

    def get_current_entries(self):
        """取得當前篩選後的文章

        Returns:
            list: 文章列表
        """
        return self.current_entries

    def filter_by_mode(self, mode):
        """按模式篩選文章

        Args:
            mode (str): 篩選模式 'all', 'unread', 'favorite'

        Returns:
            list: 篩選後的文章列表
        """
        if mode == 'all':
            return self._filter_all()
        elif mode == 'unread':
            return self._filter_unread()
        elif mode == 'favorite':
            return self._filter_favorite()
        else:
            logger.warning(f"未知的篩選模式: {mode}")
            return self.all_entries

    def _filter_all(self):
        """全部文章

        Returns:
            list: 所有文章
        """
        return self.all_entries

    def _filter_unread(self):
        """未讀文章

        Returns:
            list: 未讀文章列表
        """
        return [
            entry for entry in self.all_entries
            if not self.rss_manager.is_read(entry['id'])
        ]

    def _filter_favorite(self):
        """收藏文章

        Returns:
            list: 收藏文章列表
        """
        return [
            entry for entry in self.all_entries
            if self.rss_manager.is_favorite(entry['id'])
        ]

    def filter_by_keyword(self, entries, keyword):
        """按關鍵字搜尋文章

        Args:
            entries (list): 要搜尋的文章列表
            keyword (str): 搜尋關鍵字

        Returns:
            list: 符合的文章列表
        """
        if not keyword:
            return entries

        keyword = keyword.lower().strip()

        return [
            entry for entry in entries
            if self._match_keyword(entry, keyword)
        ]

    def _match_keyword(self, entry, keyword):
        """檢查文章是否符合關鍵字

        Args:
            entry (dict): 文章資料
            keyword (str): 搜尋關鍵字 (已轉小寫)

        Returns:
            bool: 是否符合
        """
        title = entry.get('title', '').lower()
        content = entry.get('content', entry.get('summary', '')).lower()

        return keyword in title or keyword in content

    def apply_filters(self, mode, keyword=''):
        """套用篩選條件

        Args:
            mode (str): 篩選模式 'all', 'unread', 'favorite'
            keyword (str): 搜尋關鍵字

        Returns:
            list: 篩選後的文章列表
        """
        # 步驟 1: 按模式篩選
        filtered_by_mode = self.filter_by_mode(mode)

        # 步驟 2: 按關鍵字搜尋
        filtered_by_keyword = self.filter_by_keyword(filtered_by_mode, keyword)

        # 更新當前篩選結果
        self.current_entries = filtered_by_keyword

        return filtered_by_keyword
