"""播放列表對話框模組"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from logger import logger


class MusicPlaylistDialog:
    """播放列表對話框類別

    負責管理播放列表的所有 UI 操作:
    - 顯示播放列表列表
    - 建立/刪除/重新命名播放列表
    - 編輯播放列表描述
    - 加入歌曲到播放列表
    - 顯示播放列表詳情
    """

    def __init__(self, parent_window, playlist_manager, music_manager,
                 on_play_playlist=None, on_play_song=None):
        """初始化播放列表對話框

        Args:
            parent_window: 父視窗
            playlist_manager: 播放列表管理器
            music_manager: 音樂管理器
            on_play_playlist: 播放播放列表的回調函數 (可選)
            on_play_song: 播放歌曲的回調函數 (可選)
        """
        self.parent_window = parent_window
        self.playlist_manager = playlist_manager
        self.music_manager = music_manager
        self.on_play_playlist = on_play_playlist
        self.on_play_song = on_play_song

    def show_playlists(self):
        """顯示播放列表管理對話框"""
        # 建立對話框
        playlist_dialog = tk.Toplevel(self.parent_window)
        playlist_dialog.title("📋 播放列表管理")
        playlist_dialog.geometry("700x500")
        playlist_dialog.configure(bg="#1e1e1e")
        playlist_dialog.resizable(True, True)
        playlist_dialog.transient(self.parent_window)
        playlist_dialog.lift()
        playlist_dialog.focus_force()

        main_frame = tk.Frame(playlist_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題和操作按鈕區
        header_frame = tk.Frame(main_frame, bg="#1e1e1e")
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header_frame,
            text="📋 我的播放列表",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(side=tk.LEFT)

        # 新增播放列表按鈕
        new_playlist_button = tk.Button(
            header_frame,
            text="➕ 新增播放列表",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=15,
            pady=5,
            command=lambda: self.create_playlist(playlist_dialog)
        )
        new_playlist_button.pack(side=tk.RIGHT)

        # 建立 Treeview 顯示播放列表
        tree_frame = tk.Frame(main_frame, bg="#2d2d2d")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style = ttk.Style()
        style.configure(
            "Playlist.Treeview",
            background="#2d2d2d",
            foreground="#e0e0e0",
            fieldbackground="#2d2d2d",
            borderwidth=0,
            rowheight=30
        )
        style.configure(
            "Playlist.Treeview.Heading",
            background="#0d47a1",
            foreground="white",
            font=("Microsoft JhengHei UI", 10, "bold")
        )
        style.map('Playlist.Treeview', background=[('selected', '#0078d4')])

        playlist_tree = ttk.Treeview(
            tree_frame,
            columns=('name', 'song_count', 'description'),
            show='headings',
            yscrollcommand=scrollbar.set,
            style="Playlist.Treeview",
            selectmode='browse'
        )

        # 設定欄位
        playlist_tree.heading('name', text='📋 播放列表名稱', anchor=tk.W)
        playlist_tree.heading('song_count', text='🎵 歌曲數', anchor=tk.CENTER)
        playlist_tree.heading('description', text='📝 描述', anchor=tk.W)

        playlist_tree.column('name', width=200, anchor=tk.W)
        playlist_tree.column('song_count', width=80, anchor=tk.CENTER)
        playlist_tree.column('description', width=350, anchor=tk.W)

        playlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=playlist_tree.yview)

        # 載入播放列表
        playlists = self.playlist_manager.get_all_playlists()
        for playlist in playlists:
            playlist_tree.insert('', 'end', values=(
                playlist['name'],
                playlist['song_count'],
                playlist['description']
            ))

        # 雙擊事件:查看播放列表詳情
        def on_playlist_double_click(event):
            selection = playlist_tree.selection()
            if not selection:
                return
            item_values = playlist_tree.item(selection[0], 'values')
            playlist_name = item_values[0]
            self.show_playlist_detail(playlist_name)

        playlist_tree.bind('<Double-1>', on_playlist_double_click)

        # 右鍵選單
        def on_playlist_right_click(event):
            item_id = playlist_tree.identify_row(event.y)
            if not item_id:
                return

            playlist_tree.selection_set(item_id)
            item_values = playlist_tree.item(item_id, 'values')
            playlist_name = item_values[0]

            menu = tk.Menu(playlist_dialog, tearoff=0, bg="#2d2d2d", fg="#e0e0e0")
            menu.add_command(
                label="👁️ 查看",
                command=lambda: self.show_playlist_detail(playlist_name)
            )
            menu.add_command(
                label="✏️ 重新命名",
                command=lambda: self.rename_playlist(playlist_name, playlist_dialog)
            )
            menu.add_command(
                label="📝 編輯描述",
                command=lambda: self.edit_description(playlist_name, playlist_dialog)
            )
            menu.add_separator()
            menu.add_command(
                label="🗑️ 刪除",
                command=lambda: self.delete_playlist(playlist_name, playlist_dialog)
            )
            menu.post(event.x_root, event.y_root)

        playlist_tree.bind('<Button-3>', on_playlist_right_click)

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        close_button = tk.Button(
            button_frame,
            text="關閉",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=playlist_dialog.destroy
        )
        close_button.pack()

        logger.info(f"顯示播放列表管理,共 {len(playlists)} 個列表")
        return playlist_dialog

    def create_playlist(self, parent_dialog):
        """建立新播放列表

        Args:
            parent_dialog: 父對話框
        """
        name = simpledialog.askstring(
            "新增播放列表",
            "請輸入播放列表名稱:",
            parent=parent_dialog
        )
        if not name or not name.strip():
            return

        name = name.strip()

        # 詢問描述(可選)
        description = simpledialog.askstring(
            "播放列表描述",
            "請輸入描述 (可留空):",
            parent=parent_dialog
        )
        if description is None:
            description = ""

        if self.playlist_manager.create_playlist(name, description):
            messagebox.showinfo("成功", f"播放列表 '{name}' 已建立", parent=parent_dialog)
            # 關閉並重新開啟對話框以刷新列表
            parent_dialog.destroy()
            self.show_playlists()
        else:
            messagebox.showerror(
                "錯誤",
                "建立播放列表失敗,名稱可能已存在",
                parent=parent_dialog
            )

    def delete_playlist(self, playlist_name, parent_dialog):
        """刪除播放列表

        Args:
            playlist_name: 播放列表名稱
            parent_dialog: 父對話框
        """
        result = messagebox.askyesno(
            "確認刪除",
            f"確定要刪除播放列表 '{playlist_name}' 嗎?\n\n此操作無法復原!",
            parent=parent_dialog
        )

        if result:
            if self.playlist_manager.delete_playlist(playlist_name):
                messagebox.showinfo(
                    "成功",
                    f"播放列表 '{playlist_name}' 已刪除",
                    parent=parent_dialog
                )
                # 關閉並重新開啟對話框以刷新列表
                parent_dialog.destroy()
                self.show_playlists()
            else:
                messagebox.showerror("錯誤", "刪除播放列表失敗", parent=parent_dialog)

    def rename_playlist(self, old_name, parent_dialog):
        """重新命名播放列表

        Args:
            old_name: 舊名稱
            parent_dialog: 父對話框
        """
        new_name = simpledialog.askstring(
            "重新命名播放列表",
            "請輸入新名稱:",
            initialvalue=old_name,
            parent=parent_dialog
        )
        if not new_name or not new_name.strip() or new_name == old_name:
            return

        new_name = new_name.strip()

        if self.playlist_manager.rename_playlist(old_name, new_name):
            messagebox.showinfo(
                "成功",
                f"播放列表已重新命名為 '{new_name}'",
                parent=parent_dialog
            )
            # 關閉並重新開啟對話框以刷新列表
            parent_dialog.destroy()
            self.show_playlists()
        else:
            messagebox.showerror(
                "錯誤",
                "重新命名失敗,名稱可能已存在",
                parent=parent_dialog
            )

    def edit_description(self, playlist_name, parent_dialog):
        """編輯播放列表描述

        Args:
            playlist_name: 播放列表名稱
            parent_dialog: 父對話框
        """
        playlist = self.playlist_manager.get_playlist(playlist_name)
        if not playlist:
            return

        current_desc = playlist['description']
        new_desc = simpledialog.askstring(
            "編輯描述",
            f"播放列表: {playlist_name}\n\n請輸入新的描述:",
            initialvalue=current_desc,
            parent=parent_dialog
        )

        if new_desc is None:  # 使用者取消
            return

        if self.playlist_manager.update_description(playlist_name, new_desc):
            messagebox.showinfo("成功", "描述已更新", parent=parent_dialog)
            # 關閉並重新開啟對話框以刷新列表
            parent_dialog.destroy()
            self.show_playlists()
        else:
            messagebox.showerror("錯誤", "更新描述失敗", parent=parent_dialog)

    def add_song_to_playlist(self, song):
        """加入歌曲到播放列表

        Args:
            song: 歌曲資料 (dict)
        """
        playlists = self.playlist_manager.get_all_playlists()

        if not playlists:
            result = messagebox.askyesno(
                "沒有播放列表",
                "目前沒有任何播放列表。\n\n是否要建立新的播放列表?"
            )
            if result:
                self.show_playlists()
            return

        # 建立選擇對話框
        select_dialog = tk.Toplevel(self.parent_window)
        select_dialog.title("加入到播放列表")
        select_dialog.geometry("450x350")
        select_dialog.configure(bg="#1e1e1e")
        select_dialog.resizable(False, False)
        select_dialog.transient(self.parent_window)
        select_dialog.lift()
        select_dialog.focus_force()
        select_dialog.grab_set()

        main_frame = tk.Frame(select_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 歌曲資訊
        song_title = song['title'][:40] + ('...' if len(song['title']) > 40 else '')
        tk.Label(
            main_frame,
            text=f"歌曲: {song_title}",
            font=("Microsoft JhengHei UI", 10, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0",
            wraplength=400,
            justify=tk.LEFT
        ).pack(pady=(0, 20))

        # 播放列表選擇
        tk.Label(
            main_frame,
            text="選擇播放列表:",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(anchor=tk.W, pady=(0, 5))

        # 列表框
        listbox_frame = tk.Frame(main_frame, bg="#2d2d2d")
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        playlist_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            bg="#2d2d2d",
            fg="#e0e0e0",
            selectbackground="#0078d4",
            selectforeground="white",
            font=("Microsoft JhengHei UI", 10),
            borderwidth=0,
            highlightthickness=0
        )
        playlist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=playlist_listbox.yview)

        # 填充播放列表
        for playlist in playlists:
            display_text = f"{playlist['name']} ({playlist['song_count']} 首歌)"
            playlist_listbox.insert(tk.END, display_text)

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        def confirm_add():
            selection = playlist_listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "請選擇一個播放列表", parent=select_dialog)
                return

            selected_index = selection[0]
            selected_playlist = playlists[selected_index]
            playlist_name = selected_playlist['name']

            if self.playlist_manager.add_song(playlist_name, song['id']):
                messagebox.showinfo(
                    "成功",
                    f"已加入到播放列表 '{playlist_name}'",
                    parent=select_dialog
                )
                select_dialog.destroy()
            else:
                messagebox.showwarning(
                    "提示",
                    "歌曲已在播放列表中",
                    parent=select_dialog
                )

        add_button = tk.Button(
            button_frame,
            text="加入",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=30,
            pady=8,
            command=confirm_add
        )
        add_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(
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
            command=select_dialog.destroy
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

        return select_dialog

    def show_playlist_detail(self, playlist_name):
        """顯示播放列表詳情

        Args:
            playlist_name: 播放列表名稱
        """
        playlist = self.playlist_manager.get_playlist(playlist_name)
        if not playlist:
            messagebox.showerror("錯誤", "播放列表不存在")
            return None

        # 建立對話框
        detail_dialog = tk.Toplevel(self.parent_window)
        detail_dialog.title(f"📋 {playlist_name}")
        detail_dialog.geometry("700x500")
        detail_dialog.configure(bg="#1e1e1e")
        detail_dialog.resizable(True, True)
        detail_dialog.transient(self.parent_window)
        detail_dialog.lift()
        detail_dialog.focus_force()

        main_frame = tk.Frame(detail_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題和資訊
        header_frame = tk.Frame(main_frame, bg="#1e1e1e")
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header_frame,
            text=f"📋 {playlist_name}",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(side=tk.LEFT)

        tk.Label(
            header_frame,
            text=f"{playlist['song_count']} 首歌",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#a0a0a0"
        ).pack(side=tk.RIGHT)

        # 描述
        if playlist['description']:
            tk.Label(
                main_frame,
                text=playlist['description'],
                font=("Microsoft JhengHei UI", 9),
                bg="#1e1e1e",
                fg="#a0a0a0",
                wraplength=650,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=(0, 15))

        # 建立 Treeview 顯示歌曲列表
        tree_frame = tk.Frame(main_frame, bg="#2d2d2d")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        style = ttk.Style()
        style.configure(
            "PlaylistDetail.Treeview",
            background="#2d2d2d",
            foreground="#e0e0e0",
            fieldbackground="#2d2d2d",
            borderwidth=0,
            rowheight=25
        )
        style.configure(
            "PlaylistDetail.Treeview.Heading",
            background="#0d47a1",
            foreground="white",
            font=("Microsoft JhengHei UI", 10, "bold")
        )
        style.map('PlaylistDetail.Treeview', background=[('selected', '#0078d4')])

        song_tree = ttk.Treeview(
            tree_frame,
            columns=('title', 'artist', 'duration'),
            show='headings',
            yscrollcommand=scrollbar.set,
            style="PlaylistDetail.Treeview",
            selectmode='browse'
        )

        song_tree.heading('title', text='🎵 歌曲名稱', anchor=tk.W)
        song_tree.heading('artist', text='🎤 藝術家', anchor=tk.W)
        song_tree.heading('duration', text='⏱ 時長', anchor=tk.E)

        song_tree.column('title', width=300, anchor=tk.W)
        song_tree.column('artist', width=200, anchor=tk.W)
        song_tree.column('duration', width=80, anchor=tk.E)

        song_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=song_tree.yview)

        # 載入歌曲
        for song_id in playlist['songs']:
            song = self.music_manager.get_song_by_id(song_id)
            if song:
                duration_str = self.music_manager.format_duration(song['duration'])
                song_tree.insert('', 'end', values=(
                    song['title'],
                    song.get('uploader', 'Unknown'),
                    duration_str
                ))

        # 雙擊播放
        def on_song_double_click(event):
            selection = song_tree.selection()
            if not selection:
                return
            item_index = song_tree.index(selection[0])
            if item_index < len(playlist['songs']):
                song_id = playlist['songs'][item_index]
                song = self.music_manager.get_song_by_id(song_id)
                if song:
                    # 設定播放列表為該播放列表的所有歌曲
                    playlist_songs = [
                        self.music_manager.get_song_by_id(sid)
                        for sid in playlist['songs']
                        if self.music_manager.get_song_by_id(sid)
                    ]
                    if self.on_play_song:
                        self.on_play_song(song, playlist_songs, item_index)

        song_tree.bind('<Double-1>', on_song_double_click)

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        play_all_button = tk.Button(
            button_frame,
            text="▶️ 播放全部",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=lambda: self.play_playlist(playlist_name)
        )
        play_all_button.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(
            button_frame,
            text="關閉",
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=detail_dialog.destroy
        )
        close_button.pack(side=tk.LEFT, padx=5)

        logger.info(f"顯示播放列表詳情: {playlist_name}, {playlist['song_count']} 首歌")
        return detail_dialog

    def play_playlist(self, playlist_name):
        """播放整個播放列表

        Args:
            playlist_name: 播放列表名稱
        """
        if self.on_play_playlist:
            self.on_play_playlist(playlist_name)
        else:
            logger.warning("未設定 on_play_playlist 回調函數")

    def play_song(self, song, playlist_songs, index):
        """播放歌曲

        Args:
            song: 歌曲資料
            playlist_songs: 播放列表中的所有歌曲
            index: 當前歌曲在播放列表中的索引
        """
        if self.on_play_song:
            self.on_play_song(song, playlist_songs, index)
        else:
            logger.warning("未設定 on_play_song 回調函數")
