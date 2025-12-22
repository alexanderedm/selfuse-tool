"""音樂資料夾操作模組

此模組負責處理音樂資料夾的所有操作:
- 新增資料夾
- 重新命名資料夾
- 刪除資料夾
- 顯示資料夾右鍵選單
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from src.core.logger import logger


class MusicFolderActions:
    """音樂資料夾操作類別"""

    def __init__(self, parent_window, file_manager, category_tree, on_reload_library):
        """初始化資料夾操作模組

        Args:
            parent_window: 父視窗實例
            file_manager: MusicFileManager 實例
            category_tree: 分類樹狀視圖實例
            on_reload_library: 重新載入音樂庫的回調函數
        """
        self.parent_window = parent_window
        self.file_manager = file_manager
        self.category_tree = category_tree
        self.on_reload_library = on_reload_library

        logger.info("MusicFolderActions 模組初始化完成")

    def create_new_folder(self):
        """新增資料夾"""
        try:
            # 詢問資料夾名稱
            folder_name = simpledialog.askstring("新增資料夾", "請輸入資料夾名稱:")

            # 檢查是否取消或空名稱
            if not folder_name or not folder_name.strip():
                logger.info("新增資料夾已取消")
                return

            folder_name = folder_name.strip()
            logger.info(f"嘗試新增資料夾: {folder_name}")

            # 使用 MusicFileManager 建立資料夾
            if self.file_manager.create_folder(folder_name):
                # 重新載入音樂庫
                self.on_reload_library()
                messagebox.showinfo("成功", f"資料夾 '{folder_name}' 已建立")
                logger.info(f"資料夾建立成功: {folder_name}")
            else:
                # 建立失敗,檢查原因
                if self.file_manager.folder_exists(folder_name):
                    messagebox.showerror("錯誤", f"資料夾 '{folder_name}' 已存在")
                    logger.warning(f"資料夾已存在: {folder_name}")
                else:
                    messagebox.showerror("錯誤", "建立資料夾失敗")
                    logger.error(f"建立資料夾失敗: {folder_name}")

        except Exception as e:
            logger.error(f"新增資料夾時發生錯誤: {e}")
            messagebox.showerror("錯誤", f"新增資料夾時發生錯誤:\n{str(e)}")

    def rename_folder(self, item_id, old_name):
        """重新命名資料夾

        Args:
            item_id: 樹狀結構項目 ID
            old_name: 舊的資料夾名稱
        """
        try:
            # 詢問新的資料夾名稱
            new_name = simpledialog.askstring(
                "重新命名資料夾",
                "請輸入新的資料夾名稱:",
                initialvalue=old_name
            )

            # 檢查是否取消、空名稱或名稱相同
            if not new_name or not new_name.strip() or new_name == old_name:
                logger.info("重新命名資料夾已取消")
                return

            new_name = new_name.strip()
            logger.info(f"嘗試重新命名資料夾: {old_name} -> {new_name}")

            # 使用 MusicFileManager 重新命名資料夾
            if self.file_manager.rename_folder(old_name, new_name):
                # 重新載入音樂庫
                self.on_reload_library()
                messagebox.showinfo("成功", f"資料夾已重新命名為 '{new_name}'")
                logger.info(f"資料夾重新命名成功: {old_name} -> {new_name}")
            else:
                # 重新命名失敗,檢查原因
                if self.file_manager.folder_exists(new_name):
                    messagebox.showerror("錯誤", f"資料夾 '{new_name}' 已存在")
                    logger.warning(f"資料夾已存在: {new_name}")
                else:
                    messagebox.showerror("錯誤", "重新命名資料夾失敗")
                    logger.error(f"重新命名資料夾失敗: {old_name} -> {new_name}")

        except Exception as e:
            logger.error(f"重新命名資料夾時發生錯誤: {e}")
            messagebox.showerror("錯誤", f"重新命名資料夾時發生錯誤:\n{str(e)}")

    def delete_folder(self, item_id, folder_name):
        """刪除資料夾

        Args:
            item_id: 樹狀結構項目 ID
            folder_name: 資料夾名稱
        """
        try:
            # 確認刪除
            result = messagebox.askyesno(
                "確認刪除",
                f"確定要刪除資料夾 '{folder_name}' 及其所有內容嗎?\n\n此操作無法復原!"
            )

            if not result:
                logger.info(f"刪除資料夾已取消: {folder_name}")
                return

            logger.info(f"嘗試刪除資料夾: {folder_name}")

            # 使用 MusicFileManager 刪除資料夾
            if self.file_manager.delete_folder(folder_name):
                # 重新載入音樂庫
                self.on_reload_library()
                messagebox.showinfo("成功", f"資料夾 '{folder_name}' 已刪除")
                logger.info(f"資料夾刪除成功: {folder_name}")
            else:
                messagebox.showerror("錯誤", "刪除資料夾失敗")
                logger.error(f"刪除資料夾失敗: {folder_name}")

        except Exception as e:
            logger.error(f"刪除資料夾時發生錯誤: {e}")
            messagebox.showerror("錯誤", f"刪除資料夾時發生錯誤:\n{str(e)}")

    def show_folder_context_menu(self, event):
        """顯示資料夾右鍵選單

        Args:
            event: 滑鼠事件
        """
        try:
            # 選中右鍵點擊的項目
            item_id = self.category_tree.identify_row(event.y)

            if not item_id:
                # 點擊空白處,只顯示新增資料夾選單
                menu = tk.Menu(self.parent_window, tearoff=0, bg="#2d2d2d", fg="#e0e0e0")
                menu.add_command(label="➕ 新增資料夾", command=self.create_new_folder)
                menu.post(event.x_root, event.y_root)
                return

            # 選中該項目
            self.category_tree.selection_set(item_id)
            item_values = self.category_tree.item(item_id, 'values')

            if not item_values:
                return

            item_type = item_values[0]

            # 建立右鍵選單
            menu = tk.Menu(self.parent_window, tearoff=0, bg="#2d2d2d", fg="#e0e0e0")

            if item_type == 'all':
                # 所有歌曲節點:只能新增資料夾
                menu.add_command(label="➕ 新增資料夾", command=self.create_new_folder)
            elif item_type.startswith('folder:'):
                # 資料夾節點:顯示重新命名、刪除、新增資料夾
                category_name = item_type.replace('folder:', '')
                menu.add_command(
                    label="✏️ 重新命名",
                    command=lambda: self.rename_folder(item_id, category_name)
                )
                menu.add_command(
                    label="🗑️ 刪除資料夾",
                    command=lambda: self.delete_folder(item_id, category_name)
                )
                menu.add_separator()
                menu.add_command(label="➕ 新增資料夾", command=self.create_new_folder)

            # 顯示選單
            menu.post(event.x_root, event.y_root)

        except Exception as e:
            logger.error(f"顯示資料夾右鍵選單時發生錯誤: {e}")
