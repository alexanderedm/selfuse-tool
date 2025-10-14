"""RSS Filter Manager 模組測試"""
import unittest
from unittest.mock import Mock, MagicMock


class TestRSSFilterManager(unittest.TestCase):
    """RSSFilterManager 測試套件"""

    def setUp(self):
        """測試前置設定"""
        self.mock_rss_manager = Mock()

    def test_init(self):
        """測試初始化"""
        from rss_filter_manager import RSSFilterManager

        manager = RSSFilterManager(self.mock_rss_manager)

        self.assertEqual(manager.rss_manager, self.mock_rss_manager)
        self.assertEqual(manager.all_entries, [])
        self.assertEqual(manager.current_entries, [])

    def test_set_all_entries(self):
        """測試設定所有文章"""
        from rss_filter_manager import RSSFilterManager

        manager = RSSFilterManager(self.mock_rss_manager)
        entries = [{'id': '1', 'title': 'Test', 'published': '2025-01-01'}]

        manager.set_all_entries(entries)

        self.assertEqual(manager.all_entries, entries)
        self.assertEqual(manager.current_entries, entries)

    def test_filter_by_mode_all(self):
        """測試全部模式篩選"""
        from rss_filter_manager import RSSFilterManager

        entries = [
            {'id': '1', 'title': 'Test 1', 'published': '2025-01-01'},
            {'id': '2', 'title': 'Test 2', 'published': '2025-01-02'}
        ]

        manager = RSSFilterManager(self.mock_rss_manager)
        manager.set_all_entries(entries)

        result = manager.filter_by_mode('all')

        self.assertEqual(len(result), 2)
        self.assertEqual(result, entries)

    def test_filter_by_mode_unread(self):
        """測試未讀模式篩選"""
        from rss_filter_manager import RSSFilterManager

        entries = [
            {'id': '1', 'title': 'Read', 'published': '2025-01-01'},
            {'id': '2', 'title': 'Unread', 'published': '2025-01-02'}
        ]

        self.mock_rss_manager.is_read.side_effect = lambda id: id == '1'

        manager = RSSFilterManager(self.mock_rss_manager)
        manager.set_all_entries(entries)

        result = manager.filter_by_mode('unread')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], '2')

    def test_filter_by_mode_favorite(self):
        """測試收藏模式篩選"""
        from rss_filter_manager import RSSFilterManager

        entries = [
            {'id': '1', 'title': 'Not Fav', 'published': '2025-01-01'},
            {'id': '2', 'title': 'Favorite', 'published': '2025-01-02'}
        ]

        self.mock_rss_manager.is_favorite.side_effect = lambda id: id == '2'

        manager = RSSFilterManager(self.mock_rss_manager)
        manager.set_all_entries(entries)

        result = manager.filter_by_mode('favorite')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], '2')

    def test_filter_by_keyword_in_title(self):
        """測試關鍵字標題搜尋"""
        from rss_filter_manager import RSSFilterManager

        entries = [
            {'id': '1', 'title': 'Python Tutorial', 'published': '2025-01-01', 'content': 'Learn Python'},
            {'id': '2', 'title': 'JavaScript Guide', 'published': '2025-01-02', 'content': 'Learn JS'}
        ]

        manager = RSSFilterManager(self.mock_rss_manager)
        manager.set_all_entries(entries)

        result = manager.filter_by_keyword(entries, 'python')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], '1')

    def test_filter_by_keyword_in_content(self):
        """測試關鍵字內容搜尋"""
        from rss_filter_manager import RSSFilterManager

        entries = [
            {'id': '1', 'title': 'Tutorial', 'published': '2025-01-01', 'content': 'Learn Python'},
            {'id': '2', 'title': 'Guide', 'published': '2025-01-02', 'content': 'Learn JavaScript'}
        ]

        manager = RSSFilterManager(self.mock_rss_manager)
        manager.set_all_entries(entries)

        result = manager.filter_by_keyword(entries, 'javascript')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], '2')

    def test_filter_by_keyword_case_insensitive(self):
        """測試關鍵字搜尋不區分大小寫"""
        from rss_filter_manager import RSSFilterManager

        entries = [
            {'id': '1', 'title': 'PYTHON Tutorial', 'published': '2025-01-01', 'content': 'Learn'}
        ]

        manager = RSSFilterManager(self.mock_rss_manager)
        manager.set_all_entries(entries)

        result = manager.filter_by_keyword(entries, 'python')

        self.assertEqual(len(result), 1)

    def test_filter_combined_mode_and_keyword(self):
        """測試組合篩選：模式 + 關鍵字"""
        from rss_filter_manager import RSSFilterManager

        entries = [
            {'id': '1', 'title': 'Python Tutorial', 'published': '2025-01-01', 'content': 'Learn Python'},
            {'id': '2', 'title': 'Python Guide', 'published': '2025-01-02', 'content': 'Advanced Python'},
            {'id': '3', 'title': 'JavaScript Tutorial', 'published': '2025-01-03', 'content': 'Learn JS'}
        ]

        # 只有 id='2' 是未讀
        self.mock_rss_manager.is_read.side_effect = lambda id: id != '2'

        manager = RSSFilterManager(self.mock_rss_manager)
        manager.set_all_entries(entries)

        # 篩選未讀 + 包含 'Python'
        filtered_by_mode = manager.filter_by_mode('unread')
        result = manager.filter_by_keyword(filtered_by_mode, 'python')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], '2')

    def test_filter_no_results(self):
        """測試篩選無結果"""
        from rss_filter_manager import RSSFilterManager

        entries = [
            {'id': '1', 'title': 'Python', 'published': '2025-01-01', 'content': 'Python'}
        ]

        manager = RSSFilterManager(self.mock_rss_manager)
        manager.set_all_entries(entries)

        result = manager.filter_by_keyword(entries, 'javascript')

        self.assertEqual(len(result), 0)

    def test_get_current_entries(self):
        """測試取得當前篩選後的文章"""
        from rss_filter_manager import RSSFilterManager

        entries = [
            {'id': '1', 'title': 'Test', 'published': '2025-01-01'}
        ]

        manager = RSSFilterManager(self.mock_rss_manager)
        manager.set_all_entries(entries)

        result = manager.get_current_entries()

        self.assertEqual(result, entries)


if __name__ == '__main__':
    unittest.main()
