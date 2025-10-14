"""音樂等化器對話框模組

提供圖形化等化器設定介面。
"""
import tkinter as tk
from tkinter import ttk


class MusicEqualizerDialog:
    """音樂等化器對話框類別

    提供 10 頻段等化器的圖形化設定介面，包含：
    - 啟用/停用開關
    - 預設模式選單
    - 10 個頻段滑桿
    - 重置和套用按鈕
    """

    def __init__(self, parent, equalizer):
        """初始化等化器對話框

        Args:
            parent: 父視窗
            equalizer: MusicEqualizer 實例
        """
        self.parent = parent
        self.equalizer = equalizer
        self.dialog = None

        # UI 元件
        self.enable_var = None
        self.enable_checkbox = None
        self.preset_var = None
        self.preset_combo = None
        self.sliders = []  # 存儲滑桿資訊
        self.note_label = None

    def show(self):
        """顯示等化器對話框"""
        if self.dialog is not None:
            try:
                self.dialog.lift()
                self.dialog.focus_force()
                return
            except:
                self.dialog = None

        # 建立對話框
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("等化器設定")
        self.dialog.geometry("800x600")
        self.dialog.resizable(False, False)

        # 深色主題顏色
        bg_color = "#1e1e1e"
        card_bg = "#2d2d2d"
        text_color = "#e0e0e0"
        accent_color = "#0078d4"

        self.dialog.configure(bg=bg_color)

        # 主框架
        main_frame = tk.Frame(self.dialog, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # === 頂部：啟用開關和預設選單 ===
        top_frame = tk.Frame(main_frame, bg=bg_color)
        top_frame.pack(fill=tk.X, pady=(0, 20))

        # 啟用/停用開關
        self.enable_var = tk.BooleanVar(value=self.equalizer.is_enabled())
        self.enable_checkbox = tk.Checkbutton(
            top_frame,
            text="啟用等化器",
            variable=self.enable_var,
            command=self._on_enable_toggle,
            bg=bg_color,
            fg=text_color,
            selectcolor=card_bg,
            activebackground=bg_color,
            activeforeground=text_color,
            font=("Segoe UI", 12, "bold")
        )
        self.enable_checkbox.pack(side=tk.LEFT, padx=(0, 20))

        # 預設模式選單
        preset_frame = tk.Frame(top_frame, bg=bg_color)
        preset_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            preset_frame,
            text="預設模式:",
            bg=bg_color,
            fg=text_color,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.preset_var = tk.StringVar(value=self.equalizer.get_current_preset())

        # 準備顯示名稱
        preset_names = self.equalizer.get_preset_names()
        preset_display = [
            f"{name} - {self.equalizer.get_preset_display_name(name)}"
            for name in preset_names
        ]

        self.preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=preset_display,
            state='readonly',
            width=20,
            font=("Segoe UI", 10)
        )
        self.preset_combo.pack(side=tk.LEFT)
        self.preset_combo.bind('<<ComboboxSelected>>', self._on_preset_change)

        # 設定當前值
        current_preset = self.equalizer.get_current_preset()
        current_display = f"{current_preset} - {self.equalizer.get_preset_display_name(current_preset)}"
        self.preset_combo.set(current_display)

        # === 中間：頻段滑桿 ===
        sliders_frame = tk.Frame(main_frame, bg=card_bg)
        sliders_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # 標題
        tk.Label(
            sliders_frame,
            text="頻段調整 (-12dB 到 +12dB)",
            bg=card_bg,
            fg=text_color,
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(10, 5))

        # 滑桿容器（使用 Canvas 和 Scrollbar）
        canvas = tk.Canvas(sliders_frame, bg=card_bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(sliders_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=card_bg)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 建立滑桿
        self.sliders = []
        bands = self.equalizer.get_bands()

        for band in bands:
            freq = band['frequency']
            gain = band['gain']

            # 每個頻段的框架
            band_frame = tk.Frame(scrollable_frame, bg=card_bg)
            band_frame.pack(fill=tk.X, pady=5, padx=10)

            # 頻率標籤
            freq_str = f"{freq}Hz" if freq < 1000 else f"{freq // 1000}kHz"
            freq_label = tk.Label(
                band_frame,
                text=freq_str,
                bg=card_bg,
                fg=text_color,
                font=("Segoe UI", 10),
                width=8,
                anchor='w'
            )
            freq_label.pack(side=tk.LEFT, padx=(0, 10))

            # 滑桿變數
            slider_var = tk.DoubleVar(value=gain)

            # 滑桿
            scale = tk.Scale(
                band_frame,
                from_=-12.0,
                to=12.0,
                resolution=0.5,
                orient=tk.HORIZONTAL,
                variable=slider_var,
                command=lambda val, f=freq: self._on_slider_change(f, float(val)),
                bg=card_bg,
                fg=text_color,
                troughcolor=bg_color,
                activebackground=accent_color,
                highlightthickness=0,
                length=400,
                showvalue=0
            )
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

            # 增益值標籤
            gain_label = tk.Label(
                band_frame,
                text=f"{gain:+.1f}dB",
                bg=card_bg,
                fg=text_color,
                font=("Segoe UI", 10),
                width=8,
                anchor='e'
            )
            gain_label.pack(side=tk.LEFT)

            # 保存滑桿資訊
            self.sliders.append({
                'frequency': freq,
                'var': slider_var,
                'scale': scale,
                'label': gain_label
            })

        # === 底部：說明和按鈕 ===
        bottom_frame = tk.Frame(main_frame, bg=bg_color)
        bottom_frame.pack(fill=tk.X)

        # 說明文字
        note_text = (
            "注意: 當前版本僅保存等化器設定，"
            "音訊效果應用功能待未來整合音訊處理庫實現。"
        )
        self.note_label = tk.Label(
            bottom_frame,
            text=note_text,
            bg=bg_color,
            fg="#ffa500",
            font=("Segoe UI", 9, "italic"),
            wraplength=700,
            justify=tk.LEFT
        )
        self.note_label.pack(pady=(0, 15))

        # 按鈕框架
        button_frame = tk.Frame(bottom_frame, bg=bg_color)
        button_frame.pack()

        # 重置按鈕
        reset_btn = tk.Button(
            button_frame,
            text="重置",
            command=self._on_reset,
            bg=card_bg,
            fg=text_color,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

        # 套用按鈕
        apply_btn = tk.Button(
            button_frame,
            text="套用",
            command=self._on_apply,
            bg=accent_color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        apply_btn.pack(side=tk.LEFT, padx=5)

        # 關閉按鈕
        close_btn = tk.Button(
            button_frame,
            text="關閉",
            command=self._on_close,
            bg=card_bg,
            fg=text_color,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        close_btn.pack(side=tk.LEFT, padx=5)

    def _on_enable_toggle(self):
        """啟用/停用開關事件"""
        self.equalizer.set_enabled(self.enable_var.get())

    def _on_preset_change(self, event):
        """預設模式改變事件"""
        # 從顯示名稱提取實際的 preset key
        selected = self.preset_var.get()
        if ' - ' in selected:
            preset_key = selected.split(' - ')[0]
        else:
            preset_key = selected

        # 載入預設
        self.equalizer.load_preset(preset_key)

        # 更新滑桿
        self._update_sliders()

    def _on_slider_change(self, frequency, value):
        """滑桿改變事件

        Args:
            frequency (int): 頻率
            value (float): 增益值
        """
        # 更新等化器
        self.equalizer.set_band_gain(frequency, value)

        # 更新增益標籤
        for slider_info in self.sliders:
            if slider_info['frequency'] == frequency:
                slider_info['label'].config(text=f"{value:+.1f}dB")
                break

        # 更新預設顯示
        current_preset = self.equalizer.get_current_preset()
        current_display = f"{current_preset} - {self.equalizer.get_preset_display_name(current_preset)}"
        self.preset_var.set(current_display)

    def _update_sliders(self):
        """更新所有滑桿以反映等化器狀態"""
        bands = self.equalizer.get_bands()
        for i, band in enumerate(bands):
            if i < len(self.sliders):
                slider_info = self.sliders[i]
                slider_info['var'].set(band['gain'])
                slider_info['label'].config(text=f"{band['gain']:+.1f}dB")

    def _on_reset(self):
        """重置按鈕事件"""
        # 重置等化器
        self.equalizer.reset()

        # 更新 UI
        self._update_sliders()

        # 更新預設顯示
        current_preset = self.equalizer.get_current_preset()
        current_display = f"{current_preset} - {self.equalizer.get_preset_display_name(current_preset)}"
        self.preset_var.set(current_display)

    def _on_apply(self):
        """套用按鈕事件"""
        # 儲存設定
        self.equalizer.save_settings()

        # 可選：顯示提示訊息
        # messagebox.showinfo("成功", "等化器設定已儲存")

    def _on_close(self):
        """關閉按鈕事件"""
        if self.dialog:
            self.dialog.destroy()
            self.dialog = None
