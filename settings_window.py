"""設定視窗模組"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class SettingsWindow:
    """設定視窗類別"""

    def __init__(self, audio_manager, config_manager, tk_root=None, on_save_callback=None):
        self.audio_manager = audio_manager
        self.config_manager = config_manager
        self.on_save_callback = on_save_callback
        self.window = None
        self.tk_root = tk_root  # 使用共用的根視窗

    def show(self):
        """顯示設定視窗"""
        if self.window is not None:
            self.window.lift()
            self.window.focus_force()
            return

        # 使用共用的根視窗建立 Toplevel 視窗
        if self.tk_root:
            self.window = tk.Toplevel(self.tk_root)
        else:
            # 如果沒有提供根視窗,建立獨立的視窗
            self.window = tk.Tk()
        self.window.title("⚙ 音訊切換工具 - 設定")
        self.window.geometry("600x600")
        self.window.resizable(False, False)

        # 設定深色主題顏色
        bg_color = "#1e1e1e"
        card_bg = "#2d2d2d"
        text_color = "#e0e0e0"
        text_secondary = "#a0a0a0"
        accent_bg = "#1a3a52"
        self.window.configure(bg=bg_color)

        # 建立主框架
        main_frame = tk.Frame(self.window, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # === 標題 ===
        title_label = tk.Label(
            main_frame,
            text="⚙ 音訊裝置設定",
            font=("Microsoft JhengHei UI", 16, "bold"),
            bg=bg_color,
            fg=text_color
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = tk.Label(
            main_frame,
            text="選擇兩個要快速切換的音訊輸出裝置",
            font=("Microsoft JhengHei UI", 10),
            bg=bg_color,
            fg=text_secondary
        )
        subtitle_label.pack(pady=(0, 25))

        # === 裝置選擇區 ===
        devices_frame = tk.Frame(main_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        devices_frame.pack(fill=tk.X, pady=(0, 20))

        inner_frame = tk.Frame(devices_frame, bg=card_bg)
        inner_frame.pack(padx=20, pady=20)

        # 取得所有裝置
        devices = self.audio_manager.get_all_output_devices()
        device_names = [f"{d['name']}" for d in devices]

        # 設定深色主題樣式
        style = ttk.Style()
        style.theme_use('clam')

        # Combobox 深色樣式
        style.configure("Settings.TCombobox",
                       font=("Microsoft JhengHei UI", 10),
                       fieldbackground=card_bg,
                       background=card_bg,
                       foreground=text_color,
                       arrowcolor=text_color,
                       bordercolor=text_secondary,
                       lightcolor=card_bg,
                       darkcolor=card_bg)
        style.map('Settings.TCombobox',
                 fieldbackground=[('readonly', card_bg)],
                 selectbackground=[('readonly', card_bg)],
                 selectforeground=[('readonly', text_color)])

        # 裝置 A 選擇
        device_a_frame = tk.Frame(inner_frame, bg=card_bg)
        device_a_frame.pack(fill=tk.X, pady=10)

        device_a_icon = tk.Label(
            device_a_frame,
            text="🎧",
            font=("Segoe UI Emoji", 16),
            bg=card_bg
        )
        device_a_icon.pack(side=tk.LEFT, padx=(0, 10))

        device_a_label_frame = tk.Frame(device_a_frame, bg=card_bg)
        device_a_label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        device_a_label = tk.Label(
            device_a_label_frame,
            text="裝置 A",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=card_bg,
            fg=text_color,
            anchor=tk.W
        )
        device_a_label.pack(anchor=tk.W)

        self.device_a_var = tk.StringVar()
        device_a_combo = ttk.Combobox(
            device_a_label_frame,
            textvariable=self.device_a_var,
            values=device_names,
            state="readonly",
            width=50,
            font=("Microsoft JhengHei UI", 10)
        )
        device_a_combo.pack(fill=tk.X, pady=(5, 0))

        # 設定目前的裝置 A
        current_device_a = self.config_manager.get_device_a()
        if current_device_a:
            try:
                index = next(i for i, d in enumerate(devices) if d['id'] == current_device_a['id'])
                device_a_combo.current(index)
            except StopIteration:
                pass

        # 分隔線
        separator = ttk.Separator(inner_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=15)

        # 裝置 B 選擇
        device_b_frame = tk.Frame(inner_frame, bg=card_bg)
        device_b_frame.pack(fill=tk.X, pady=10)

        device_b_icon = tk.Label(
            device_b_frame,
            text="🔊",
            font=("Segoe UI Emoji", 16),
            bg=card_bg
        )
        device_b_icon.pack(side=tk.LEFT, padx=(0, 10))

        device_b_label_frame = tk.Frame(device_b_frame, bg=card_bg)
        device_b_label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        device_b_label = tk.Label(
            device_b_label_frame,
            text="裝置 B",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=card_bg,
            fg=text_color,
            anchor=tk.W
        )
        device_b_label.pack(anchor=tk.W)

        self.device_b_var = tk.StringVar()
        device_b_combo = ttk.Combobox(
            device_b_label_frame,
            textvariable=self.device_b_var,
            values=device_names,
            state="readonly",
            width=50,
            font=("Microsoft JhengHei UI", 10)
        )
        device_b_combo.pack(fill=tk.X, pady=(5, 0))

        # 設定目前的裝置 B
        current_device_b = self.config_manager.get_device_b()
        if current_device_b:
            try:
                index = next(i for i, d in enumerate(devices) if d['id'] == current_device_b['id'])
                device_b_combo.current(index)
            except StopIteration:
                pass

        # === 當前裝置資訊 ===
        current_frame = tk.Frame(main_frame, bg=accent_bg, relief=tk.FLAT, bd=1)
        current_frame.pack(fill=tk.X, pady=(0, 20))

        current_device = self.audio_manager.get_default_device()
        current_text = f"🎵 目前使用: {current_device['name'] if current_device else '未知'}"

        current_info = tk.Label(
            current_frame,
            text=current_text,
            font=("Microsoft JhengHei UI", 10),
            bg=accent_bg,
            fg="#4fc3f7",
            pady=10
        )
        current_info.pack()

        # === 音樂根目錄設定區 ===
        music_path_frame = tk.Frame(main_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        music_path_frame.pack(fill=tk.X, pady=(0, 20))

        music_path_inner = tk.Frame(music_path_frame, bg=card_bg)
        music_path_inner.pack(padx=20, pady=20)

        # 標題
        music_path_title_frame = tk.Frame(music_path_inner, bg=card_bg)
        music_path_title_frame.pack(fill=tk.X, pady=(0, 10))

        music_path_icon = tk.Label(
            music_path_title_frame,
            text="🎵",
            font=("Segoe UI Emoji", 16),
            bg=card_bg
        )
        music_path_icon.pack(side=tk.LEFT, padx=(0, 10))

        music_path_label = tk.Label(
            music_path_title_frame,
            text="音樂根目錄",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=card_bg,
            fg=text_color,
            anchor=tk.W
        )
        music_path_label.pack(side=tk.LEFT)

        # 路徑顯示和瀏覽按鈕
        path_control_frame = tk.Frame(music_path_inner, bg=card_bg)
        path_control_frame.pack(fill=tk.X)

        # 取得目前的音樂根目錄
        # 優先使用 config 中的設定,如果沒有則使用 DEFAULT_MUSIC_ROOT_PATH
        from constants import DEFAULT_MUSIC_ROOT_PATH
        current_music_path = self.config_manager.config.get('music_root_path', DEFAULT_MUSIC_ROOT_PATH)

        self.music_path_var = tk.StringVar(value=current_music_path)
        music_path_entry = tk.Entry(
            path_control_frame,
            textvariable=self.music_path_var,
            font=("Microsoft JhengHei UI", 10),
            bg="#353535",
            fg=text_color,
            insertbackground=text_color,
            relief=tk.FLAT,
            bd=5
        )
        music_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_button = tk.Button(
            path_control_frame,
            text="📁 瀏覽",
            font=("Microsoft JhengHei UI", 10),
            bg="#0078d4",
            fg="white",
            activebackground="#005a9e",
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._browse_music_directory
        )
        browse_button.pack(side=tk.RIGHT)

        # 路徑說明
        path_hint = tk.Label(
            music_path_inner,
            text="設定音樂檔案所在的根目錄",
            font=("Microsoft JhengHei UI", 9),
            bg=card_bg,
            fg=text_secondary,
            anchor=tk.W
        )
        path_hint.pack(fill=tk.X, pady=(5, 0))

        # 網路路徑格式提示
        network_path_hint = tk.Label(
            music_path_inner,
            text="支援格式: 本地路徑 (C:/Music)、網路磁碟機 (Z:/Shuvi) 或 UNC 路徑 (//Server/Share)",
            font=("Microsoft JhengHei UI", 8),
            bg=card_bg,
            fg="#808080",
            anchor=tk.W
        )
        network_path_hint.pack(fill=tk.X, pady=(2, 0))

        # 網路路徑提醒
        network_warning = tk.Label(
            music_path_inner,
            text="網路磁碟機 (如 Z:) 將自動轉換為 UNC 路徑格式以確保 Python 可正確訪問",
            font=("Microsoft JhengHei UI", 8),
            bg=card_bg,
            fg="#4a90e2",
            anchor=tk.W
        )
        network_warning.pack(fill=tk.X, pady=(2, 0))

        # === 按鈕框架 ===
        button_frame = tk.Frame(main_frame, bg=bg_color)
        button_frame.pack(pady=(10, 0))

        # 儲存按鈕
        save_button = ttk.Button(
            button_frame,
            text="✓ 儲存設定",
            command=lambda: self._save_settings(devices, device_a_combo, device_b_combo),
            width=15
        )
        save_button.grid(row=0, column=0, padx=5)

        # 取消按鈕
        cancel_button = ttk.Button(
            button_frame,
            text="✕ 取消",
            command=self._close_window,
            width=15
        )
        cancel_button.grid(row=0, column=1, padx=5)

        # 儲存裝置列表的參考
        self.devices = devices

        # 關閉視窗時的處理
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        # 不要在這裡呼叫 mainloop(),因為主程式已經在執行 mainloop 了
        # self.window.mainloop()

    def _browse_music_directory(self):
        """瀏覽並選擇音樂根目錄"""
        initial_dir = self.music_path_var.get()
        directory = filedialog.askdirectory(
            title="選擇音樂根目錄",
            initialdir=initial_dir if initial_dir else "/"
        )
        if directory:
            # 將路徑標準化為使用正斜線
            directory = directory.replace('\\', '/')
            self.music_path_var.set(directory)

    def _save_settings(self, devices, device_a_combo, device_b_combo):
        """儲存設定"""
        device_a_index = device_a_combo.current()
        device_b_index = device_b_combo.current()

        if device_a_index == -1 or device_b_index == -1:
            messagebox.showwarning("警告", "請選擇兩個裝置")
            return

        if device_a_index == device_b_index:
            messagebox.showwarning("警告", "請選擇兩個不同的裝置")
            return

        # 儲存音訊裝置設定
        self.config_manager.set_device_a(devices[device_a_index])
        self.config_manager.set_device_b(devices[device_b_index])

        # 儲存音樂根目錄設定
        music_path = self.music_path_var.get().strip()
        if music_path:
            # 使用 path_utils 標準化網路路徑
            from path_utils import normalize_network_path
            normalized_path = normalize_network_path(music_path)
            self.config_manager.config['music_root_path'] = normalized_path
            self.config_manager.save_config()

            # 如果路徑被轉換了,通知使用者
            if normalized_path != music_path:
                messagebox.showinfo(
                    "路徑已標準化",
                    f"網路磁碟機路徑已自動轉換為 UNC 格式:\n\n"
                    f"原始: {music_path}\n"
                    f"轉換後: {normalized_path}\n\n"
                    f"這確保 Python 可以正確訪問網路路徑。"
                )

        messagebox.showinfo("成功", "設定已儲存!")

        # 呼叫回調函數
        if self.on_save_callback:
            self.on_save_callback()

        self._close_window()

    def _close_window(self):
        """關閉視窗"""
        if self.window:
            self.window.destroy()
            self.window = None
        # 不要銷毀共用的根視窗
