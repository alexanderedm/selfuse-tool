"""音樂庫視圖模組 - 資料夾樹和歌曲列表"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from src.core.logger import logger


class MusicLibraryView:
    """音樂庫視圖類別 - 負責顯示資料夾樹和歌曲列表"""

    def __init__(self, parent, music_manager, on_category_select=None,
                 on_song_select=None, on_song_double_click=None,
                 on_category_rename=None, on_category_delete=None):
        """初始化音樂庫視圖

        Args:
            parent: 父視窗
            music_manager: 音樂管理器實例
            on_category_select: 分類選擇回調函數
            on_song_select: 歌曲選擇回調函數
            on_song_double_click: 歌曲雙擊回調函數
            on_category_rename: 分類重命名回調函數
            on_category_delete: 分類刪除回調函數
        """
        self.parent = parent
        self.music_manager = music_manager
        self.on_category_select = on_category_select
        self.on_song_select = on_song_select
        self.on_song_double_click = on_song_double_click
        self.on_category_rename = on_category_rename
        self.on_category_delete = on_category_delete

        # 當前播放列表
        self.current_playlist = []

        # 排序狀態
        self.sort_by = "歌曲名稱"
        self.ascending = True

        # 拖放狀態
        self.drag_data = None
        self.drag_start_index = None

        # 顏色主題
        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.accent_color = "#0078d4"
        self.text_color = "#e0e0e0"
        self.text_secondary = "#a0a0a0"
        self.header_bg = "#0d47a1"

        # 建立主框架
        self.main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 排序按鈕的引用
        self.order_button = None

        # 建立 UI 元件
        self._create_ui()

        # 載入音樂庫
        self._load_music_library()

    def _create_ui(self):
        """建立 UI 元件"""
        # 左側:資料夾樹狀結構 (使用 CustomTkinter 框架 + ttk.Treeview)
        left_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=15,
            fg_color=self.card_bg
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.configure(width=350)

        # 標題
        category_header = ctk.CTkLabel(
            left_frame,
            text="📂 資料夾",
            font=("Microsoft JhengHei UI", 12, "bold"),
            text_color="white"
        )
        category_header.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Treeview 框架 (內嵌 ttk.Treeview)
        tree_frame = tk.Frame(left_frame, bg=self.card_bg)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        category_scroll = tk.Scrollbar(tree_frame)
        category_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Music.Treeview",
            background=self.card_bg,
            foreground=self.text_color,
            fieldbackground=self.card_bg,
            borderwidth=0,
            rowheight=28,
            font=("Microsoft JhengHei UI", 10)
        )
        style.configure("Music.Treeview.Heading", background=self.header_bg, foreground="white")
        style.map('Music.Treeview', background=[('selected', self.accent_color)])

        self.category_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=category_scroll.set,
            style="Music.Treeview",
            selectmode='browse',
            show='tree'
        )
        self.category_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        category_scroll.config(command=self.category_tree.yview)

        # 綁定事件
        self.category_tree.bind('<<TreeviewSelect>>', self._on_category_select_internal)
        self.category_tree.bind('<Button-3>', self._on_category_right_click)
        self.category_tree.bind('<Double-1>', self._on_category_double_click_internal)

        # 右側:歌曲列表 (使用 CustomTkinter 框架 + ttk.Treeview)
        right_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=15,
            fg_color=self.card_bg
        )
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 標題
        song_header = ctk.CTkLabel(
            right_frame,
            text="🎵 歌曲列表",
            font=("Microsoft JhengHei UI", 12, "bold"),
            text_color="white"
        )
        song_header.pack(fill=tk.X, padx=10, pady=(10, 5))

        # 排序控制區
        self._create_sort_controls(right_frame)

        # 建立 Treeview 用於歌曲列表
        song_tree_frame = tk.Frame(right_frame, bg=self.card_bg)
        song_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        song_scroll = tk.Scrollbar(song_tree_frame)
        song_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style.configure(
            "Song.Treeview",
            background=self.card_bg,
            foreground=self.text_color,
            fieldbackground=self.card_bg,
            borderwidth=0,
            rowheight=25
        )
        style.configure(
            "Song.Treeview.Heading",
            background=self.header_bg,
            foreground="white",
            font=("Microsoft JhengHei UI", 10, "bold")
        )
        style.map('Song.Treeview', background=[('selected', self.accent_color)])

        # 建立 Treeview,包含標題、藝術家和時長三個欄位
        self.song_tree = ttk.Treeview(
            song_tree_frame,
            columns=('title', 'artist', 'duration'),
            show='headings',
            yscrollcommand=song_scroll.set,
            style="Song.Treeview",
            selectmode='browse'
        )

        # 設定欄位標題和寬度
        self.song_tree.heading('title', text='🎵 歌曲名稱', anchor=tk.W)
        self.song_tree.heading('artist', text='🎤 藝術家', anchor=tk.W)
        self.song_tree.heading('duration', text='⏱ 時長', anchor=tk.E)

        # 設定欄位寬度
        self.song_tree.column('title', width=350, anchor=tk.W)
        self.song_tree.column('artist', width=200, anchor=tk.W)
        self.song_tree.column('duration', width=80, anchor=tk.E)

        self.song_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        song_scroll.config(command=self.song_tree.yview)
        self.song_tree.bind('<Double-1>', self._on_song_double_click)
        self.song_tree.bind('<Button-3>', self._on_song_right_click)

        # 拖放功能綁定
        self._setup_drag_and_drop()

    def _create_sort_controls(self, parent):
        """建立排序控制區

        Args:
            parent: 父框架
        """
        sort_frame = ctk.CTkFrame(parent, fg_color="transparent")
        sort_frame.pack(fill=tk.X, padx=10, pady=(5, 5))

        # 排序標籤
        ctk.CTkLabel(
            sort_frame,
            text="排序：",
            font=("Microsoft JhengHei UI", 10),
            text_color=self.text_secondary
        ).pack(side=tk.LEFT, padx=(0, 5))

        # 排序方式選單
        self.sort_menu = ctk.CTkOptionMenu(
            sort_frame,
            values=["歌曲名稱", "藝術家", "時長"],
            command=self._on_sort_change,
            width=120,
            height=32,
            corner_radius=8,
            font=("Microsoft JhengHei UI", 10)
        )
        self.sort_menu.set(self.sort_by)
        self.sort_menu.pack(side=tk.LEFT)

        # 升序/降序切換按鈕
        self.order_button = ctk.CTkButton(
            sort_frame,
            text="↓ 降序",
            width=80,
            height=32,
            corner_radius=8,
            font=("Microsoft JhengHei UI", 10),
            command=self._toggle_sort_order
        )
        self.order_button.pack(side=tk.LEFT, padx=(5, 0))

    def _on_sort_change(self, sort_by):
        """排序方式改變"""
        self.sort_by = sort_by
        self._sort_songs()

    def _toggle_sort_order(self):
        """切換升序/降序"""
        self.ascending = not self.ascending
        if self.order_button:
            self.order_button.configure(
                text="↑ 升序" if self.ascending else "↓ 降序"
            )
        self._sort_songs()

    def _sort_songs(self):
        """對歌曲列表排序"""
        if not self.current_playlist:
            return

        # 根據選擇的排序方式排序
        if self.sort_by == "歌曲名稱":
            sorted_playlist = sorted(
                self.current_playlist,
                key=lambda x: x.get('title', '').lower(),
                reverse=not self.ascending
            )
        elif self.sort_by == "藝術家":
            sorted_playlist = sorted(
                self.current_playlist,
                key=lambda x: x.get('uploader', '').lower(),
                reverse=not self.ascending
            )
        elif self.sort_by == "時長":
            sorted_playlist = sorted(
                self.current_playlist,
                key=lambda x: x.get('duration', 0),
                reverse=not self.ascending
            )
        else:
            sorted_playlist = self.current_playlist

        # 更新顯示
        self.display_songs(sorted_playlist)

    def _on_song_right_click(self, event):
        """歌曲右鍵選單"""
        # 獲取點擊的歌曲
        item_id = self.song_tree.identify_row(event.y)
        if not item_id:
            return

        # 選中該項目
        self.song_tree.selection_set(item_id)
        item_index = self.song_tree.index(item_id)

        if item_index >= len(self.current_playlist):
            return

        song = self.current_playlist[item_index]

        # 建立右鍵選單
        menu = tk.Menu(self.parent, tearoff=0, bg=self.card_bg, fg=self.text_color)
        menu.add_command(
            label="📁 移動到...",
            command=lambda: self._move_song_dialog(song)
        )
        menu.add_separator()
        menu.add_command(
            label="🗑️ 刪除",
            command=lambda: self._delete_song(song)
        )
        menu.post(event.x_root, event.y_root)

    def _move_song_dialog(self, song):
        """顯示移動歌曲對話框

        Args:
            song (dict): 歌曲資料
        """
        # 獲取所有分類（資料夾）
        categories = self.music_manager.get_all_categories()

        if not categories:
            messagebox.showwarning("警告", "沒有可移動到的資料夾")
            return

        # 建立對話框
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("移動歌曲")
        dialog.geometry("450x400")
        dialog.transient(self.parent)
        dialog.lift()
        dialog.focus_force()

        # 主框架
        main_frame = ctk.CTkFrame(dialog, corner_radius=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        ctk.CTkLabel(
            main_frame,
            text=f"移動歌曲: {song['title'][:40]}",
            font=("Microsoft JhengHei UI", 12, "bold"),
            wraplength=400
        ).pack(pady=(0, 10))

        # 當前資料夾
        current_category = song.get('category', 'Unknown')
        ctk.CTkLabel(
            main_frame,
            text=f"當前資料夾: {current_category}",
            font=("Microsoft JhengHei UI", 10),
            text_color=self.text_secondary
        ).pack(pady=(0, 15))

        # 目標資料夾選擇
        ctk.CTkLabel(
            main_frame,
            text="選擇目標資料夾:",
            font=("Microsoft JhengHei UI", 10)
        ).pack(anchor=tk.W, pady=(0, 5))

        # 列表框框架
        listbox_frame = tk.Frame(main_frame, bg=self.card_bg)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        category_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            bg=self.card_bg,
            fg=self.text_color,
            selectbackground=self.accent_color,
            selectforeground="white",
            font=("Microsoft JhengHei UI", 10),
            borderwidth=0,
            highlightthickness=0
        )
        category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=category_listbox.yview)

        # 填充資料夾列表（排除當前資料夾）
        for category in categories:
            if category != current_category:
                category_listbox.insert(tk.END, category)

        # 按鈕區
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()

        def confirm_move():
            selection = category_listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "請選擇目標資料夾", parent=dialog)
                return

            target_category = category_listbox.get(selection[0])

            # 執行移動
            if self._move_song_to_category(song, target_category):
                messagebox.showinfo(
                    "成功",
                    f"歌曲已移動到 '{target_category}'",
                    parent=dialog
                )
                dialog.destroy()
                # 重新載入音樂庫
                self.reload_library()
            else:
                messagebox.showerror("錯誤", "移動歌曲失敗", parent=dialog)

        ctk.CTkButton(
            button_frame,
            text="確定",
            width=100,
            command=confirm_move
        ).pack(side=tk.LEFT, padx=5)

        ctk.CTkButton(
            button_frame,
            text="取消",
            width=100,
            fg_color="gray40",
            hover_color="gray50",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def _move_song_to_category(self, song, target_category):
        """移動歌曲到指定分類

        Args:
            song (dict): 歌曲資料
            target_category (str): 目標分類名稱

        Returns:
            bool: 是否成功
        """
        try:
            import os
            import shutil

            # 獲取原始音訊檔案路徑
            source_audio_path = song.get('audio_path')
            if not source_audio_path or not os.path.exists(source_audio_path):
                logger.error(f"音訊檔案不存在: {source_audio_path}")
                return False

            # 建立目標路徑
            music_root = self.music_manager.music_root_path
            target_dir = os.path.join(music_root, target_category)
            os.makedirs(target_dir, exist_ok=True)

            # 獲取檔案名稱（不含副檔名）
            audio_filename = os.path.basename(source_audio_path)
            base_name = os.path.splitext(audio_filename)[0]

            # 移動音訊檔案
            target_audio_path = os.path.join(target_dir, audio_filename)
            logger.info(f"移動音訊檔案: {source_audio_path} -> {target_audio_path}")
            shutil.move(source_audio_path, target_audio_path)

            # 移動 JSON 檔案（如果存在）
            source_json_path = os.path.join(
                os.path.dirname(source_audio_path),
                f"{base_name}.json"
            )
            if os.path.exists(source_json_path):
                target_json_path = os.path.join(target_dir, f"{base_name}.json")
                logger.info(f"移動 JSON 檔案: {source_json_path} -> {target_json_path}")
                shutil.move(source_json_path, target_json_path)

            logger.info(f"歌曲移動成功: {song['title']} -> {target_category}")
            return True

        except Exception as e:
            logger.error(f"移動歌曲失敗: {e}", exc_info=True)
            return False

    def _delete_song(self, song):
        """刪除歌曲

        Args:
            song (dict): 歌曲資料
        """
        result = messagebox.askyesno(
            "確認刪除",
            f"確定要刪除歌曲嗎？\n\n{song['title']}\n\n此操作無法復原！"
        )

        if result:
            try:
                import os

                # 刪除音訊檔案
                audio_path = song.get('audio_path')
                if audio_path and os.path.exists(audio_path):
                    logger.info(f"刪除音訊檔案: {audio_path}")
                    os.remove(audio_path)

                    # 刪除對應的 JSON 檔案
                    base_name = os.path.splitext(os.path.basename(audio_path))[0]
                    json_path = os.path.join(os.path.dirname(audio_path), f"{base_name}.json")
                    if os.path.exists(json_path):
                        logger.info(f"刪除 JSON 檔案: {json_path}")
                        os.remove(json_path)

                    messagebox.showinfo("成功", "歌曲已刪除")
                    # 重新載入音樂庫
                    self.reload_library()
                else:
                    messagebox.showerror("錯誤", "找不到音訊檔案")
            except Exception as e:
                logger.error(f"刪除歌曲失敗: {e}", exc_info=True)
                messagebox.showerror("錯誤", f"刪除失敗: {e}")

    def _load_music_library(self):
        """載入音樂庫"""
        result = self.music_manager.scan_music_library()

        if not result['success']:
            logger.error(f"載入音樂庫失敗: {result['message']}")
            return

        # 清空樹狀結構
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)

        # 新增 "所有歌曲" 根節點
        all_songs_node = self.category_tree.insert('', 'end', text='📋 所有歌曲', values=('all',), open=True)

        # 載入分類(資料夾) - 包含空資料夾
        categories = self.music_manager.get_all_categories()
        for category in categories:
            # 新增資料夾節點(即使是空資料夾也顯示)
            folder_node = self.category_tree.insert(
                '', 'end',
                text=f'📁 {category}',
                values=(f'folder:{category}',),
                open=False
            )

            # 載入該資料夾下的歌曲
            songs = self.music_manager.get_songs_by_category(category)
            if songs:
                for song in songs:
                    duration_str = self.music_manager.format_duration(song['duration'])
                    song_text = f'🎵 {song["title"]} ({duration_str})'
                    song_id = song.get('id', '')
                    self.category_tree.insert(
                        folder_node, 'end',
                        text=song_text,
                        values=(f'song:{song_id}',)
                    )
            else:
                # 空資料夾:新增一個提示節點
                self.category_tree.insert(
                    folder_node, 'end',
                    text='   (空資料夾)',
                    values=('empty',),
                    tags=('empty',)
                )

        # 預設選擇所有歌曲
        self.category_tree.selection_set(all_songs_node)
        self._load_all_songs()

    def _load_all_songs(self):
        """載入所有歌曲"""
        songs = self.music_manager.get_all_songs()
        self.display_songs(songs)

    def _get_selected_category_info(self):
        """取得選中的分類資訊

        Returns:
            tuple: (item_id, item_type) 或 (None, None) 如果沒有選擇
        """
        selection = self.category_tree.selection()
        if not selection:
            return None, None

        item_id = selection[0]
        item_values = self.category_tree.item(item_id, 'values')

        if not item_values:
            return None, None

        return item_id, item_values[0]

    def _load_folder_songs_view(self, folder_type):
        """載入資料夾歌曲到視圖

        Args:
            folder_type (str): 資料夾類型字串 (格式: 'folder:category_name')
        """
        category_name = folder_type.replace('folder:', '')
        songs = self.music_manager.get_songs_by_category(category_name)
        self.display_songs(songs)

    def _handle_song_selection(self, song_id, item_id):
        """處理歌曲選擇，更新播放列表

        Args:
            song_id (str): 歌曲 ID
            item_id: TreeView 項目 ID
        """
        song = self.music_manager.get_song_by_id(song_id)
        if not song:
            return

        # 載入所屬資料夾的所有歌曲到播放列表
        parent_id = self.category_tree.parent(item_id)
        if not parent_id:
            return

        parent_values = self.category_tree.item(parent_id, 'values')
        if not parent_values:
            return

        if parent_values[0].startswith('folder:'):
            category_name = parent_values[0].replace('folder:', '')
            self.current_playlist = self.music_manager.get_songs_by_category(category_name)

    def _on_category_select_internal(self, event):
        """分類/資料夾選擇事件(內部處理)"""
        item_id, item_type = self._get_selected_category_info()

        if item_type is None:
            return

        # 根據類型載入對應內容
        if item_type == 'all':
            self._load_all_songs()
        elif item_type.startswith('folder:'):
            self._load_folder_songs_view(item_type)
        elif item_type.startswith('song:'):
            song_id = item_type.replace('song:', '')
            self._handle_song_selection(song_id, item_id)

        # 觸發外部回調
        if self.on_category_select:
            self.on_category_select(item_type)

    def _on_category_double_click_internal(self, event):
        """雙擊事件:展開/收合資料夾 或 觸發歌曲播放"""
        selection = self.category_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        item_values = self.category_tree.item(item_id, 'values')

        if not item_values:
            return

        item_type = item_values[0]

        if item_type.startswith('song:'):
            # 雙擊歌曲,找到索引並觸發回調
            song_id = item_type.replace('song:', '')
            song = self.music_manager.get_song_by_id(song_id)
            if song and self.on_song_double_click:
                # 找到歌曲在當前播放列表中的索引
                index = -1
                for i, s in enumerate(self.current_playlist):
                    if s['id'] == song_id:
                        index = i
                        break
                self.on_song_double_click(song, self.current_playlist, index)

    def _on_category_right_click(self, event):
        """資料夾右鍵選單"""
        # 獲取點擊的項目
        item_id = self.category_tree.identify_row(event.y)
        if not item_id:
            return

        # 選中該項目
        self.category_tree.selection_set(item_id)
        item_values = self.category_tree.item(item_id, 'values')

        if not item_values:
            return

        item_type = item_values[0]

        # 只對資料夾顯示右鍵選單
        if item_type.startswith('folder:'):
            category_name = item_type.replace('folder:', '')

            # 建立右鍵選單
            menu = tk.Menu(self.parent, tearoff=0, bg=self.card_bg, fg=self.text_color)
            menu.add_command(
                label="✏️ 重新命名",
                command=lambda: self._rename_category(category_name)
            )
            menu.add_separator()
            menu.add_command(
                label="🗑️ 刪除",
                command=lambda: self._delete_category(category_name)
            )
            menu.post(event.x_root, event.y_root)

    def _rename_category(self, old_name):
        """重新命名分類

        Args:
            old_name (str): 舊分類名稱
        """
        new_name = simpledialog.askstring(
            "重新命名資料夾",
            "請輸入新名稱:",
            initialvalue=old_name
        )

        if not new_name or new_name.strip() == "" or new_name == old_name:
            return

        new_name = new_name.strip()

        # 執行重命名
        if self.on_category_rename:
            success = self.on_category_rename(old_name, new_name)
            if success:
                messagebox.showinfo("成功", f"資料夾已重新命名為 '{new_name}'")
                self.reload_library()
            else:
                messagebox.showerror("錯誤", "重新命名失敗")

    def _delete_category(self, category_name):
        """刪除分類

        Args:
            category_name (str): 分類名稱
        """
        songs = self.music_manager.get_songs_by_category(category_name)
        song_count = len(songs)

        result = messagebox.askyesno(
            "確認刪除",
            f"確定要刪除資料夾 '{category_name}' 嗎？\n\n"
            f"此資料夾包含 {song_count} 首歌曲。\n\n"
            f"此操作無法復原！"
        )

        if result:
            if self.on_category_delete:
                success = self.on_category_delete(category_name)
                if success:
                    messagebox.showinfo("成功", "資料夾已刪除")
                    self.reload_library()
                else:
                    messagebox.showerror("錯誤", "刪除資料夾失敗")

    def _on_song_double_click(self, event):
        """歌曲雙擊事件"""
        selection = self.song_tree.selection()
        if not selection:
            return

        # 獲取選中的項目索引
        item_id = selection[0]
        item_index = self.song_tree.index(item_id)

        if item_index < len(self.current_playlist):
            song = self.current_playlist[item_index]
            if self.on_song_double_click:
                self.on_song_double_click(song, self.current_playlist, item_index)

    def display_songs(self, songs):
        """顯示歌曲列表

        Args:
            songs (list): 歌曲列表
        """
        self.current_playlist = songs

        # 清空 Treeview
        for item in self.song_tree.get_children():
            self.song_tree.delete(item)

        # 插入歌曲到 Treeview
        for song in songs:
            duration_str = self.music_manager.format_duration(song['duration'])
            artist = song.get('uploader', 'Unknown')
            self.song_tree.insert('', 'end', values=(song['title'], artist, duration_str))

    def reload_library(self):
        """重新載入音樂庫"""
        self._load_music_library()
        logger.info("音樂庫已重新載入")

    def get_selected_category(self):
        """取得選中的分類

        Returns:
            str: 分類類型 ('all', 'folder:name', 'song:id', 或 None)
        """
        selection = self.category_tree.selection()
        if not selection:
            return None

        item_values = self.category_tree.item(selection[0], 'values')
        if not item_values:
            return None

        return item_values[0]

    def get_selected_song_index(self):
        """取得選中的歌曲索引

        Returns:
            int: 歌曲索引,如果沒有選中則回傳 -1
        """
        selection = self.song_tree.selection()
        if not selection:
            return -1

        item_id = selection[0]
        return self.song_tree.index(item_id)

    def get_current_playlist(self):
        """取得當前播放列表

        Returns:
            list: 歌曲列表
        """
        return self.current_playlist

    def clear_song_list(self):
        """清空歌曲列表"""
        for item in self.song_tree.get_children():
            self.song_tree.delete(item)
        self.current_playlist = []

    def _setup_drag_and_drop(self):
        """設定拖放功能"""
        # 歌曲列表綁定拖動事件
        self.song_tree.bind('<ButtonPress-1>', self._on_drag_start)
        self.song_tree.bind('<B1-Motion>', self._on_drag_motion)
        self.song_tree.bind('<ButtonRelease-1>', self._on_drop)

        # 資料夾樹綁定放下區域事件
        self.category_tree.bind('<Motion>', self._on_category_hover)

    def _on_drag_start(self, event):
        """開始拖動歌曲

        Args:
            event: 事件物件
        """
        # 獲取點擊的項目
        item_id = self.song_tree.identify_row(event.y)
        if not item_id:
            self.drag_data = None
            return

        # 獲取歌曲索引
        item_index = self.song_tree.index(item_id)
        if item_index >= len(self.current_playlist):
            self.drag_data = None
            return

        # 儲存拖動資料
        self.drag_start_index = item_index
        self.drag_data = self.current_playlist[item_index]

        # 選中該項目
        self.song_tree.selection_set(item_id)

    def _on_drag_motion(self, event):
        """拖動過程中的處理

        Args:
            event: 事件物件
        """
        if self.drag_data is None:
            return

        # 改變滑鼠游標為拖動樣式
        self.song_tree.config(cursor="hand2")

    def _on_drop(self, event):
        """放下歌曲

        Args:
            event: 事件物件
        """
        # 重置滑鼠游標
        self.song_tree.config(cursor="")

        if self.drag_data is None:
            return

        # 檢查是否放在資料夾樹上
        try:
            # 獲取滑鼠相對於資料夾樹的位置
            x = event.x_root - self.category_tree.winfo_rootx()
            y = event.y_root - self.category_tree.winfo_rooty()

            # 檢查是否在資料夾樹範圍內
            if (0 <= x <= self.category_tree.winfo_width() and
                0 <= y <= self.category_tree.winfo_height()):

                # 獲取放下位置的項目
                item_id = self.category_tree.identify_row(y)
                if item_id:
                    item_values = self.category_tree.item(item_id, 'values')
                    if item_values and item_values[0].startswith('folder:'):
                        # 獲取目標資料夾名稱
                        target_category = item_values[0].replace('folder:', '')
                        current_category = self.drag_data.get('category', '')

                        # 確認是否要移動
                        if target_category != current_category:
                            result = messagebox.askyesno(
                                "確認移動",
                                f"將歌曲 '{self.drag_data['title'][:40]}' 移動到資料夾 '{target_category}' 嗎？",
                                parent=self.parent
                            )

                            if result:
                                # 執行移動
                                if self._move_song_to_category(self.drag_data, target_category):
                                    logger.info(f"拖放移動歌曲成功: {self.drag_data['title']} -> {target_category}")
                                    messagebox.showinfo(
                                        "成功",
                                        f"歌曲已移動到 '{target_category}'",
                                        parent=self.parent
                                    )
                                    # 重新載入音樂庫
                                    self.reload_library()
                                else:
                                    messagebox.showerror("錯誤", "移動歌曲失敗", parent=self.parent)

        except Exception as e:
            logger.error(f"拖放處理失敗: {e}")

        # 清除拖動資料
        self.drag_data = None
        self.drag_start_index = None

    def _on_category_hover(self, event):
        """資料夾樹懸停時的處理

        Args:
            event: 事件物件
        """
        if self.drag_data is None:
            return

        # 獲取懸停位置的項目
        item_id = self.category_tree.identify_row(event.y)
        if item_id:
            item_values = self.category_tree.item(item_id, 'values')
            if item_values and item_values[0].startswith('folder:'):
                # 改變游標樣式表示可以放下
                self.category_tree.config(cursor="hand2")
                return

        # 其他情況恢復正常游標
        self.category_tree.config(cursor="")

    def destroy(self):
        """銷毀視圖"""
        if self.main_frame:
            self.main_frame.destroy()
