"""音樂等化器對話框模組

提供圖形化等化器設定介面（使用 ttkbootstrap 現代化風格）。
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class MusicEqualizerDialog:
    """音樂等化器對話框類別

    提供 10 頻段等化器的圖形化設定介面，包含：
    - 啟用/停用開關
    - 預設模式選單
    - 10 個頻段滑桿（即時生效）
    - 重置按鈕
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

        # 建立對話框（使用 ttkbootstrap 風格）
        self.dialog = ttk.Toplevel(self.parent)
        self.dialog.title("🎚️ 等化器設定")
        self.dialog.geometry("800x600")
        self.dialog.resizable(False, False)

        # 主框架
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # === 頂部：啟用開關和預設選單 ===
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=X, pady=(0, 20))

        # 啟用/停用開關
        self.enable_var = ttk.BooleanVar(value=self.equalizer.is_enabled())
        self.enable_checkbox = ttk.Checkbutton(
            top_frame,
            text="啟用等化器",
            variable=self.enable_var,
            command=self._on_enable_toggle,
            bootstyle="success-round-toggle"
        )
        self.enable_checkbox.pack(side=LEFT, padx=(0, 20))

        # 預設模式選單
        preset_frame = ttk.Frame(top_frame)
        preset_frame.pack(side=LEFT, fill=X, expand=YES)

        ttk.Label(
            preset_frame,
            text="預設模式:",
            font=("Microsoft JhengHei UI", 10)
        ).pack(side=LEFT, padx=(0, 10))

        self.preset_var = ttk.StringVar(value=self.equalizer.get_current_preset())

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
            font=("Microsoft JhengHei UI", 10)
        )
        self.preset_combo.pack(side=LEFT)
        self.preset_combo.bind('<<ComboboxSelected>>', self._on_preset_change)

        # 設定當前值
        current_preset = self.equalizer.get_current_preset()
        current_display = f"{current_preset} - {self.equalizer.get_preset_display_name(current_preset)}"
        self.preset_combo.set(current_display)

        # === 中間：頻段滑桿 ===
        sliders_frame = ttk.Frame(main_frame, bootstyle="dark")
        sliders_frame.pack(fill=BOTH, expand=YES, pady=(0, 20))

        # 標題
        ttk.Label(
            sliders_frame,
            text="頻段調整 (-12dB 到 +12dB)",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bootstyle="inverse-dark"
        ).pack(pady=(10, 5))

        # 滑桿容器
        scrollable_frame = ttk.Frame(sliders_frame, padding=10)
        scrollable_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # 建立滑桿
        self.sliders = []
        bands = self.equalizer.get_bands()

        for band in bands:
            freq = band['frequency']
            gain = band['gain']

            # 每個頻段的框架
            band_frame = ttk.Frame(scrollable_frame)
            band_frame.pack(fill=X, pady=5, padx=10)

            # 頻率標籤
            freq_str = f"{freq}Hz" if freq < 1000 else f"{freq // 1000}kHz"
            freq_label = ttk.Label(
                band_frame,
                text=freq_str,
                font=("Microsoft JhengHei UI", 10),
                width=8,
                anchor='w'
            )
            freq_label.pack(side=LEFT, padx=(0, 10))

            # 滑桿變數
            slider_var = ttk.DoubleVar(value=gain)

            # 滑桿（使用 ttkbootstrap 的現代化滑桿）
            scale = ttk.Scale(
                band_frame,
                from_=-12.0,
                to=12.0,
                orient=HORIZONTAL,
                variable=slider_var,
                command=lambda val, f=freq: self._on_slider_change(f, float(val)),
                bootstyle=SUCCESS,
                length=400
            )
            scale.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))

            # 增益值標籤
            gain_label = ttk.Label(
                band_frame,
                text=f"{gain:+.1f}dB",
                font=("Microsoft JhengHei UI", 10),
                width=8,
                anchor='e'
            )
            gain_label.pack(side=LEFT)

            # 保存滑桿資訊
            self.sliders.append({
                'frequency': freq,
                'var': slider_var,
                'scale': scale,
                'label': gain_label
            })

        # === 底部：說明和按鈕 ===
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=X)

        # 說明文字
        note_text = (
            "✨ 提示: 等化器設定會即時應用到音訊播放，無需按套用即可聽到效果。"
            "支援 10 頻段參數 EQ，設定會自動保存。"
        )
        self.note_label = ttk.Label(
            bottom_frame,
            text=note_text,
            font=("Microsoft JhengHei UI", 9, "italic"),
            bootstyle=SUCCESS,
            wraplength=700,
            justify=LEFT
        )
        self.note_label.pack(pady=(0, 15))

        # 按鈕框架
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack()

        # 重置按鈕（居中顯示，使用圓角按鈕）
        reset_btn = ttk.Button(
            button_frame,
            text="🔄 重置為預設值",
            command=self._on_reset,
            bootstyle="info-outline",
            width=20
        )
        reset_btn.pack(padx=5)

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
        self.equalizer.set_enabled(self.enable_var.get())
        # 觸發即時同步
        self._trigger_equalizer_change()

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
                slider_info['label'].config(text=f"{value:+.1f}dB")
                break

        # 更新預設顯示
        current_preset = self.equalizer.get_current_preset()
        current_display = f"{current_preset} - {self.equalizer.get_preset_display_name(current_preset)}"
        self.preset_var.set(current_display)

        # 觸發即時同步
        self._trigger_equalizer_change()

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

        # 觸發即時同步
        self._trigger_equalizer_change()

        # 自動保存設定
        self.equalizer.save_settings()

    def _on_close(self):
        """關閉按鈕事件"""
        if self.dialog:
            self.dialog.destroy()
            self.dialog = None
