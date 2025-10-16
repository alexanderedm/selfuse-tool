"""RSS Window 模組測試"""
import unittest
from unittest.mock import Mock, MagicMock, patch, call
import tkinter as tk
from tkinter import ttk
import threading


def mock_tk_components(func):
    """裝飾器：Mock 所有 tkinter 元件"""
    @patch('rss_window.tk.Label')
    @patch('rss_window.tk.Frame')
    @patch('rss_window.ttk.Style')
    @patch('rss_window.ttk.Button')
    @patch('rss_window.tk.Toplevel')
    @patch('rss_window.RSSFeedListView')
    @patch('rss_window.RSSFilterManager')
    @patch('rss_window.RSSEntryListView')
    @patch('rss_window.RSSPreviewView')
    def wrapper(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label,
        *args,  # 接受額外的參數（來自其他 patch decorator）
        **kwargs
    ):
        return func(
            self,
            mock_preview_view,
            mock_entry_list_view,
            mock_filter_manager,
            mock_feed_list_view,
            mock_toplevel,
            mock_button,
            mock_style,
            mock_frame,
            mock_label,
            *args,  # 傳遞額外的參數給原函數
            **kwargs
        )
    return wrapper


class TestRSSWindow(unittest.TestCase):
    """RSSWindow 測試套件"""

    def setUp(self):
        """測試前置設定"""
        self.mock_rss_manager = Mock()
        # 預設返回空訂閱列表
        self.mock_rss_manager.get_all_feeds.return_value = {}
        self.mock_rss_manager.fetch_feed_entries.return_value = []

    def tearDown(self):
        """測試後清理"""
        pass

    # ========== A. 初始化和視窗管理測試 (8 tests) ==========

    def test_init(self):
        """測試初始化"""
        from rss_window import RSSWindow

        rss_window = RSSWindow(self.mock_rss_manager)

        # 驗證成員變數
        self.assertEqual(rss_window.rss_manager, self.mock_rss_manager)
        self.assertIsNone(rss_window.window)
        self.assertIsNone(rss_window.tk_root)
        self.assertIsNone(rss_window.current_feed_url)
        self.assertIsNone(rss_window.loading_label)
        self.assertIsNone(rss_window.feed_list_view)
        self.assertIsNone(rss_window.filter_manager)
        self.assertIsNone(rss_window.entry_list_view)
        self.assertIsNone(rss_window.preview_view)

    def test_init_with_tk_root(self):
        """測試使用共用根視窗初始化"""
        from rss_window import RSSWindow

        mock_root = Mock()
        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)

        self.assertEqual(rss_window.tk_root, mock_root)

    @mock_tk_components
    def test_show_creates_new_window(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試首次建立視窗"""
        from rss_window import RSSWindow

        # 建立 mock 根視窗
        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 驗證使用 Toplevel 建立視窗
        mock_toplevel.assert_called_once_with(mock_root)
        self.assertIsNotNone(rss_window.window)
        mock_window.title.assert_called_once()
        mock_window.geometry.assert_called_once()

    @mock_tk_components
    def test_show_reuses_existing_window(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試重用現有視窗"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()  # 第一次建立

        # 重設 mock 以檢查第二次呼叫
        mock_toplevel.reset_mock()

        rss_window.show()  # 第二次呼叫

        # 驗證不會再次建立視窗
        mock_toplevel.assert_not_called()
        # 驗證呼叫 lift 和 focus_force
        mock_window.lift.assert_called()
        mock_window.focus_force.assert_called()

    @mock_tk_components
    def test_show_recreates_destroyed_window(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試重建已銷毀的視窗"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 模擬視窗被銷毀 (lift 拋出例外)
        mock_window.lift.side_effect = Exception("Window destroyed")

        # 重設 mock
        mock_toplevel.reset_mock()
        mock_window.lift.side_effect = None  # 重設第二個視窗不拋例外

        rss_window.show()

        # 驗證重新建立視窗
        self.assertEqual(mock_toplevel.call_count, 1)

    @patch('rss_window.tk.Label')
    @patch('rss_window.tk.Frame')
    @patch('rss_window.ttk.Style')
    @patch('rss_window.ttk.Button')
    @patch('rss_window.tk.Tk')
    @patch('rss_window.RSSFeedListView')
    @patch('rss_window.RSSFilterManager')
    @patch('rss_window.RSSEntryListView')
    @patch('rss_window.RSSPreviewView')
    def test_window_uses_independent_root(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_tk,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試使用獨立視窗"""
        from rss_window import RSSWindow

        mock_window = Mock()
        mock_tk.return_value = mock_window

        # 不提供 tk_root
        rss_window = RSSWindow(self.mock_rss_manager)
        rss_window.show()

        # 驗證使用 Tk() 建立獨立視窗
        mock_tk.assert_called_once()
        self.assertIsNotNone(rss_window.window)

    @mock_tk_components
    def test_close_window(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試關閉視窗"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 關閉視窗
        rss_window._close_window()

        # 驗證呼叫 destroy
        mock_window.destroy.assert_called_once()
        self.assertIsNone(rss_window.window)

    def test_close_window_when_already_none(self):
        """測試關閉空視窗"""
        from rss_window import RSSWindow

        rss_window = RSSWindow(self.mock_rss_manager)
        # window 為 None
        rss_window._close_window()

        # 應該不會拋出例外
        self.assertIsNone(rss_window.window)

    # ========== B. 子視圖建立測試 (6 tests) ==========

    @mock_tk_components
    def test_creates_feed_list_view(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試建立 feed 列表視圖"""
        from rss_window import RSSWindow

        mock_root = Mock()
        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 驗證建立 RSSFeedListView
        mock_feed_list_view.assert_called_once()
        call_args = mock_feed_list_view.call_args
        # RSSFeedListView 使用位置參數 (content_frame, rss_manager, on_feed_select_callback=...)
        self.assertEqual(call_args[0][1], self.mock_rss_manager)  # 第二個位置參數
        self.assertIsNotNone(call_args[1]['on_feed_select_callback'])

    @mock_tk_components
    def test_creates_filter_manager(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager_class,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試建立篩選管理器"""
        from rss_window import RSSWindow

        mock_root = Mock()
        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 驗證建立 RSSFilterManager
        mock_filter_manager_class.assert_called_once_with(self.mock_rss_manager)
        self.assertIsNotNone(rss_window.filter_manager)

    @mock_tk_components
    def test_creates_entry_list_view(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試建立文章列表視圖"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_filter_manager_instance = Mock()
        mock_filter_manager.return_value = mock_filter_manager_instance

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 驗證建立 RSSEntryListView
        mock_entry_list_view.assert_called_once()
        call_args = mock_entry_list_view.call_args[0]
        self.assertEqual(call_args[1], self.mock_rss_manager)
        self.assertEqual(call_args[2], mock_filter_manager_instance)

    @mock_tk_components
    def test_creates_preview_view(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試建立預覽視圖"""
        from rss_window import RSSWindow

        mock_root = Mock()
        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 驗證建立 RSSPreviewView
        mock_preview_view.assert_called_once()
        self.assertIsNotNone(rss_window.preview_view)

    @mock_tk_components
    def test_creates_loading_label(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試建立載入標籤"""
        from rss_window import RSSWindow

        mock_root = Mock()
        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 驗證建立 loading label
        self.assertIsNotNone(rss_window.loading_label)

    @mock_tk_components
    def test_all_subviews_initialized(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試所有子視圖初始化"""
        from rss_window import RSSWindow

        mock_root = Mock()
        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 驗證所有子視圖都被初始化
        self.assertIsNotNone(rss_window.feed_list_view)
        self.assertIsNotNone(rss_window.filter_manager)
        self.assertIsNotNone(rss_window.entry_list_view)
        self.assertIsNotNone(rss_window.preview_view)
        self.assertIsNotNone(rss_window.loading_label)

    # ========== C. Feed 選擇和載入測試 (8 tests) ==========

    def test_on_feed_selected(self):
        """測試選擇 feed"""
        from rss_window import RSSWindow

        rss_window = RSSWindow(self.mock_rss_manager)
        rss_window._load_entries = Mock()

        feed_url = 'https://example.com/feed'
        rss_window._on_feed_selected(feed_url)

        # 驗證設定 current_feed_url
        self.assertEqual(rss_window.current_feed_url, feed_url)
        # 驗證呼叫 _load_entries
        rss_window._load_entries.assert_called_once_with(feed_url)

    @mock_tk_components
    def test_load_entries_clears_ui(
        self,
        mock_preview_view,
        mock_entry_list_view_class,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試載入前清空 UI"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        # Mock 子視圖實例
        mock_entry_list_view_instance = Mock()
        mock_preview_view_instance = Mock()
        mock_entry_list_view_class.return_value = mock_entry_list_view_instance
        mock_preview_view.return_value = mock_preview_view_instance

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 載入文章
        feed_url = 'https://example.com/feed'
        rss_window._load_entries(feed_url)

        # 驗證清空 UI
        mock_entry_list_view_instance.clear.assert_called_once()
        mock_preview_view_instance.clear_preview.assert_called_once()

    @mock_tk_components
    def test_load_entries_shows_loading(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試顯示載入中標籤"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        # Mock loading_label
        mock_loading_label = Mock()
        mock_label.return_value = mock_loading_label

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 載入文章
        feed_url = 'https://example.com/feed'
        rss_window._load_entries(feed_url)

        # 驗證顯示載入標籤
        rss_window.loading_label.place.assert_called_once()

    @patch('rss_window.threading.Thread')
    @mock_tk_components
    def test_load_entries_spawns_background_thread(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label,
        mock_thread
    ):
        """測試啟動背景執行緒"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 載入文章
        feed_url = 'https://example.com/feed'
        rss_window._load_entries(feed_url)

        # 驗證建立執行緒
        mock_thread.assert_called_once()
        self.assertTrue(mock_thread.call_args[1]['daemon'])
        # 驗證啟動執行緒
        mock_thread_instance.start.assert_called_once()

    @mock_tk_components
    def test_load_entries_calls_fetch_feed_entries(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試呼叫抓取方法"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        test_entries = [{'id': '1', 'title': 'Test'}]
        self.mock_rss_manager.fetch_feed_entries.return_value = test_entries

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 載入文章並等待執行緒完成
        feed_url = 'https://example.com/feed'

        # 同步執行以避免執行緒問題
        with patch('rss_window.threading.Thread') as mock_thread:
            # 直接執行 target 函數
            def side_effect(*args, **kwargs):
                target = kwargs['target']
                target()
                return Mock()
            mock_thread.side_effect = side_effect

            rss_window._load_entries(feed_url)

        # 驗證呼叫 fetch_feed_entries
        self.mock_rss_manager.fetch_feed_entries.assert_called_once_with(feed_url)

    @mock_tk_components
    def test_update_entries_ui(
        self,
        mock_preview_view,
        mock_entry_list_view_class,
        mock_filter_manager_class,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試更新 UI"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        mock_filter_manager_instance = Mock()
        mock_entry_list_view_instance = Mock()
        mock_filter_manager_class.return_value = mock_filter_manager_instance
        mock_entry_list_view_class.return_value = mock_entry_list_view_instance

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        test_entries = [{'id': '1', 'title': 'Test'}]
        rss_window._update_entries_ui(test_entries)

        # 驗證更新篩選管理器
        mock_filter_manager_instance.set_entries.assert_called_once_with(test_entries)
        # 驗證顯示文章
        mock_entry_list_view_instance.display_entries.assert_called_once_with(test_entries)

    @mock_tk_components
    def test_update_entries_ui_hides_loading(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試隱藏載入中"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        # Mock loading label
        mock_loading_label = Mock()
        mock_label.return_value = mock_loading_label

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        test_entries = [{'id': '1', 'title': 'Test'}]
        rss_window._update_entries_ui(test_entries)

        # 驗證隱藏載入標籤
        rss_window.loading_label.place_forget.assert_called_once()

    @mock_tk_components
    def test_update_entries_ui_with_empty_entries(
        self,
        mock_preview_view,
        mock_entry_list_view_class,
        mock_filter_manager_class,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試更新空文章列表"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        mock_filter_manager_instance = Mock()
        mock_entry_list_view_instance = Mock()
        mock_filter_manager_class.return_value = mock_filter_manager_instance
        mock_entry_list_view_class.return_value = mock_entry_list_view_instance

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 空文章列表
        rss_window._update_entries_ui([])

        # 驗證仍會呼叫相關方法
        mock_filter_manager_instance.set_entries.assert_called_once_with([])
        mock_entry_list_view_instance.display_entries.assert_called_once_with([])

    # ========== D. Entry 選擇測試 (3 tests) ==========

    @mock_tk_components
    def test_on_entry_selected(
        self,
        mock_preview_view_class,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試選擇文章"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        mock_preview_view_instance = Mock()
        mock_preview_view_class.return_value = mock_preview_view_instance

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        test_entry = {'id': '1', 'title': 'Test Entry'}
        rss_window._on_entry_selected(test_entry)

        # 驗證顯示預覽
        mock_preview_view_instance.show_preview.assert_called_once_with(test_entry)

    @mock_tk_components
    def test_on_entry_selected_shows_preview(
        self,
        mock_preview_view_class,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試顯示預覽"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        mock_preview_view_instance = Mock()
        mock_preview_view_class.return_value = mock_preview_view_instance

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        test_entry = {
            'id': '1',
            'title': 'Test Entry',
            'content': 'Test Content'
        }
        rss_window._on_entry_selected(test_entry)

        # 驗證傳遞正確的文章資料
        call_args = mock_preview_view_instance.show_preview.call_args[0]
        self.assertEqual(call_args[0], test_entry)

    @mock_tk_components
    def test_on_entry_selected_with_none(
        self,
        mock_preview_view_class,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試空選擇"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        mock_preview_view_instance = Mock()
        mock_preview_view_class.return_value = mock_preview_view_instance

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 傳入 None
        rss_window._on_entry_selected(None)

        # 仍應呼叫 show_preview
        mock_preview_view_instance.show_preview.assert_called_once_with(None)

    # ========== E. 操作功能測試 (5 tests) ==========

    @patch('rss_window.messagebox.showinfo')
    @patch('rss_window.simpledialog.askstring')
    @mock_tk_components
    def test_add_feed_manual_success(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view_class,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label,
        mock_askstring,
        mock_showinfo
    ):
        """測試成功新增 feed"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        mock_feed_list_view_instance = Mock()
        mock_feed_list_view_class.return_value = mock_feed_list_view_instance

        # 模擬使用者輸入（直接返回字串，這樣 .strip() 才能正常運作）
        mock_askstring.return_value = 'https://example.com/feed  '

        # 模擬成功新增
        self.mock_rss_manager.add_feed.return_value = {
            'success': True,
            'message': '新增成功'
        }

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        rss_window._add_feed_manual()

        # 驗證呼叫 add_feed
        self.mock_rss_manager.add_feed.assert_called_once_with('https://example.com/feed')
        # 驗證顯示成功訊息
        mock_showinfo.assert_called_once()
        # 驗證重新載入訂閱列表
        self.assertEqual(mock_feed_list_view_instance.load_feeds.call_count, 2)  # show() + _add_feed_manual()

    @patch('rss_window.simpledialog.askstring')
    @mock_tk_components
    def test_add_feed_manual_empty_url(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label,
        mock_askstring
    ):
        """測試空 URL"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        # 模擬使用者取消或輸入空字串
        mock_askstring.return_value = None

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        rss_window._add_feed_manual()

        # 驗證不呼叫 add_feed
        self.mock_rss_manager.add_feed.assert_not_called()

    @patch('rss_window.messagebox.showerror')
    @patch('rss_window.simpledialog.askstring')
    @mock_tk_components
    def test_add_feed_manual_failure(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label,
        mock_askstring,
        mock_showerror
    ):
        """測試新增失敗"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        # 模擬使用者輸入（直接返回字串）
        mock_askstring.return_value = '  invalid_url  '

        # 模擬新增失敗
        self.mock_rss_manager.add_feed.return_value = {
            'success': False,
            'message': '無效的 URL'
        }

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        rss_window._add_feed_manual()

        # 驗證呼叫 add_feed
        self.mock_rss_manager.add_feed.assert_called_once_with('invalid_url')
        # 驗證顯示錯誤訊息
        mock_showerror.assert_called_once()

    @mock_tk_components
    def test_refresh_feeds_clears_cache(
        self,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試重新整理清除快取"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        rss_window._refresh_feeds()

        # 驗證清除快取
        self.mock_rss_manager.clear_cache.assert_called_once()

    @mock_tk_components
    @patch('rss_window.messagebox.showinfo')
    def test_refresh_feeds_reloads_current_feed(
        self,
        mock_showinfo,
        mock_preview_view,
        mock_entry_list_view,
        mock_filter_manager,
        mock_feed_list_view,
        mock_toplevel,
        mock_button,
        mock_style,
        mock_frame,
        mock_label
    ):
        """測試重新載入當前 feed"""
        from rss_window import RSSWindow

        mock_root = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window

        rss_window = RSSWindow(self.mock_rss_manager, tk_root=mock_root)
        rss_window.show()

        # 設定當前 feed
        rss_window.current_feed_url = 'https://example.com/feed'
        rss_window._load_entries = Mock()

        rss_window._refresh_feeds()

        # 驗證重新載入
        rss_window._load_entries.assert_called_once_with('https://example.com/feed')
        # 不應顯示完成訊息
        mock_showinfo.assert_not_called()


if __name__ == '__main__':
    unittest.main()
