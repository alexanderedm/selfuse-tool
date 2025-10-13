"""音樂下載對話框模組"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import re
import os
from logger import logger


class MusicDownloadDialog:
    """管理音樂下載相關的 UI 和邏輯"""

    def __init__(self, parent, music_manager, youtube_downloader, on_download_complete=None):
        """初始化下載對話框

        Args:
            parent: 父視窗
            music_manager: 音樂管理器實例
            youtube_downloader: YouTube 下載器實例
            on_download_complete: 下載完成後的回調函數
        """
        self.parent = parent
        self.music_manager = music_manager
        self.youtube_downloader = youtube_downloader
        self.on_download_complete = on_download_complete

        # 對話框實例
        self.dialog = None
        self.progress_dialog = None

    def show_download_dialog(self):
        """顯示下載對話框"""
        # 檢查 yt-dlp 是否安裝
        if not self.youtube_downloader.check_ytdlp_installed():
            messagebox.showerror(
                "錯誤",
                "未安裝 yt-dlp!\n\n請在命令提示字元執行:\npip install yt-dlp"
            )
            return

        # 建立下載對話框
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("📥 下載 YouTube 音樂")
        self.dialog.geometry("600x400")
        self.dialog.configure(bg="#1e1e1e")
        self.dialog.resizable(False, False)

        # 置中顯示
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        main_frame = tk.Frame(self.dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        tk.Label(
            main_frame,
            text="下載 YouTube 音樂",
            font=("Microsoft JhengHei UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(pady=(0, 15))

        # 搜尋/URL 輸入框架
        input_frame = tk.Frame(main_frame, bg="#1e1e1e")
        input_frame.pack(fill=tk.X, pady=(0, 15))

        # URL 輸入
        tk.Label(
            input_frame,
            text="YouTube 連結或搜尋關鍵字:",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(anchor=tk.W)

        url_entry = tk.Entry(
            input_frame,
            font=("Microsoft JhengHei UI", 10),
            bg="#2d2d2d",
            fg="#e0e0e0",
            insertbackground="#e0e0e0",
            relief=tk.FLAT,
            borderwidth=0
        )
        url_entry.pack(fill=tk.X, ipady=8, pady=(5, 0))

        # 分類選擇
        tk.Label(
            main_frame,
            text="下載到分類:",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(anchor=tk.W)

        category_frame = tk.Frame(main_frame, bg="#1e1e1e")
        category_frame.pack(fill=tk.X, pady=(5, 15))

        categories = self.music_manager.get_all_categories()
        if not categories:
            categories = ["下載"]

        category_var = tk.StringVar(value=categories[0] if categories else "下載")

        category_combo = ttk.Combobox(
            category_frame,
            textvariable=category_var,
            values=categories,
            font=("Microsoft JhengHei UI", 10),
            state="readonly"
        )
        category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 或新增分類
        new_category_button = tk.Button(
            category_frame,
            text="+ 新增分類",
            font=("Microsoft JhengHei UI", 9),
            bg="#353535",
            fg="#e0e0e0",
            activebackground="#505050",
            activeforeground="white",
            borderwidth=0,
            padx=10,
            pady=5,
            command=lambda: self._add_new_category(category_combo, category_var)
        )
        new_category_button.pack(side=tk.LEFT, padx=(10, 0))

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack(pady=(10, 0))

        download_btn = tk.Button(
            button_frame,
            text="🎵 開始",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=30,
            pady=8,
            command=lambda: self._smart_download_or_search(
                url_entry.get(),
                category_var.get()
            )
        )
        download_btn.pack(side=tk.LEFT, padx=5)

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
            command=self.dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _is_youtube_url(self, text):
        """檢測是否為 YouTube URL

        Args:
            text (str): 待檢測的文字

        Returns:
            bool: 是否為 YouTube URL
        """
        if not text or not text.strip():
            return False

        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com',
            r'(?:https?://)?(?:www\.)?youtu\.be',
            r'(?:https?://)?music\.youtube\.com'
        ]

        return any(re.search(pattern, text, re.IGNORECASE) for pattern in youtube_patterns)

    def _smart_download_or_search(self, input_text, category):
        """智能判斷輸入是 URL 還是搜尋關鍵字

        Args:
            input_text (str): 輸入文字
            category (str): 目標分類
        """
        if not input_text or not input_text.strip():
            messagebox.showwarning("警告", "請輸入 YouTube 連結或搜尋關鍵字", parent=self.dialog)
            return

        input_text = input_text.strip()

        if self._is_youtube_url(input_text):
            # 是 URL,直接下載
            logger.info(f"偵測到 YouTube 連結,直接下載: {input_text}")
            self._start_direct_download(input_text, category)
        else:
            # 不是 URL,進行搜尋
            logger.info(f"偵測到搜尋關鍵字,開始搜尋: {input_text}")
            self._start_search_download(input_text, category)

    def _start_direct_download(self, url, category):
        """直接下載 YouTube URL

        Args:
            url (str): YouTube URL
            category (str): 目標分類
        """
        self.start_download(url, category)

    def _start_search_download(self, query, category):
        """搜尋並下載

        Args:
            query (str): 搜尋關鍵字
            category (str): 目標分類
        """
        # 顯示搜尋中訊息
        search_msg = messagebox.showinfo(
            "搜尋中",
            "正在搜尋 YouTube 影片,請稍候...",
            parent=self.dialog
        )

        # 在背景執行緒中搜尋
        def search_thread():
            results = self.youtube_downloader.search_youtube(query, max_results=5)

            if not results:
                self.parent.after(0, lambda: messagebox.showerror(
                    "搜尋失敗",
                    "沒有找到相關影片,請嘗試其他關鍵字。",
                    parent=self.dialog
                ))
                return

            # 顯示搜尋結果選擇對話框
            self.parent.after(0, lambda: self.show_search_results(results, category))

        threading.Thread(target=search_thread, daemon=True).start()

    def show_search_results(self, results, category):
        """顯示搜尋結果對話框

        Args:
            results (list): 搜尋結果列表
            category (str): 目標分類
        """
        # 建立結果對話框
        result_dialog = tk.Toplevel(self.dialog)
        result_dialog.title("🔍 搜尋結果")
        result_dialog.geometry("700x500")
        result_dialog.configure(bg="#1e1e1e")
        result_dialog.resizable(False, False)

        # 置中顯示
        result_dialog.transient(self.dialog)
        result_dialog.grab_set()

        main_frame = tk.Frame(result_dialog, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        tk.Label(
            main_frame,
            text=f"找到 {len(results)} 個結果,請選擇要下載的影片:",
            font=("Microsoft JhengHei UI", 12, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(pady=(0, 10))

        # 顯示將下載到的分類
        tk.Label(
            main_frame,
            text=f"下載分類: {category}",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#a0a0a0"
        ).pack(pady=(0, 15))

        # 結果列表框架
        list_frame = tk.Frame(main_frame, bg="#2d2d2d")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 滾動條
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 結果列表
        result_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg="#2d2d2d",
            fg="#e0e0e0",
            selectbackground="#0078d4",
            selectforeground="white",
            font=("Microsoft JhengHei UI", 10),
            borderwidth=0,
            highlightthickness=0,
            height=15
        )
        result_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=result_listbox.yview)

        # 填充搜尋結果
        for i, video in enumerate(results):
            duration_str = self.music_manager.format_duration(video['duration'])
            display_text = f"{i+1}. {video['title']}\n   👤 {video['uploader']} | ⏱ {duration_str}"
            result_listbox.insert(tk.END, display_text)
            # 添加空行分隔
            if i < len(results) - 1:
                result_listbox.insert(tk.END, "")

        # 按鈕區
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack()

        def on_select():
            selection = result_listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "請選擇一個影片", parent=result_dialog)
                return

            # 因為有空行,需要計算實際的影片索引
            selected_index = selection[0]
            video_index = selected_index // 2  # 每個影片佔2行(內容+空行)

            if video_index < len(results):
                selected_video = results[video_index]

                # 關閉對話框
                result_dialog.destroy()
                self.dialog.destroy()

                # 開始下載
                self.start_download(selected_video.get('webpage_url', ''), category)

        select_btn = tk.Button(
            button_frame,
            text="選擇並下載",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            borderwidth=0,
            padx=20,
            pady=8,
            command=on_select
        )
        select_btn.pack(side=tk.LEFT, padx=5)

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
            command=result_dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def start_download(self, url, category):
        """開始下載流程

        Args:
            url (str): YouTube URL
            category (str): 目標分類
        """
        if not url or not url.strip():
            messagebox.showwarning("警告", "請輸入 YouTube 連結")
            return

        # 關閉主對話框(如果存在)
        if self.dialog:
            self.dialog.destroy()

        # 顯示進度對話框
        self.show_progress()

        # 在背景執行緒中下載
        def download_thread():
            # 更新狀態
            self.parent.after(0, lambda: self._update_progress_status("正在獲取影片資訊..."))

            result = self.youtube_downloader.download_audio(url, category)

            # 停止進度條
            self.parent.after(0, self._stop_progress)

            # 關閉進度對話框
            self.parent.after(0, lambda: self.progress_dialog.destroy() if self.progress_dialog else None)

            # 調用完成回調
            if result['success']:
                self.parent.after(0, lambda: self.on_download_complete(True, result['message'], category))
            else:
                self.parent.after(0, lambda: self.on_download_complete(False, result['message'], None))

        threading.Thread(target=download_thread, daemon=True).start()

    def show_progress(self):
        """顯示下載進度對話框"""
        self.progress_dialog = tk.Toplevel(self.parent)
        self.progress_dialog.title("📥 下載中")
        self.progress_dialog.geometry("450x200")
        self.progress_dialog.configure(bg="#1e1e1e")
        self.progress_dialog.resizable(False, False)
        self.progress_dialog.transient(self.parent)
        self.progress_dialog.grab_set()

        # 進度框架
        progress_frame = tk.Frame(self.progress_dialog, bg="#1e1e1e")
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        tk.Label(
            progress_frame,
            text="正在下載音樂...",
            font=("Microsoft JhengHei UI", 12, "bold"),
            bg="#1e1e1e",
            fg="#e0e0e0"
        ).pack(pady=(0, 15))

        # 狀態標籤
        self.status_label = tk.Label(
            progress_frame,
            text="準備下載...",
            font=("Microsoft JhengHei UI", 10),
            bg="#1e1e1e",
            fg="#a0a0a0",
            wraplength=400,
            justify=tk.CENTER
        )
        self.status_label.pack(pady=(0, 15))

        # 不確定模式的進度條
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.pack(pady=(0, 15))
        self.progress_bar.start(10)  # 開始動畫

        # 小提示
        tk.Label(
            progress_frame,
            text="這可能需要幾分鐘時間,請耐心等候...",
            font=("Microsoft JhengHei UI", 8),
            bg="#1e1e1e",
            fg="#606060"
        ).pack()

    def _update_progress_status(self, status):
        """更新進度狀態文字

        Args:
            status (str): 狀態文字
        """
        if self.status_label:
            self.status_label.config(text=status)

    def _stop_progress(self):
        """停止進度條動畫"""
        if self.progress_bar:
            self.progress_bar.stop()

    def _add_new_category(self, combo, var):
        """新增分類

        Args:
            combo: Combobox 元件
            var: StringVar 變數
        """
        new_category = simpledialog.askstring("新增分類", "請輸入新分類名稱:")
        if new_category and new_category.strip():
            new_category = new_category.strip()
            # 建立分類資料夾
            category_path = os.path.join(self.music_manager.music_root_path, new_category)
            os.makedirs(category_path, exist_ok=True)

            # 更新下拉選單
            categories = self.music_manager.get_all_categories()
            categories.append(new_category)
            combo['values'] = categories
            var.set(new_category)

            logger.info(f"新增分類: {new_category}")
