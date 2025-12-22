"""RSS Entry List View 模組測試"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk


class TestRSSEntryListView(unittest.TestCase):
    """RSSEntryListView 測試套件"""

    def setUp(self):
        """測試前置設定"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.mock_rss_manager = Mock()
        self.mock_filter_manager = Mock()
        self.mock_on_entry_select = Mock()

    def tearDown(self):
        """測試後清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_init(self):
        """測試初始化"""
        from src.rss.rss_entry_list_view import RSSEntryListView

        parent = tk.Frame(self.root)
        view = RSSEntryListView(
            parent,
            self.mock_rss_manager,
            self.mock_filter_manager,
            self.mock_on_entry_select
        )

        self.assertIsNotNone(view.entries_tree)
        self.assertEqual(view.rss_manager, self.mock_rss_manager)
        self.assertEqual(view.filter_manager, self.mock_filter_manager)

    def test_display_entries_empty(self):
        """測試顯示空文章列表"""
        from src.rss.rss_entry_list_view import RSSEntryListView

        parent = tk.Frame(self.root)
        view = RSSEntryListView(
            parent,
            self.mock_rss_manager,
            self.mock_filter_manager,
            self.mock_on_entry_select
        )

        view.display_entries([])

        # 檢查是否有錯誤訊息
        children = view.entries_tree.get_children()
        self.assertEqual(len(children), 1)

    def test_display_entries_with_data(self):
        """測試顯示文章列表"""
        from src.rss.rss_entry_list_view import RSSEntryListView

        entries = [
            {'id': '1', 'title': 'Test 1', 'published': '2025-01-01'},
            {'id': '2', 'title': 'Test 2', 'published': '2025-01-02'}
        ]

        self.mock_rss_manager.is_read.return_value = False
        self.mock_rss_manager.is_favorite.return_value = False

        parent = tk.Frame(self.root)
        view = RSSEntryListView(
            parent,
            self.mock_rss_manager,
            self.mock_filter_manager,
            self.mock_on_entry_select
        )

        view.display_entries(entries)

        children = view.entries_tree.get_children()
        self.assertEqual(len(children), 2)

    def test_on_entry_select(self):
        """測試文章選擇"""
        from src.rss.rss_entry_list_view import RSSEntryListView

        entries = [
            {'id': '1', 'title': 'Test', 'published': '2025-01-01'}
        ]

        self.mock_rss_manager.is_read.return_value = False
        self.mock_rss_manager.is_favorite.return_value = False

        parent = tk.Frame(self.root)
        view = RSSEntryListView(
            parent,
            self.mock_rss_manager,
            self.mock_filter_manager,
            self.mock_on_entry_select
        )

        view.display_entries(entries)

        # 選擇第一個項目
        children = view.entries_tree.get_children()
        view.entries_tree.selection_set(children[0])

        # 觸發選擇事件
        view._on_entry_select(None)

        # 回調應被呼叫
        self.mock_on_entry_select.assert_called_once()
        # 自動標記為已讀
        self.mock_rss_manager.mark_as_read.assert_called_once_with('1')

    def test_toggle_read_status(self):
        """測試切換已讀狀態"""
        from src.rss.rss_entry_list_view import RSSEntryListView

        entries = [
            {'id': '1', 'title': 'Test', 'published': '2025-01-01'}
        ]

        self.mock_rss_manager.is_read.return_value = False
        self.mock_rss_manager.is_favorite.return_value = False

        parent = tk.Frame(self.root)
        view = RSSEntryListView(
            parent,
            self.mock_rss_manager,
            self.mock_filter_manager,
            self.mock_on_entry_select
        )

        view.display_entries(entries)
        children = view.entries_tree.get_children()
        item = children[0]

        # 標記為已讀
        view.toggle_read_status(item, entries[0], True)

        self.mock_rss_manager.mark_as_read.assert_called_with('1')

    def test_toggle_favorite(self):
        """測試切換收藏狀態"""
        from src.rss.rss_entry_list_view import RSSEntryListView

        entries = [
            {'id': '1', 'title': 'Test', 'published': '2025-01-01'}
        ]

        self.mock_rss_manager.is_read.return_value = False
        self.mock_rss_manager.is_favorite.return_value = False

        parent = tk.Frame(self.root)
        view = RSSEntryListView(
            parent,
            self.mock_rss_manager,
            self.mock_filter_manager,
            self.mock_on_entry_select
        )

        view.display_entries(entries)
        children = view.entries_tree.get_children()
        item = children[0]

        # 加入收藏
        view.toggle_favorite(item, entries[0], True)

        self.mock_rss_manager.add_favorite.assert_called_with('1', entries[0])

    def test_clear_entries(self):
        """測試清空文章列表"""
        from src.rss.rss_entry_list_view import RSSEntryListView

        entries = [
            {'id': '1', 'title': 'Test', 'published': '2025-01-01'}
        ]

        self.mock_rss_manager.is_read.return_value = False
        self.mock_rss_manager.is_favorite.return_value = False

        parent = tk.Frame(self.root)
        view = RSSEntryListView(
            parent,
            self.mock_rss_manager,
            self.mock_filter_manager,
            self.mock_on_entry_select
        )

        view.display_entries(entries)
        self.assertGreater(len(view.entries_tree.get_children()), 0)

        view.clear()
        self.assertEqual(len(view.entries_tree.get_children()), 0)

    def test_apply_filter(self):
        """測試套用篩選"""
        from src.rss.rss_entry_list_view import RSSEntryListView

        entries = [
            {'id': '1', 'title': 'Test', 'published': '2025-01-01'}
        ]

        self.mock_filter_manager.apply_filters.return_value = entries

        parent = tk.Frame(self.root)
        view = RSSEntryListView(
            parent,
            self.mock_rss_manager,
            self.mock_filter_manager,
            self.mock_on_entry_select
        )

        view.apply_filter()

        # 檢查是否呼叫 filter_manager
        self.mock_filter_manager.apply_filters.assert_called_once()


if __name__ == '__main__':
    unittest.main()
