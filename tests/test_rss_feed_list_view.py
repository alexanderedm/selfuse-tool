"""RSS Feed List View 模組測試"""
import unittest
from unittest.mock import Mock, MagicMock, patch, call
import tkinter as tk
from tkinter import ttk


class TestRSSFeedListView(unittest.TestCase):
    """RSSFeedListView 測試套件"""

    def setUp(self):
        """測試前置設定"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏主視窗
        self.mock_rss_manager = Mock()
        self.mock_on_feed_select = Mock()

    def tearDown(self):
        """測試後清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_init(self):
        """測試初始化"""
        from src.rss.rss_feed_list_view import RSSFeedListView

        parent = tk.Frame(self.root)
        view = RSSFeedListView(parent, self.mock_rss_manager, self.mock_on_feed_select)

        self.assertIsNotNone(view.feeds_tree)
        self.assertEqual(view.rss_manager, self.mock_rss_manager)
        self.assertEqual(view.on_feed_select_callback, self.mock_on_feed_select)

    def test_load_feeds_empty(self):
        """測試載入空訂閱列表"""
        from src.rss.rss_feed_list_view import RSSFeedListView

        self.mock_rss_manager.get_all_feeds.return_value = {}

        parent = tk.Frame(self.root)
        view = RSSFeedListView(parent, self.mock_rss_manager, self.mock_on_feed_select)
        view.load_feeds()

        # 檢查是否有 "尚無訂閱" 項目
        children = view.feeds_tree.get_children()
        self.assertEqual(len(children), 1)
        text = view.feeds_tree.item(children[0], 'text')
        self.assertIn('尚無訂閱', text)

    def test_load_feeds_with_data(self):
        """測試載入訂閱列表"""
        from src.rss.rss_feed_list_view import RSSFeedListView

        feeds = {
            'https://example.com/feed1': {'title': 'Feed 1'},
            'https://example.com/feed2': {'title': 'Feed 2'}
        }
        self.mock_rss_manager.get_all_feeds.return_value = feeds

        parent = tk.Frame(self.root)
        view = RSSFeedListView(parent, self.mock_rss_manager, self.mock_on_feed_select)
        view.load_feeds()

        # 檢查是否有2個訂閱
        children = view.feeds_tree.get_children()
        self.assertEqual(len(children), 2)

    def test_on_feed_select_no_selection(self):
        """測試未選擇訂閱時的行為"""
        from src.rss.rss_feed_list_view import RSSFeedListView

        parent = tk.Frame(self.root)
        view = RSSFeedListView(parent, self.mock_rss_manager, self.mock_on_feed_select)

        # 模擬沒有選擇
        view.feeds_tree.selection = Mock(return_value=())

        # 觸發選擇事件
        view._on_feed_select(None)

        # 回調不應被呼叫
        self.mock_on_feed_select.assert_not_called()

    def test_on_feed_select_with_selection(self):
        """測試選擇訂閱時的行為"""
        from src.rss.rss_feed_list_view import RSSFeedListView

        self.mock_rss_manager.get_all_feeds.return_value = {
            'https://example.com/feed1': {'title': 'Feed 1'}
        }

        parent = tk.Frame(self.root)
        view = RSSFeedListView(parent, self.mock_rss_manager, self.mock_on_feed_select)
        view.load_feeds()

        # 選擇第一個項目
        children = view.feeds_tree.get_children()
        self.assertGreater(len(children), 0)
        view.feeds_tree.selection_set(children[0])

        # 觸發選擇事件
        event = Mock()
        view._on_feed_select(event)

        # 回調應被呼叫並傳入 feed_url
        self.mock_on_feed_select.assert_called_once()
        args = self.mock_on_feed_select.call_args[0]
        self.assertEqual(args[0], 'https://example.com/feed1')

    def test_remove_feed(self):
        """測試移除訂閱"""
        from src.rss.rss_feed_list_view import RSSFeedListView

        # 設定 get_all_feeds 返回空字典以避免載入錯誤
        self.mock_rss_manager.get_all_feeds.return_value = {}

        parent = tk.Frame(self.root)
        view = RSSFeedListView(parent, self.mock_rss_manager, self.mock_on_feed_select)

        with patch('tkinter.messagebox.askyesno', return_value=True):
            view.remove_feed('https://example.com/feed1')

        # 檢查是否呼叫了 rss_manager.remove_feed
        self.mock_rss_manager.remove_feed.assert_called_once_with('https://example.com/feed1')

    def test_remove_feed_cancelled(self):
        """測試取消移除訂閱"""
        from src.rss.rss_feed_list_view import RSSFeedListView

        parent = tk.Frame(self.root)
        view = RSSFeedListView(parent, self.mock_rss_manager, self.mock_on_feed_select)

        with patch('tkinter.messagebox.askyesno', return_value=False):
            view.remove_feed('https://example.com/feed1')

        # 檢查 remove_feed 不應被呼叫
        self.mock_rss_manager.remove_feed.assert_not_called()

    def test_right_click_menu(self):
        """測試右鍵選單建立"""
        from src.rss.rss_feed_list_view import RSSFeedListView

        self.mock_rss_manager.get_all_feeds.return_value = {
            'https://example.com/feed1': {'title': 'Feed 1'}
        }

        parent = tk.Frame(self.root)
        view = RSSFeedListView(parent, self.mock_rss_manager, self.mock_on_feed_select)
        view.load_feeds()

        # 模擬右鍵點擊
        children = view.feeds_tree.get_children()
        item_id = children[0]

        # 取得 item 的 bbox 以計算 y 座標
        bbox = view.feeds_tree.bbox(item_id)
        if bbox:
            y = bbox[1] + 10
        else:
            y = 10

        event = Mock()
        event.y = y
        event.x_root = 100
        event.y_root = 100

        # 模擬 identify_row 返回正確的 item
        view.feeds_tree.identify_row = Mock(return_value=item_id)

        # 測試右鍵選單 (不實際顯示)
        with patch('tkinter.Menu') as mock_menu_class:
            mock_menu = Mock()
            mock_menu_class.return_value = mock_menu

            view._on_feed_right_click(event)

            # 檢查選單是否被建立並顯示
            mock_menu_class.assert_called_once()
            mock_menu.post.assert_called_once()

    def test_reload_feeds(self):
        """測試重新載入訂閱列表"""
        from src.rss.rss_feed_list_view import RSSFeedListView

        # 第一次載入
        self.mock_rss_manager.get_all_feeds.return_value = {
            'https://example.com/feed1': {'title': 'Feed 1'}
        }

        parent = tk.Frame(self.root)
        view = RSSFeedListView(parent, self.mock_rss_manager, self.mock_on_feed_select)
        view.load_feeds()

        self.assertEqual(len(view.feeds_tree.get_children()), 1)

        # 第二次載入 (新增一個訂閱)
        self.mock_rss_manager.get_all_feeds.return_value = {
            'https://example.com/feed1': {'title': 'Feed 1'},
            'https://example.com/feed2': {'title': 'Feed 2'}
        }

        view.load_feeds()

        self.assertEqual(len(view.feeds_tree.get_children()), 2)


if __name__ == '__main__':
    unittest.main()
