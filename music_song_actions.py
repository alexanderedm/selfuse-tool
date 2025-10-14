"""音樂歌曲操作模組 - 歌曲的右鍵選單和操作邏輯"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from logger import logger


class MusicSongActions:
    """音樂歌曲操作類別 - 負責歌曲的各種操作(播放、刪除、移動、加入播放列表等)"""

    def __init__(self, parent_window, music_manager, file_manager,
                 on_play_song=None, on_reload_library=None):
        """初始化音樂歌曲操作

        Args:
            parent_window: 父視窗
            music_manager: 音樂管理器實例
            file_manager: 檔案管理器實例
            on_play_song: 播放歌曲回調函數 (song, playlist, index)
            on_reload_library: 重新載入音樂庫回調函數
        """
        self.parent_window = parent_window
        self.music_manager = music_manager
        self.file_manager = file_manager
        self.on_play_song = on_play_song
        self.on_reload_library = on_reload_library

        # 顏色主題
        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.accent_color = "#0078d4"
        self.text_color = "#e0e0e0"
        self.text_secondary = "#a0a0a0"

    def play_song_from_tree(self, song):
        """從樹狀結構播放歌曲

        Args:
            song (dict): 歌曲資訊
        """
        if not song:
            return

        # 載入所屬資料夾的所有歌曲到播放列表
        category = song.get('category', '')
        playlist = []
        index = 0

        if category:
            playlist = self.music_manager.get_songs_by_category(category)
            # 找到該歌曲在播放列表中的索引
            for i, s in enumerate(playlist):
                if s['id'] == song['id']:
                    index = i
                    break

        # 觸發播放回調
        if self.on_play_song:
            self.on_play_song(song, playlist, index)

        logger.info(f"從樹狀結構播放歌曲: {song.get('title', 'Unknown')}")

    def delete_song(self, song):
        """刪除歌曲

        Args:
            song (dict): 歌曲資訊

        Returns:
            bool: 是否刪除成功
        """
        # 確認刪除
        result = messagebox.askyesno(
            "確認刪除",
            f"確定要刪除歌曲 '{song['title']}' 嗎?\n\n此操作無法復原!",
            parent=self.parent_window
        )

        if not result:
            return False

        # 使用 MusicFileManager 刪除歌曲
        if self.file_manager.delete_song(song):
            # 重新載入音樂庫
            if self.on_reload_library:
                self.on_reload_library()

            messagebox.showinfo(
                "成功",
                f"歌曲 '{song['title']}' 已刪除",
                parent=self.parent_window
            )

            logger.info(f"歌曲已刪除: {song.get('title', 'Unknown')}")
            return True
        else:
            messagebox.showerror(
                "錯誤",
                "刪除歌曲失敗",
                parent=self.parent_window
            )

            logger.error(f"刪除歌曲失敗: {song.get('title', 'Unknown')}")
            return False

    def move_song_to_category(self, song):
        """移動歌曲到不同分類

        Args:
            song (dict): 歌曲資訊
        """
        # 取得所有分類
        categories = self.music_manager.get_all_categories()
        if not categories:
            messagebox.showwarning(
                "警告",
                "沒有可用的分類",
                parent=self.parent_window
            )
            return

        # 取得當前分類
        current_category = song.get('category', '')

        # 從分類列表中移除當前分類
        available_categories = [c for c in categories if c != current_category]

        if not available_categories:
            messagebox.showinfo(
                "提示",
                "沒有其他分類可以移動到。\n請先建立新的分類資料夾。",
                parent=self.parent_window
            )
            return

        # 顯示移動對話框
        self._show_move_dialog(song, current_category, available_categories)

    def _show_move_dialog(self, song, current_category, available_categories):
        """顯示移動歌曲對話框

        Args:
            song (dict): 歌曲資訊
            current_category (str): 當前分類
            available_categories (list): 可用的分類列表
        """
        # 建立分類選擇對話框
        move_dialog = tk.Toplevel(self.parent_window)
        move_dialog.title("移動歌曲")
        move_dialog.geometry("450x300")
        move_dialog.configure(bg=self.bg_color)
        move_dialog.resizable(False, False)
        move_dialog.transient(self.parent_window)
        move_dialog.grab_set()

        main_frame = tk.Frame(move_dialog, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        tk.Label(
            main_frame,
            text="移動歌曲到...",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(0, 10))

        # 歌曲資訊
        tk.Label(
            main_frame,
            text=f"歌曲: {song['title'][:40]}{'...' if len(song['title']) > 40 else ''}",
            font=("Microsoft JhengHei UI", 9),
            bg=self.bg_color,
            fg=self.text_secondary,
            wraplength=400,
            justify=tk.LEFT
        ).pack(pady=(0, 5))

        tk.Label(
            main_frame,
            text=f"目前位置: {current_category}",
            font=("Microsoft JhengHei UI", 9),
            bg=self.bg_color,
            fg=self.text_secondary
        ).pack(pady=(0, 20))

        # 選擇目標分類
        tk.Label(
            main_frame,
            text="選擇目標資料夾:",
            font=("Microsoft JhengHei UI", 10),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(anchor=tk.W, pady=(0, 5))

        # 下拉選單
        category_var = tk.StringVar(value=available_categories[0])

        style = ttk.Style()
        style.configure(
            "Move.TCombobox",
            fieldbackground=self.card_bg,
            background=self.card_bg,
            foreground=self.text_color
        )

        category_combo = ttk.Combobox(
            main_frame,
            textvariable=category_var,
            values=available_categories,
            font=("Microsoft JhengHei UI", 10),
            state="readonly",
            style="Move.TCombobox"
        )
        category_combo.pack(fill=tk.X, ipady=5, pady=(0, 20))

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack()

        def confirm_move():
            target_category = category_var.get()
            if not target_category:
                messagebox.showwarning(
                    "警告",
                    "請選擇目標資料夾",
                    parent=move_dialog
                )
                return

            # 關閉對話框
            move_dialog.destroy()

            # 使用 MusicFileManager 執行移動操作
            if self.file_manager.move_song(song, target_category):
                # 重新載入音樂庫
                if self.on_reload_library:
                    self.on_reload_library()

                messagebox.showinfo(
                    "成功",
                    f"歌曲已移動到分類: {target_category}",
                    parent=self.parent_window
                )

                logger.info(f"歌曲已移動: {song.get('title', 'Unknown')} -> {target_category}")
            else:
                # 取得檔名用於錯誤訊息
                audio_filename = os.path.basename(song['audio_path'])
                target_audio_path = os.path.join(
                    self.music_manager.music_root_path,
                    target_category,
                    audio_filename
                )
                if os.path.exists(target_audio_path):
                    messagebox.showerror(
                        "錯誤",
                        f"目標資料夾中已存在同名檔案:\n{audio_filename}",
                        parent=self.parent_window
                    )
                else:
                    messagebox.showerror(
                        "錯誤",
                        "移動歌曲失敗",
                        parent=self.parent_window
                    )

                logger.error(f"移動歌曲失敗: {song.get('title', 'Unknown')}")

        move_btn = tk.Button(
            button_frame,
            text="移動",
            font=("Microsoft JhengHei UI", 10),
            bg=self.accent_color,
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=30,
            pady=8,
            command=confirm_move
        )
        move_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=move_dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
