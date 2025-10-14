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

    def _create_window(self):
        """建立並配置設定視窗"""
        # 使用共用的根視窗建立 Toplevel 視窗
        if self.tk_root:
            window = tk.Toplevel(self.tk_root)
        else:
            # 如果沒有提供根視窗,建立獨立的視窗
            window = tk.Tk()
        window.title("⚙ 音訊切換工具 - 設定")
        window.geometry("600x750")
        window.resizable(False, False)

        # 設定深色主題顏色
        bg_color = "#1e1e1e"
        window.configure(bg=bg_color)
        return window

    def _create_title_section(self, main_frame, bg_color, text_color, text_secondary):
        """建立標題區塊"""
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

    def _create_device_section(self, main_frame, devices, card_bg, text_color, text_secondary):
        """建立音訊裝置選擇區塊"""
        # === 裝置選擇區 ===
        devices_frame = tk.Frame(main_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        devices_frame.pack(fill=tk.X, pady=(0, 20))

        inner_frame = tk.Frame(devices_frame, bg=card_bg)
        inner_frame.pack(padx=20, pady=20)

        # 取得所有裝置名稱
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
        device_a_combo = self._create_single_device_selector(
            inner_frame, devices, "🎧", "裝置 A",
            card_bg, text_color, is_device_a=True
        )

        # 分隔線
        separator = ttk.Separator(inner_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=15)

        # 裝置 B 選擇
        device_b_combo = self._create_single_device_selector(
            inner_frame, devices, "🔊", "裝置 B",
            card_bg, text_color, is_device_a=False
        )

        return device_a_combo, device_b_combo

    def _create_single_device_selector(self, parent, devices, icon, label_text,
                                      card_bg, text_color, is_device_a):
        """建立單個裝置選擇器"""
        device_frame = tk.Frame(parent, bg=card_bg)
        device_frame.pack(fill=tk.X, pady=10)

        device_icon = tk.Label(
            device_frame,
            text=icon,
            font=("Segoe UI Emoji", 16),
            bg=card_bg
        )
        device_icon.pack(side=tk.LEFT, padx=(0, 10))

        device_label_frame = tk.Frame(device_frame, bg=card_bg)
        device_label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        device_label = tk.Label(
            device_label_frame,
            text=label_text,
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=card_bg,
            fg=text_color,
            anchor=tk.W
        )
        device_label.pack(anchor=tk.W)

        # 建立變數
        if is_device_a:
            self.device_a_var = tk.StringVar()
            device_var = self.device_a_var
        else:
            self.device_b_var = tk.StringVar()
            device_var = self.device_b_var

        device_names = [f"{d['name']}" for d in devices]
        device_combo = ttk.Combobox(
            device_label_frame,
            textvariable=device_var,
            values=device_names,
            state="readonly",
            width=50,
            font=("Microsoft JhengHei UI", 10)
        )
        device_combo.pack(fill=tk.X, pady=(5, 0))

        # 設定目前的裝置
        current_device = (self.config_manager.get_device_a() if is_device_a
                         else self.config_manager.get_device_b())
        if current_device:
            try:
                index = next(i for i, d in enumerate(devices) if d['id'] == current_device['id'])
                device_combo.current(index)
            except StopIteration:
                pass

        return device_combo

    def _create_current_device_info(self, main_frame, accent_bg):
        """建立當前裝置資訊區塊"""
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

    def _create_music_path_section(self, main_frame, card_bg, text_color, text_secondary):
        """建立音樂根目錄設定區塊"""
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
        hints = [
            ("設定音樂檔案所在的根目錄", 9, text_secondary),
            ("支援格式: 本地路徑 (C:/Music)、網路磁碟機 (Z:/Shuvi) 或 UNC 路徑 (//Server/Share)", 8, "#808080"),
            ("網路磁碟機 (如 Z:) 將自動轉換為 UNC 路徑格式以確保 Python 可正確訪問", 8, "#4a90e2")
        ]

        for hint_text, font_size, color in hints:
            hint_label = tk.Label(
                music_path_inner,
                text=hint_text,
                font=("Microsoft JhengHei UI", font_size),
                bg=card_bg,
                fg=color,
                anchor=tk.W
            )
            hint_label.pack(fill=tk.X, pady=(5 if font_size == 9 else 2, 0))

    def _create_metadata_section(self, main_frame, card_bg, text_color, text_secondary):
        """建立音樂資訊自動補全設定區塊"""
        metadata_frame = tk.Frame(main_frame, bg=card_bg, relief=tk.RIDGE, bd=1)
        metadata_frame.pack(fill=tk.X, pady=(0, 20))

        metadata_inner = tk.Frame(metadata_frame, bg=card_bg)
        metadata_inner.pack(padx=20, pady=20)

        # 標題
        metadata_title_frame = tk.Frame(metadata_inner, bg=card_bg)
        metadata_title_frame.pack(fill=tk.X, pady=(0, 10))

        metadata_icon = tk.Label(
            metadata_title_frame,
            text="🔄",
            font=("Segoe UI Emoji", 16),
            bg=card_bg
        )
        metadata_icon.pack(side=tk.LEFT, padx=(0, 10))

        metadata_label = tk.Label(
            metadata_title_frame,
            text="音樂資訊自動補全",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=card_bg,
            fg=text_color,
            anchor=tk.W
        )
        metadata_label.pack(side=tk.LEFT)

        # 啟用選項
        self.auto_fetch_var = tk.BooleanVar(
            value=self.config_manager.get("auto_fetch_metadata", True)
        )

        metadata_check_frame = tk.Frame(metadata_inner, bg=card_bg)
        metadata_check_frame.pack(fill=tk.X)

        metadata_checkbox = tk.Checkbutton(
            metadata_check_frame,
            text="啟用自動補全音樂資訊",
            variable=self.auto_fetch_var,
            font=("Microsoft JhengHei UI", 10),
            bg=card_bg,
            fg=text_color,
            selectcolor=card_bg,
            activebackground=card_bg,
            activeforeground=text_color
        )
        metadata_checkbox.pack(anchor=tk.W)

        # 功能說明
        hints = [
            ("播放時自動抓取缺失的專輯封面、藝術家、專輯名稱等資訊", 9, text_secondary),
            ("資料來源: iTunes Search API", 8, "#808080")
        ]

        for hint_text, font_size, color in hints:
            hint_label = tk.Label(
                metadata_inner,
                text=hint_text,
                font=("Microsoft JhengHei UI", font_size),
                bg=card_bg,
                fg=color,
                anchor=tk.W
            )
            hint_label.pack(fill=tk.X, pady=(5 if font_size == 9 else 2, 0))

    def _create_button_section(self, main_frame, devices, device_a_combo, device_b_combo, bg_color):
        """建立按鈕區塊"""
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

    def show(self):
        """顯示設定視窗"""
        if self.window is not None:
            self.window.lift()
            self.window.focus_force()
            return

        self.window = self._create_window()

        # 設定深色主題顏色
        bg_color = "#1e1e1e"
        card_bg = "#2d2d2d"
        text_color = "#e0e0e0"
        text_secondary = "#a0a0a0"
        accent_bg = "#1a3a52"

        # 建立主框架
        main_frame = tk.Frame(self.window, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # 取得所有裝置
        devices = self.audio_manager.get_all_output_devices()

        # 建立各個區塊
        self._create_title_section(main_frame, bg_color, text_color, text_secondary)
        device_a_combo, device_b_combo = self._create_device_section(
            main_frame, devices, card_bg, text_color, text_secondary
        )
        self._create_current_device_info(main_frame, accent_bg)
        self._create_music_path_section(main_frame, card_bg, text_color, text_secondary)
        self._create_metadata_section(main_frame, card_bg, text_color, text_secondary)
        self._create_button_section(main_frame, devices, device_a_combo, device_b_combo, bg_color)

        # 儲存裝置列表的參考
        self.devices = devices

        # 關閉視窗時的處理
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

    def _browse_music_directory(self):
        """瀏覽並選擇音樂根目錄"""
        from logger import logger
        initial_dir = self.music_path_var.get()
        directory = filedialog.askdirectory(
            title="選擇音樂根目錄",
            initialdir=initial_dir if initial_dir else "/"
        )
        if directory:
            # 將路徑標準化為使用正斜線
            directory = directory.replace('\\', '/')
            self.music_path_var.set(directory)

            # 自動儲存選擇的路徑
            logger.info(f"[設定視窗] 瀏覽選擇路徑: {directory}")
            from path_utils import normalize_network_path
            normalized_path = normalize_network_path(directory)
            self.config_manager.config['music_root_path'] = normalized_path
            self.config_manager.save_config()
            logger.info(f"[設定視窗] 路徑已自動儲存: {normalized_path}")

            # 如果路徑被轉換了,通知使用者
            if normalized_path != directory:
                messagebox.showinfo(
                    "路徑已儲存",
                    f"網路磁碟機路徑已自動轉換並儲存為 UNC 格式:\n\n"
                    f"原始: {directory}\n"
                    f"儲存為: {normalized_path}\n\n"
                    f"這確保 Python 可以正確訪問網路路徑。"
                )
            else:
                messagebox.showinfo("路徑已儲存", f"音樂路徑已成功儲存:\n{normalized_path}")

            # 呼叫回調函數
            if self.on_save_callback:
                self.on_save_callback()

    def _save_music_path_and_metadata(self):
        """儲存音樂路徑和自動補全設定

        Returns:
            tuple: (settings_saved, normalized_path, original_path)
        """
        from logger import logger
        from path_utils import normalize_network_path

        settings_saved = False
        normalized_path = ""

        # 儲存音樂根目錄設定
        music_path = self.music_path_var.get().strip()
        logger.info(f"[設定視窗] 音樂路徑: {music_path}")
        if music_path:
            normalized_path = normalize_network_path(music_path)
            self.config_manager.config['music_root_path'] = normalized_path
            self.config_manager.save_config()
            settings_saved = True

        # 儲存自動補全設定
        auto_fetch_enabled = self.auto_fetch_var.get()
        self.config_manager.set("auto_fetch_metadata", auto_fetch_enabled)
        logger.info(f"[設定視窗] 自動補全音樂資訊: {auto_fetch_enabled}")
        settings_saved = True

        # 如果路徑被轉換了,通知使用者
        if music_path and music_path != normalized_path:
            messagebox.showinfo(
                "路徑已標準化",
                f"網路磁碟機路徑已自動轉換為 UNC 格式:\n\n"
                f"原始: {music_path}\n"
                f"轉換後: {normalized_path}\n\n"
                f"這確保 Python 可以正確訪問網路路徑。"
            )

        return settings_saved, normalized_path, music_path

    def _is_device_selected(self, device_index):
        """檢查裝置是否被選擇

        Args:
            device_index: 裝置索引

        Returns:
            bool: 是否已選擇裝置
        """
        return device_index != -1

    def _show_incomplete_device_warning(self, settings_saved):
        """顯示裝置選擇不完整的警告訊息

        Args:
            settings_saved: 是否已有其他設定被儲存
        """
        warning_msg = ("音樂路徑已儲存,但音訊裝置設定不完整。\n請選擇兩個裝置以儲存音訊設定。"
                     if settings_saved else "請選擇兩個裝置")
        messagebox.showwarning("部分儲存" if settings_saved else "警告", warning_msg)

    def _show_duplicate_device_warning(self, settings_saved):
        """顯示裝置重複選擇的警告訊息

        Args:
            settings_saved: 是否已有其他設定被儲存
        """
        warning_msg = ("音樂路徑已儲存,但請選擇兩個不同的裝置以儲存音訊設定。"
                     if settings_saved else "請選擇兩個不同的裝置")
        messagebox.showwarning("部分儲存" if settings_saved else "警告", warning_msg)

    def _save_device_configuration(self, devices, device_a_index, device_b_index):
        """儲存裝置配置到設定檔

        Args:
            devices: 裝置列表
            device_a_index: 裝置 A 的索引
            device_b_index: 裝置 B 的索引
        """
        self.config_manager.set_device_a(devices[device_a_index])
        self.config_manager.set_device_b(devices[device_b_index])

    def _validate_and_save_devices(self, devices, device_a_index, device_b_index, settings_saved):
        """驗證並儲存音訊裝置設定

        Args:
            devices: 裝置列表
            device_a_index: 裝置 A 的索引
            device_b_index: 裝置 B 的索引
            settings_saved: 是否已有設定被儲存

        Returns:
            bool: 是否成功儲存裝置設定
        """
        # 如果沒有選擇任何裝置,直接返回
        if not self._is_device_selected(device_a_index) and not self._is_device_selected(device_b_index):
            return settings_saved

        # 檢查是否只選擇了一個裝置
        if not self._is_device_selected(device_a_index) or not self._is_device_selected(device_b_index):
            self._show_incomplete_device_warning(settings_saved)
            return settings_saved

        # 檢查是否選擇了相同裝置
        if device_a_index == device_b_index:
            self._show_duplicate_device_warning(settings_saved)
            return settings_saved

        # 儲存音訊裝置設定
        self._save_device_configuration(devices, device_a_index, device_b_index)
        return True

    def _show_success_and_close(self):
        """顯示成功訊息並關閉視窗"""
        messagebox.showinfo("成功", "設定已儲存!")

        # 呼叫回調函數
        if self.on_save_callback:
            self.on_save_callback()

        self._close_window()

    def _save_settings(self, devices, device_a_combo, device_b_combo):
        """儲存設定"""
        from logger import logger
        logger.info("[設定視窗] 開始儲存設定...")

        # 儲存音樂路徑和自動補全設定
        settings_saved, _, _ = self._save_music_path_and_metadata()

        # 取得裝置索引
        device_a_index = device_a_combo.current()
        device_b_index = device_b_combo.current()

        # 驗證並儲存裝置設定
        settings_saved = self._validate_and_save_devices(
            devices, device_a_index, device_b_index, settings_saved
        )

        # 顯示結果
        if settings_saved:
            self._show_success_and_close()
        else:
            messagebox.showwarning("警告", "沒有可儲存的設定變更")

    def _close_window(self):
        """關閉視窗"""
        if self.window:
            self.window.destroy()
            self.window = None
        # 不要銷毀共用的根視窗
