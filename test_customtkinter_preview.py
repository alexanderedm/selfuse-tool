"""CustomTkinter 等化器對話框預覽

展示 CustomTkinter 的現代化 UI 效果，包含：
- 圓角按鈕
- 現代化滑桿
- 開關元件
- 深色主題
"""
import customtkinter as ctk
import tkinter as tk


class CustomTkinterEqualizerPreview:
    """CustomTkinter 等化器預覽視窗"""

    def __init__(self):
        # 設定 CustomTkinter 外觀
        ctk.set_appearance_mode("dark")  # 深色模式
        ctk.set_default_color_theme("blue")  # 主題顏色

        # 建立主視窗
        self.window = ctk.CTk()
        self.window.title("等化器設定（CustomTkinter 預覽）")
        self.window.geometry("800x650")

        # 建立 UI
        self._create_ui()

    def _create_ui(self):
        """建立 UI 元件"""
        # 主框架
        main_frame = ctk.CTkFrame(self.window, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # === 頂部：標題和啟用開關 ===
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # 標題
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎛️ 等化器設定",
            font=("Microsoft JhengHei UI", 24, "bold")
        )
        title_label.pack(side="left")

        # 啟用開關（圓角開關）
        self.enable_switch = ctk.CTkSwitch(
            header_frame,
            text="啟用等化器",
            font=("Microsoft JhengHei UI", 14),
            command=self._on_switch_toggle
        )
        self.enable_switch.pack(side="right")
        self.enable_switch.select()  # 預設開啟

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

        self.preset_combo = ctk.CTkOptionMenu(
            preset_frame,
            values=["flat - 平坦", "pop - 流行", "rock - 搖滾", "classical - 古典",
                    "jazz - 爵士", "vocal - 人聲", "bass_boost - 重低音", "soft - 柔和"],
            width=250,
            font=("Microsoft JhengHei UI", 12),
            command=self._on_preset_change
        )
        self.preset_combo.pack(side="left")

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

        # 建立 10 個頻段滑桿
        self.sliders = []
        frequencies = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000]

        for freq in frequencies:
            self._create_slider_row(freq)

        # === 底部區域 ===
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=20)

        # 重置按鈕（圓角按鈕）- 居中顯示
        reset_btn = ctk.CTkButton(
            bottom_frame,
            text="🔄 重置為預設值",
            font=("Microsoft JhengHei UI", 13),
            height=40,
            width=200,
            corner_radius=10,
            command=self._on_reset
        )
        reset_btn.pack(pady=(0, 10))

        # 提示文字
        tip_label = ctk.CTkLabel(
            bottom_frame,
            text="✨ 等化器調整即時生效，無需按套用。使用視窗右上角 X 關閉。",
            font=("Microsoft JhengHei UI", 11),
            text_color="#4caf50"
        )
        tip_label.pack()

    def _create_slider_row(self, frequency):
        """建立單個頻段滑桿行

        Args:
            frequency (int): 頻率
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
        slider.set(0.0)  # 預設值
        slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # 增益值標籤
        gain_label = ctk.CTkLabel(
            row_frame,
            text="+0.0dB",
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

    def _on_switch_toggle(self):
        """啟用開關切換事件"""
        state = "已啟用" if self.enable_switch.get() else "已停用"
        print(f"等化器{state}")

    def _on_preset_change(self, choice):
        """預設模式改變事件"""
        print(f"切換預設模式：{choice}")
        # 這裡可以根據預設模式調整滑桿

    def _on_slider_change(self, frequency, value):
        """滑桿改變事件"""
        # 更新增益標籤
        for slider_info in self.sliders:
            if slider_info['frequency'] == frequency:
                slider_info['label'].configure(text=f"{value:+.1f}dB")
                break
        print(f"{frequency}Hz: {value:+.1f}dB")

    def _on_reset(self):
        """重置按鈕事件"""
        print("重置所有頻段為 0dB")
        for slider_info in self.sliders:
            slider_info['slider'].set(0.0)
            slider_info['label'].configure(text="+0.0dB")

    def run(self):
        """運行視窗"""
        self.window.mainloop()


if __name__ == "__main__":
    app = CustomTkinterEqualizerPreview()
    app.run()
