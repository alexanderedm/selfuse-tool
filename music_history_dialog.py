"""音樂播放歷史對話框模組"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from logger import logger


class MusicHistoryDialog:
    """音樂播放歷史對話框類別"""

    def __init__(self, parent, play_history_manager, music_manager):
        """初始化對話框

        Args:
            parent: 父視窗
            play_history_manager: 播放歷史管理器實例
            music_manager: 音樂管理器實例
        """
        self.parent = parent
        self.play_history_manager = play_history_manager
        self.music_manager = music_manager

    def show_play_history(self):
        """顯示播放歷史對話框

        Returns:
            Toplevel: 建立的對話框視窗
        """
        # 建立對話框
        history_dialog = tk.Toplevel(self.parent)
        history_dialog.title("📜 播放歷史")
        history_dialog.geometry("700x500")
        history_dialog.configure(bg="#1e1e1e")
        history_dialog.resizable(True, True)
        history_dialog.transient(self.parent)

        main_frame = tk.Frame(history_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題和統計資訊
        header_frame = tk.Frame(main_frame, bg="#1e1e1e")
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header_frame,
            text="📜 最近播放",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(side=tk.LEFT)

        total_plays = self.play_history_manager.get_total_plays()
        tk.Label(
            header_frame,
            text=f"總播放次數: {total_plays}",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#a0a0a0"
        ).pack(side=tk.RIGHT)

        # 建立 Treeview 顯示歷史記錄
        tree_frame = tk.Frame(main_frame, bg="#2d2d2d")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style = ttk.Style()
        style.configure(
            "History.Treeview",
            background="#2d2d2d",
            foreground="#e0e0e0",
            fieldbackground="#2d2d2d",
            borderwidth=0,
            rowheight=25
        )
        style.configure(
            "History.Treeview.Heading",
            background="#0d47a1",
            foreground="white",
            font=("Microsoft JhengHei UI", 10, "bold")
        )
        style.map('History.Treeview', background=[('selected', '#0078d4')])

        history_tree = ttk.Treeview(
            tree_frame,
            columns=('title', 'artist', 'category', 'played_at'),
            show='headings',
            yscrollcommand=scrollbar.set,
            style="History.Treeview",
            selectmode='browse'
        )

        # 設定欄位
        history_tree.heading('title', text='🎵 歌曲名稱', anchor=tk.W)
        history_tree.heading('artist', text='🎤 藝術家', anchor=tk.W)
        history_tree.heading('category', text='📁 分類', anchor=tk.W)
        history_tree.heading('played_at', text='⏰ 播放時間', anchor=tk.W)

        history_tree.column('title', width=250, anchor=tk.W)
        history_tree.column('artist', width=150, anchor=tk.W)
        history_tree.column('category', width=100, anchor=tk.W)
        history_tree.column('played_at', width=150, anchor=tk.W)

        history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=history_tree.yview)

        # 載入歷史記錄
        recent_plays = self.play_history_manager.get_recent_plays(limit=50)
        for record in recent_plays:
            # 格式化播放時間
            time_str = self._format_play_time(record['played_at'])

            history_tree.insert('', 'end', values=(
                record['title'],
                record['artist'],
                record['category'],
                time_str
            ))

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        clear_button = tk.Button(
            button_frame,
            text="🗑️ 清除歷史",
            font=("Microsoft JhengHei UI", 10),
            bg="#d43d00",
            fg="white",
            activebackground="#b03400",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=lambda: self._clear_play_history(history_dialog)
        )
        clear_button.pack(side=tk.LEFT, padx=5)

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
            command=history_dialog.destroy
        )
        close_button.pack(side=tk.LEFT, padx=5)

        logger.info(f"顯示播放歷史,共 {len(recent_plays)} 筆記錄")
        return history_dialog

    def show_most_played(self):
        """顯示最常播放的歌曲對話框

        Returns:
            Toplevel: 建立的對話框視窗
        """
        # 建立對話框
        most_played_dialog = tk.Toplevel(self.parent)
        most_played_dialog.title("🏆 最常播放")
        most_played_dialog.geometry("700x500")
        most_played_dialog.configure(bg="#1e1e1e")
        most_played_dialog.resizable(True, True)
        most_played_dialog.transient(self.parent)

        main_frame = tk.Frame(most_played_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        tk.Label(
            main_frame,
            text="🏆 最常播放排行榜",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(pady=(0, 15))

        # 建立 Treeview 顯示排行榜
        tree_frame = tk.Frame(main_frame, bg="#2d2d2d")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 設定 Treeview 樣式
        style = ttk.Style()
        style.configure(
            "MostPlayed.Treeview",
            background="#2d2d2d",
            foreground="#e0e0e0",
            fieldbackground="#2d2d2d",
            borderwidth=0,
            rowheight=25
        )
        style.configure(
            "MostPlayed.Treeview.Heading",
            background="#0d47a1",
            foreground="white",
            font=("Microsoft JhengHei UI", 10, "bold")
        )
        style.map('MostPlayed.Treeview', background=[('selected', '#0078d4')])

        most_played_tree = ttk.Treeview(
            tree_frame,
            columns=('rank', 'title', 'artist', 'category', 'play_count'),
            show='headings',
            yscrollcommand=scrollbar.set,
            style="MostPlayed.Treeview",
            selectmode='browse'
        )

        # 設定欄位
        most_played_tree.heading('rank', text='🥇 排名', anchor=tk.CENTER)
        most_played_tree.heading('title', text='🎵 歌曲名稱', anchor=tk.W)
        most_played_tree.heading('artist', text='🎤 藝術家', anchor=tk.W)
        most_played_tree.heading('category', text='📁 分類', anchor=tk.W)
        most_played_tree.heading('play_count', text='🔢 播放次數', anchor=tk.CENTER)

        most_played_tree.column('rank', width=60, anchor=tk.CENTER)
        most_played_tree.column('title', width=230, anchor=tk.W)
        most_played_tree.column('artist', width=130, anchor=tk.W)
        most_played_tree.column('category', width=100, anchor=tk.W)
        most_played_tree.column('play_count', width=90, anchor=tk.CENTER)

        most_played_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=most_played_tree.yview)

        # 載入最常播放的歌曲
        most_played = self.play_history_manager.get_most_played(limit=50)

        for rank, record in enumerate(most_played, start=1):
            song_id = record['song_id']
            play_count = record['play_count']

            # 從音樂管理器獲取歌曲詳細資訊
            song = self.music_manager.get_song_by_id(song_id)

            if song:
                # 排名表情符號
                rank_emoji = self._get_rank_emoji(rank)

                most_played_tree.insert('', 'end', values=(
                    rank_emoji,
                    song.get('title', 'Unknown'),
                    song.get('uploader', 'Unknown'),
                    song.get('category', 'Unknown'),
                    play_count
                ))

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
            command=most_played_dialog.destroy
        )
        close_button.pack()

        logger.info(f"顯示最常播放排行榜,共 {len(most_played)} 首歌曲")
        return most_played_dialog

    def _clear_play_history(self, dialog):
        """清除播放歷史

        Args:
            dialog: 對話框視窗
        """
        result = messagebox.askyesno(
            "確認清除",
            "確定要清除所有播放歷史記錄嗎?\n\n此操作無法復原!",
            parent=dialog
        )

        if result:
            self.play_history_manager.clear_history()
            messagebox.showinfo("成功", "播放歷史已清除", parent=dialog)
            dialog.destroy()
            logger.info("播放歷史已清除")

    def _format_play_time(self, played_at):
        """格式化播放時間

        Args:
            played_at: ISO 格式的時間字串

        Returns:
            str: 格式化後的時間字串
        """
        try:
            played_time = datetime.fromisoformat(played_at)
            return played_time.strftime('%Y-%m-%d %H:%M')
        except Exception:
            # 如果解析失敗,截取前 16 個字符
            return played_at[:16] if len(played_at) >= 16 else played_at

    def _get_rank_emoji(self, rank):
        """取得排名表情符號

        Args:
            rank: 排名數字

        Returns:
            str: 排名表情符號或數字
        """
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        else:
            return str(rank)
