"""音樂等化器對話框模組

提供圖形化等化器設定介面。
"""
import customtkinter as ctk


class MusicEqualizerDialog:
    """音樂等化器對話框類別

    提供 10 頻段等化器的圖形化設定介面，包含：
    - 啟用/停用開關（使用 CTkSwitch）
    - 預設模式選單（使用 CTkOptionMenu）
    - 10 個頻段滑桿（即時生效，使用 CTkSlider）
    - 重置按鈕（圓角按鈕）
    """

    def __init__(self, parent, equalizer, on_equalizer_change=None):
        """初始化等化器對話框

        Args:
            parent: 父視窗
            equalizer: MusicEqualizer 實例
            on_equalizer_change: 等化器變更時的回調函數 (可選)
        """
        self.parent = parent
        self.equalizer = equalizer
        self.on_equalizer_change = on_equalizer_change
        self.dialog = None

        # UI 元件
        self.enable_switch = None
        self.preset_var = None
        self.preset_menu = None
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
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("等化器設定")
        self.dialog.geometry("800x650")

        # 置頂並聚焦
        self.dialog.transient(self.parent)
        self.dialog.lift()
        self.dialog.focus_force()

        # === 主框架 ===
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # === 頂部：標題和啟用開關 ===
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # 標題
        title_label = ctk.CTkLabel(
            header_frame,
            text="等化器設定",
            font=("Microsoft JhengHei UI", 24, "bold")
        )
        title_label.pack(side="left")

        # 啟用開關（圓角開關）
        self.enable_switch = ctk.CTkSwitch(
            header_frame,
            text="啟用等化器",
            font=("Microsoft JhengHei UI", 14),
            command=self._on_enable_toggle
        )
        self.enable_switch.pack(side="right")
        if self.equalizer.is_enabled():
            self.enable_switch.select()

        # 分隔線
        separator1 = ctk.CTkFrame(main_frame, height=2, fg_color="gray30")
        separator1.pack(fill="x", padx=20, pady=10)

        # === 預設模式選單 ===
        preset_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        preset_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            preset_frame,
            text="預設模式：",
            font=("Microsoft JhengHei UI", 13)
        ).pack(side="left", padx=(0, 10))

        # 準備顯示名稱
        preset_names = self.equalizer.get_preset_names()
        preset_display = [
            f"{name} - {self.equalizer.get_preset_display_name(name)}"
            for name in preset_names
        ]

        # 獲取當前預設
        current_preset = self.equalizer.get_current_preset()
        current_display = f"{current_preset} - {self.equalizer.get_preset_display_name(current_preset)}"

        self.preset_menu = ctk.CTkOptionMenu(
            preset_frame,
            values=preset_display,
            width=300,
            font=("Microsoft JhengHei UI", 12),
            command=self._on_preset_change
        )
        self.preset_menu.set(current_display)
        self.preset_menu.pack(side="left")

        # === 頻段滑桿區域 ===
        sliders_label = ctk.CTkLabel(
            main_frame,
            text="頻段調整 (-12dB 到 +12dB)",
            font=("Microsoft JhengHei UI", 14, "bold")
        )
        sliders_label.pack(pady=(20, 10))

        # 滑桿容器（使用 scrollable frame）
        self.scrollable_frame = ctk.CTkScrollableFrame(
            main_frame,
            height=300,
            corner_radius=10
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 建立滑桿
        self.sliders = []
        bands = self.equalizer.get_bands()

        for band in bands:
            freq = band['frequency']
            gain = band['gain']
            self._create_slider_row(freq, gain)

        # === 底部區域 ===
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=20)

        # 重置按鈕（圓角按鈕）- 居中顯示
        reset_btn = ctk.CTkButton(
            bottom_frame,
            text="重置為預設值",
            font=("Microsoft JhengHei UI", 13),
            height=40,
            width=200,
            corner_radius=10,
            command=self._on_reset
        )
        reset_btn.pack(pady=(0, 10))

        # 提示文字
        self.note_label = ctk.CTkLabel(
            bottom_frame,
            text="等化器調整即時生效，無需按套用。使用視窗右上角 X 關閉。",
            font=("Microsoft JhengHei UI", 11),
            text_color="#4caf50"
        )
        self.note_label.pack()

    def _create_slider_row(self, frequency, gain):
        """建立單個頻段滑桿行

        Args:
            frequency (int): 頻率
            gain (float): 增益值
        """
        # 每個頻段的框架
        row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=8, padx=10)

        # 頻率標籤
        freq_str = f"{frequency}Hz" if frequency < 1000 else f"{frequency // 1000}kHz"
        freq_label = ctk.CTkLabel(
            row_frame,
            text=freq_str,
            font=("Microsoft JhengHei UI", 12),
            width=80
        )
        freq_label.pack(side="left", padx=(0, 10))

        # 滑桿（CustomTkinter 的現代化滑桿）
        slider = ctk.CTkSlider(
            row_frame,
            from_=-12.0,
            to=12.0,
            number_of_steps=48,  # 0.5 的步進
            width=500,
            command=lambda val, f=frequency: self._on_slider_change(f, val)
        )
        slider.set(gain)
        slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # 增益值標籤
        gain_label = ctk.CTkLabel(
            row_frame,
            text=f"{gain:+.1f}dB",
            font=("Microsoft JhengHei UI", 12),
            width=80
        )
        gain_label.pack(side="left")

        # 保存滑桿資訊
        self.sliders.append({
            'frequency': frequency,
            'slider': slider,
            'label': gain_label
        })

    def _trigger_equalizer_change(self):
        """觸發等化器變更回調"""
        if self.on_equalizer_change:
            try:
                self.on_equalizer_change()
            except Exception as e:
                from logger import logger
                logger.error(f"等化器變更回調執行失敗: {e}")

    def _on_enable_toggle(self):
        """啟用/停用開關事件"""
        self.equalizer.set_enabled(self.enable_switch.get())
        # 觸發即時同步
        self._trigger_equalizer_change()

    def _on_preset_change(self, choice):
        """預設模式改變事件"""
        # 從顯示名稱提取實際的 preset key
        if ' - ' in choice:
            preset_key = choice.split(' - ')[0]
        else:
            preset_key = choice

        # 載入預設
        self.equalizer.load_preset(preset_key)

        # 更新滑桿
        self._update_sliders()

        # 觸發即時同步
        self._trigger_equalizer_change()

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
                slider_info['label'].configure(text=f"{value:+.1f}dB")
                break

        # 更新預設顯示
        current_preset = self.equalizer.get_current_preset()
        current_display = f"{current_preset} - {self.equalizer.get_preset_display_name(current_preset)}"
        self.preset_menu.set(current_display)

        # 觸發即時同步
        self._trigger_equalizer_change()

    def _update_sliders(self):
        """更新所有滑桿以反映等化器狀態"""
        bands = self.equalizer.get_bands()
        for i, band in enumerate(bands):
            if i < len(self.sliders):
                slider_info = self.sliders[i]
                slider_info['slider'].set(band['gain'])
                slider_info['label'].configure(text=f"{band['gain']:+.1f}dB")

    def _on_reset(self):
        """重置按鈕事件"""
        # 重置等化器
        self.equalizer.reset()

        # 更新 UI
        self._update_sliders()

        # 更新預設顯示
        current_preset = self.equalizer.get_current_preset()
        current_display = f"{current_preset} - {self.equalizer.get_preset_display_name(current_preset)}"
        self.preset_menu.set(current_display)

        # 觸發即時同步
        self._trigger_equalizer_change()

        # 自動保存設定
        self.equalizer.save_settings()

    def _on_close(self):
        """關閉按鈕事件"""
        if self.dialog:
            self.dialog.destroy()
            self.dialog = None
