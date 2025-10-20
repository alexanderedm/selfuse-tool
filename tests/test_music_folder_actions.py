"""MusicFolderActions 模組測試"""
import unittest
from unittest.mock import Mock, MagicMock, patch, call
import tkinter as tk
from tkinter import messagebox, simpledialog


class TestMusicFolderActions(unittest.TestCase):
    """MusicFolderActions 類別測試"""

    def setUp(self):
        """測試前的設定"""
        # 建立 Mock 物件
        self.mock_window = Mock(spec=tk.Tk)
        self.mock_file_manager = Mock()
        self.mock_on_reload = Mock()

        # 建立 category_tree mock
        self.mock_category_tree = Mock()

        # 匯入模組
        from src.music.actions.music_folder_actions import MusicFolderActions

        # 建立實例
        self.folder_actions = MusicFolderActions(
            parent_window=self.mock_window,
            file_manager=self.mock_file_manager,
            category_tree=self.mock_category_tree,
            on_reload_library=self.mock_on_reload
        )

    def test_01_initialization(self):
        """測試初始化"""
        self.assertIsNotNone(self.folder_actions)
        self.assertEqual(self.folder_actions.parent_window, self.mock_window)
        self.assertEqual(self.folder_actions.file_manager, self.mock_file_manager)
        self.assertEqual(self.folder_actions.category_tree, self.mock_category_tree)
        self.assertEqual(self.folder_actions.on_reload_library, self.mock_on_reload)

    @patch('src.music.actions.music_folder_actions.simpledialog.askstring')
    @patch('src.music.actions.music_folder_actions.messagebox.showinfo')
    def test_02_create_folder_success(self, mock_showinfo, mock_askstring):
        """測試新增資料夾 - 成功"""
        # 設定回傳值
        mock_askstring.return_value = "New Folder"
        self.mock_file_manager.create_folder.return_value = True

        # 執行
        self.folder_actions.create_new_folder()

        # 驗證
        mock_askstring.assert_called_once()
        self.mock_file_manager.create_folder.assert_called_once_with("New Folder")
        self.mock_on_reload.assert_called_once()
        mock_showinfo.assert_called_once()

    @patch('src.music.actions.music_folder_actions.simpledialog.askstring')
    def test_03_create_folder_cancel(self, mock_askstring):
        """測試新增資料夾 - 取消"""
        # 設定回傳值 (None = 取消)
        mock_askstring.return_value = None

        # 執行
        self.folder_actions.create_new_folder()

        # 驗證 - 不應該呼叫 create_folder
        self.mock_file_manager.create_folder.assert_not_called()
        self.mock_on_reload.assert_not_called()

    @patch('src.music.actions.music_folder_actions.simpledialog.askstring')
    def test_04_create_folder_empty_name(self, mock_askstring):
        """測試新增資料夾 - 空名稱"""
        # 設定回傳值
        mock_askstring.return_value = "   "

        # 執行
        self.folder_actions.create_new_folder()

        # 驗證 - 不應該呼叫 create_folder
        self.mock_file_manager.create_folder.assert_not_called()
        self.mock_on_reload.assert_not_called()

    @patch('src.music.actions.music_folder_actions.simpledialog.askstring')
    @patch('src.music.actions.music_folder_actions.messagebox.showerror')
    def test_05_create_folder_already_exists(self, mock_showerror, mock_askstring):
        """測試新增資料夾 - 已存在"""
        # 設定回傳值
        mock_askstring.return_value = "Existing"
        self.mock_file_manager.create_folder.return_value = False
        self.mock_file_manager.folder_exists.return_value = True

        # 執行
        self.folder_actions.create_new_folder()

        # 驗證
        self.mock_file_manager.create_folder.assert_called_once()
        self.mock_on_reload.assert_not_called()
        mock_showerror.assert_called_once()

    @patch('src.music.actions.music_folder_actions.simpledialog.askstring')
    @patch('src.music.actions.music_folder_actions.messagebox.showinfo')
    def test_06_rename_folder_success(self, mock_showinfo, mock_askstring):
        """測試重新命名資料夾 - 成功"""
        # 設定回傳值
        mock_askstring.return_value = "New Name"
        self.mock_file_manager.rename_folder.return_value = True

        # 執行
        self.folder_actions.rename_folder("item1", "Old Name")

        # 驗證
        mock_askstring.assert_called_once()
        self.mock_file_manager.rename_folder.assert_called_once_with("Old Name", "New Name")
        self.mock_on_reload.assert_called_once()
        mock_showinfo.assert_called_once()

    @patch('src.music.actions.music_folder_actions.simpledialog.askstring')
    def test_07_rename_folder_cancel(self, mock_askstring):
        """測試重新命名資料夾 - 取消"""
        # 設定回傳值
        mock_askstring.return_value = None

        # 執行
        self.folder_actions.rename_folder("item1", "Old Name")

        # 驗證
        self.mock_file_manager.rename_folder.assert_not_called()
        self.mock_on_reload.assert_not_called()

    @patch('src.music.actions.music_folder_actions.simpledialog.askstring')
    def test_08_rename_folder_same_name(self, mock_askstring):
        """測試重新命名資料夾 - 相同名稱"""
        # 設定回傳值
        mock_askstring.return_value = "Old Name"

        # 執行
        self.folder_actions.rename_folder("item1", "Old Name")

        # 驗證
        self.mock_file_manager.rename_folder.assert_not_called()
        self.mock_on_reload.assert_not_called()

    @patch('src.music.actions.music_folder_actions.simpledialog.askstring')
    @patch('src.music.actions.music_folder_actions.messagebox.showerror')
    def test_09_rename_folder_already_exists(self, mock_showerror, mock_askstring):
        """測試重新命名資料夾 - 新名稱已存在"""
        # 設定回傳值
        mock_askstring.return_value = "Existing"
        self.mock_file_manager.rename_folder.return_value = False
        self.mock_file_manager.folder_exists.return_value = True

        # 執行
        self.folder_actions.rename_folder("item1", "Old Name")

        # 驗證
        self.mock_file_manager.rename_folder.assert_called_once()
        self.mock_on_reload.assert_not_called()
        mock_showerror.assert_called_once()

    @patch('src.music.actions.music_folder_actions.messagebox.askyesno')
    @patch('src.music.actions.music_folder_actions.messagebox.showinfo')
    def test_10_delete_folder_success(self, mock_showinfo, mock_askyesno):
        """測試刪除資料夾 - 成功"""
        # 設定回傳值
        mock_askyesno.return_value = True
        self.mock_file_manager.delete_folder.return_value = True

        # 執行
        self.folder_actions.delete_folder("item1", "Test Folder")

        # 驗證
        mock_askyesno.assert_called_once()
        self.mock_file_manager.delete_folder.assert_called_once_with("Test Folder")
        self.mock_on_reload.assert_called_once()
        mock_showinfo.assert_called_once()

    @patch('src.music.actions.music_folder_actions.messagebox.askyesno')
    def test_11_delete_folder_cancel(self, mock_askyesno):
        """測試刪除資料夾 - 取消"""
        # 設定回傳值
        mock_askyesno.return_value = False

        # 執行
        self.folder_actions.delete_folder("item1", "Test Folder")

        # 驗證
        self.mock_file_manager.delete_folder.assert_not_called()
        self.mock_on_reload.assert_not_called()

    @patch('src.music.actions.music_folder_actions.messagebox.askyesno')
    @patch('src.music.actions.music_folder_actions.messagebox.showerror')
    def test_12_delete_folder_failed(self, mock_showerror, mock_askyesno):
        """測試刪除資料夾 - 失敗"""
        # 設定回傳值
        mock_askyesno.return_value = True
        self.mock_file_manager.delete_folder.return_value = False

        # 執行
        self.folder_actions.delete_folder("item1", "Test Folder")

        # 驗證
        self.mock_file_manager.delete_folder.assert_called_once()
        self.mock_on_reload.assert_not_called()
        mock_showerror.assert_called_once()

    @patch('src.music.actions.music_folder_actions.tk.Menu')
    def test_13_show_folder_context_menu_on_empty(self, mock_menu_class):
        """測試右鍵選單 - 空白處"""
        # 設定 mock
        mock_menu = Mock()
        mock_menu_class.return_value = mock_menu
        self.mock_category_tree.identify_row.return_value = ""

        # 建立 mock event
        mock_event = Mock()
        mock_event.y = 100
        mock_event.x_root = 200
        mock_event.y_root = 300

        # 執行
        self.folder_actions.show_folder_context_menu(mock_event)

        # 驗證
        mock_menu.add_command.assert_called_once()
        mock_menu.post.assert_called_once_with(200, 300)

    @patch('src.music.actions.music_folder_actions.tk.Menu')
    def test_14_show_folder_context_menu_on_all_songs(self, mock_menu_class):
        """測試右鍵選單 - 所有歌曲節點"""
        # 設定 mock
        mock_menu = Mock()
        mock_menu_class.return_value = mock_menu
        self.mock_category_tree.identify_row.return_value = "item1"
        # 修正：使用 side_effect 來回傳正確的 values

        def item_side_effect(item_id, option=None):
            if option == 'values':
                return ('all',)
            return {'values': ('all',)}

        self.mock_category_tree.item.side_effect = item_side_effect

        # 建立 mock event
        mock_event = Mock()
        mock_event.y = 100
        mock_event.x_root = 200
        mock_event.y_root = 300

        # 執行
        self.folder_actions.show_folder_context_menu(mock_event)

        # 驗證
        mock_menu.add_command.assert_called_once()
        mock_menu.post.assert_called_once()

    @patch('src.music.actions.music_folder_actions.tk.Menu')
    def test_15_show_folder_context_menu_on_folder(self, mock_menu_class):
        """測試右鍵選單 - 資料夾節點"""
        # 設定 mock
        mock_menu = Mock()
        mock_menu_class.return_value = mock_menu
        self.mock_category_tree.identify_row.return_value = "item1"
        # 修正：使用 side_effect 來回傳正確的 values

        def item_side_effect(item_id, option=None):
            if option == 'values':
                return ('folder:MyFolder',)
            return {'values': ('folder:MyFolder',)}

        self.mock_category_tree.item.side_effect = item_side_effect

        # 建立 mock event
        mock_event = Mock()
        mock_event.y = 100
        mock_event.x_root = 200
        mock_event.y_root = 300

        # 執行
        self.folder_actions.show_folder_context_menu(mock_event)

        # 驗證 - 應該有 3 個命令：重新命名、刪除、新增
        self.assertEqual(mock_menu.add_command.call_count, 3)
        mock_menu.add_separator.assert_called_once()
        mock_menu.post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
