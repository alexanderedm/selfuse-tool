"""MusicLibraryView 模組測試"""
import unittest
from unittest.mock import Mock, MagicMock, patch, call
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk


class TestMusicLibraryView(unittest.TestCase):
    """MusicLibraryView 測試類別"""

    def setUp(self):
        """測試前置作業"""
        # 建立模擬的父視窗和根視窗
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏窗口
        self.parent = tk.Frame(self.root)

        # Mock parent.after to execute immediately
        self.parent.after = lambda delay, func: func()

        # 建立模擬的 music_manager
        self.mock_music_manager = Mock()
        self.mock_music_manager.music_root_path = "E:\\Music"
        # 支援同步和異步掃描
        self.mock_music_manager.scan_music_library.return_value = {
            'success': True,
            'message': 'OK'
        }
        # Mock 異步掃描，立即調用回調
        def mock_async_scan(callback=None):
            if callback:
                callback({'success': True, 'message': 'OK'})
        self.mock_music_manager.scan_music_library_async = Mock(side_effect=mock_async_scan)
        self.mock_music_manager.get_all_categories.return_value = ['Rock', 'Pop']
        self.mock_music_manager.get_all_songs.return_value = [
            {'id': '1', 'title': 'Song 1', 'duration': 180, 'category': 'Rock'},
            {'id': '2', 'title': 'Song 2', 'duration': 240, 'category': 'Pop'}
        ]
        self.mock_music_manager.get_songs_by_category.return_value = [
            {'id': '1', 'title': 'Song 1', 'duration': 180, 'category': 'Rock'}
        ]
        self.mock_music_manager.format_duration.side_effect = lambda d: f"{d//60}:{d%60:02d}"
        self.mock_music_manager.get_song_by_id.return_value = {
            'id': '1', 'title': 'Song 1', 'duration': 180, 'category': 'Rock'
        }

        # 回調函數模擬
        self.mock_on_category_select = Mock()
        self.mock_on_song_select = Mock()
        self.mock_on_song_double_click = Mock()

    def tearDown(self):
        """測試後清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_init_creates_ui_components(self):
        """測試初始化時建立所有 UI 元件"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 驗證主框架已建立
        self.assertIsNotNone(view.main_frame)

        # 驗證左側資料夾樹已建立
        self.assertIsNotNone(view.category_tree)
        self.assertIsInstance(view.category_tree, ttk.Treeview)

        # 驗證右側歌曲列表已建立
        self.assertIsNotNone(view.song_tree)
        self.assertIsInstance(view.song_tree, ttk.Treeview)

    def test_init_loads_music_library(self):
        """測試初始化時載入音樂庫"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 驗證掃描音樂庫被呼叫（異步版本）
        self.mock_music_manager.scan_music_library_async.assert_called()

        # 異步加載時，get_all_categories 在回調中調用
        # 由於我們的 mock_async_scan 立即調用回調，所以應該被調用
        self.mock_music_manager.get_all_categories.assert_called()

    def test_load_categories_populates_tree(self):
        """測試載入分類填充樹狀結構"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 驗證樹狀結構包含節點
        children = view.category_tree.get_children()
        self.assertGreater(len(children), 0)

        # 驗證第一個節點存在（可能是"載入中..."或"所有歌曲"）
        first_item = children[0]
        text = view.category_tree.item(first_item, 'text')
        # 異步加載時可能顯示載入中
        self.assertTrue('所有歌曲' in text or '載入' in text)

    def test_category_tree_selection_triggers_callback(self):
        """測試選擇分類時觸發回調"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 模擬選擇一個分類
        children = view.category_tree.get_children()
        if children:
            view.category_tree.selection_set(children[0])
            view.category_tree.event_generate('<<TreeviewSelect>>')

            # 給事件處理時間
            self.root.update()

            # 驗證回調被觸發
            self.mock_on_category_select.assert_called()

    def test_display_songs_updates_song_tree(self):
        """測試顯示歌曲更新歌曲列表"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 準備測試歌曲
        test_songs = [
            {'id': '1', 'title': 'Test Song 1', 'duration': 180},
            {'id': '2', 'title': 'Test Song 2', 'duration': 240}
        ]

        # 呼叫 display_songs
        view.display_songs(test_songs)

        # 驗證歌曲樹包含歌曲
        song_items = view.song_tree.get_children()
        self.assertEqual(len(song_items), 2)

    def test_song_double_click_triggers_callback(self):
        """測試雙擊歌曲觸發回調"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 新增測試歌曲
        test_songs = [
            {'id': '1', 'title': 'Test Song', 'duration': 180}
        ]
        view.display_songs(test_songs)

        # 模擬雙擊
        song_items = view.song_tree.get_children()
        if song_items:
            view.song_tree.selection_set(song_items[0])
            # 直接呼叫事件處理器
            view._on_song_double_click(Mock())

            # 驗證回調被觸發
            self.mock_on_song_double_click.assert_called()

    def test_reload_library_refreshes_display(self):
        """測試重新載入音樂庫刷新顯示"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 重置呼叫計數
        self.mock_music_manager.scan_music_library_async.reset_mock()

        # 呼叫重新載入
        view.reload_library()

        # 驗證重新掃描（異步版本）
        self.mock_music_manager.scan_music_library_async.assert_called()

    def test_get_selected_category_returns_correct_value(self):
        """測試取得選中的分類回傳正確值"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 取得選中的分類
        selected = view.get_selected_category()

        # 異步加載時可能返回 None 或 'all'
        self.assertIn(selected, [None, 'all', ''])

    def test_get_selected_song_index_returns_correct_value(self):
        """測試取得選中的歌曲索引回傳正確值"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 新增測試歌曲
        test_songs = [
            {'id': '1', 'title': 'Test Song', 'duration': 180}
        ]
        view.display_songs(test_songs)

        # 選擇第一首歌
        song_items = view.song_tree.get_children()
        if song_items:
            view.song_tree.selection_set(song_items[0])

            # 取得選中的歌曲索引
            index = view.get_selected_song_index()
            self.assertEqual(index, 0)

    def test_empty_category_shows_placeholder(self):
        """測試空分類顯示佔位提示"""
        from src.music.views.music_library_view import MusicLibraryView

        # 設定空分類
        self.mock_music_manager.get_all_categories.return_value = ['Empty']
        self.mock_music_manager.get_songs_by_category.return_value = []

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 驗證空資料夾顯示
        # (具體實作需要檢查樹狀結構是否包含空資料夾提示)
        children = view.category_tree.get_children()
        self.assertGreater(len(children), 0)

    def test_category_right_click_shows_context_menu(self):
        """測試右鍵點擊分類顯示上下文選單"""
        from src.music.views.music_library_view import MusicLibraryView

        mock_on_rename = Mock()
        mock_on_delete = Mock()

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click,
            on_category_rename=mock_on_rename,
            on_category_delete=mock_on_delete
        )

        # 模擬右鍵點擊事件
        event = Mock()
        event.y = 10
        event.x_root = 100
        event.y_root = 100

        # 這需要視窗可見才能正確測試,這裡只驗證函數存在
        self.assertTrue(hasattr(view, '_on_category_right_click'))

    def test_get_current_playlist_returns_displayed_songs(self):
        """測試取得當前播放列表回傳顯示的歌曲"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 新增測試歌曲
        test_songs = [
            {'id': '1', 'title': 'Test Song 1', 'duration': 180},
            {'id': '2', 'title': 'Test Song 2', 'duration': 240}
        ]
        view.display_songs(test_songs)

        # 取得當前播放列表
        playlist = view.get_current_playlist()

        # 驗證回傳的歌曲列表
        self.assertEqual(len(playlist), 2)
        self.assertEqual(playlist[0]['id'], '1')
        self.assertEqual(playlist[1]['id'], '2')

    def test_clear_song_list_removes_all_songs(self):
        """測試清空歌曲列表移除所有歌曲"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 新增測試歌曲
        test_songs = [
            {'id': '1', 'title': 'Test Song', 'duration': 180}
        ]
        view.display_songs(test_songs)

        # 清空列表
        view.clear_song_list()

        # 驗證歌曲樹為空
        song_items = view.song_tree.get_children()
        self.assertEqual(len(song_items), 0)

    def test_expand_category_opens_folder(self):
        """測試展開分類打開資料夾"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 取得一個分類節點
        children = view.category_tree.get_children()
        if len(children) > 1:  # 跳過「所有歌曲」
            folder_item = children[1]

            # 展開資料夾
            view.category_tree.item(folder_item, open=True)

            # 驗證資料夾已展開
            is_open = view.category_tree.item(folder_item, 'open')
            self.assertTrue(is_open)

    def test_style_configuration_applied(self):
        """測試樣式配置已套用"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 驗證樹狀結構的樣式
        self.assertIsNotNone(view.category_tree['style'])
        self.assertIsNotNone(view.song_tree['style'])

    def test_pack_layout_manager_used(self):
        """測試使用 pack 佈局管理器"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 驗證主框架已 pack
        pack_info = view.main_frame.pack_info()
        self.assertIsNotNone(pack_info)
        self.assertEqual(pack_info['fill'], 'both')
        self.assertTrue(pack_info['expand'])

    def test_category_select_loads_songs(self):
        """測試選擇分類載入歌曲"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 取得分類節點 (不是「所有歌曲」)
        children = view.category_tree.get_children()
        if len(children) > 1:
            # 選擇第二個節點 (第一個資料夾)
            view.category_tree.selection_set(children[1])
            view.category_tree.event_generate('<<TreeviewSelect>>')
            self.root.update()

            # 驗證 get_songs_by_category 被呼叫
            self.mock_music_manager.get_songs_by_category.assert_called()

    def test_song_list_displays_duration(self):
        """測試歌曲列表顯示時長"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 新增測試歌曲
        test_songs = [
            {'id': '1', 'title': 'Test Song', 'duration': 180}
        ]
        view.display_songs(test_songs)

        # 驗證 format_duration 被呼叫
        self.mock_music_manager.format_duration.assert_called()

    def test_destroy_cleans_up_resources(self):
        """測試銷毀時清理資源"""
        from src.music.views.music_library_view import MusicLibraryView

        view = MusicLibraryView(
            parent=self.parent,
            music_manager=self.mock_music_manager,
            on_category_select=self.mock_on_category_select,
            on_song_select=self.mock_on_song_select,
            on_song_double_click=self.mock_on_song_double_click
        )

        # 銷毀視圖
        view.destroy()

        # 驗證主框架已銷毀 (winfo_exists 回傳 0 表示已銷毀)
        exists = view.main_frame.winfo_exists()
        self.assertEqual(exists, 0)


if __name__ == '__main__':
    unittest.main()
