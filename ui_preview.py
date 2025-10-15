"""現代化 UI 預覽視窗

展示 ttkbootstrap 的圓角按鈕、精緻配色等現代化效果。
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


def show_ui_preview():
    """顯示 UI 預覽視窗"""

    # 創建主視窗（使用 darkly 主題 - Spotify 風格）
    root = ttk.Window(themename="darkly")
    root.title("🎵 現代化 UI 預覽 - Spotify 風格")
    root.geometry("800x600")

    # 主容器
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=BOTH, expand=YES)

    # 標題
    title = ttk.Label(
        main_frame,
        text="🎨 現代化音樂播放器 UI",
        font=("Microsoft JhengHei UI", 24, "bold"),
        bootstyle="inverse-primary"
    )
    title.pack(pady=(0, 20))

    # 說明文字
    desc = ttk.Label(
        main_frame,
        text="這是使用 ttkbootstrap 的現代化 UI 效果\n圓角按鈕 • 精緻配色 • Spotify 風格深色主題",
        font=("Microsoft JhengHei UI", 11),
        bootstyle="secondary"
    )
    desc.pack(pady=(0, 30))

    # 按鈕展示區
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=X, pady=20)

    ttk.Label(button_frame, text="各種圓角按鈕：", font=("Microsoft JhengHei UI", 12, "bold")).pack(anchor=W, pady=(0, 10))

    # 第一排按鈕
    btn_row1 = ttk.Frame(button_frame)
    btn_row1.pack(fill=X, pady=5)

    ttk.Button(btn_row1, text="▶️ 播放", bootstyle=SUCCESS, width=15).pack(side=LEFT, padx=5)
    ttk.Button(btn_row1, text="⏸️ 暫停", bootstyle=PRIMARY, width=15).pack(side=LEFT, padx=5)
    ttk.Button(btn_row1, text="⏹️ 停止", bootstyle=DANGER, width=15).pack(side=LEFT, padx=5)

    # 第二排按鈕
    btn_row2 = ttk.Frame(button_frame)
    btn_row2.pack(fill=X, pady=5)

    ttk.Button(btn_row2, text="📂 開啟檔案", bootstyle="info-outline", width=15).pack(side=LEFT, padx=5)
    ttk.Button(btn_row2, text="💾 儲存", bootstyle="success-outline", width=15).pack(side=LEFT, padx=5)
    ttk.Button(btn_row2, text="🗑️ 刪除", bootstyle="danger-outline", width=15).pack(side=LEFT, padx=5)

    # 卡片展示
    ttk.Separator(main_frame, bootstyle=SECONDARY).pack(fill=X, pady=30)

    ttk.Label(main_frame, text="現代化卡片設計：", font=("Microsoft JhengHei UI", 12, "bold")).pack(anchor=W, pady=(0, 10))

    # 音樂資訊卡片
    card = ttk.Frame(main_frame, bootstyle="dark", relief="raised", borderwidth=1)
    card.pack(fill=X, pady=10, ipady=20, ipadx=20)

    ttk.Label(card, text="🎵 正在播放", font=("Microsoft JhengHei UI", 14, "bold"), bootstyle=SUCCESS).pack(anchor=W)
    ttk.Label(card, text="歌曲名稱：My Favorite Song", font=("Microsoft JhengHei UI", 11)).pack(anchor=W, pady=(5, 2))
    ttk.Label(card, text="藝術家：Various Artists", font=("Microsoft JhengHei UI", 10), bootstyle=SECONDARY).pack(anchor=W)

    # 進度條
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill=X, pady=20)

    ttk.Label(progress_frame, text="播放進度：", font=("Microsoft JhengHei UI", 11)).pack(anchor=W, pady=(0, 5))
    progressbar = ttk.Progressbar(
        progress_frame,
        length=700,
        bootstyle="success-striped",
        mode='determinate',
        value=65
    )
    progressbar.pack(fill=X)

    # 滑桿
    slider_frame = ttk.Frame(main_frame)
    slider_frame.pack(fill=X, pady=20)

    ttk.Label(slider_frame, text="音量控制：", font=("Microsoft JhengHei UI", 11)).pack(anchor=W, pady=(0, 5))
    scale = ttk.Scale(
        slider_frame,
        from_=0,
        to=100,
        orient=HORIZONTAL,
        bootstyle=SUCCESS,
        value=75
    )
    scale.pack(fill=X)

    # 底部按鈕
    bottom_frame = ttk.Frame(main_frame)
    bottom_frame.pack(side=BOTTOM, fill=X, pady=(30, 0))

    ttk.Button(
        bottom_frame,
        text="✅ 應用此主題到音樂播放器",
        bootstyle="success",
        width=30,
        command=lambda: print("準備應用主題...")
    ).pack()

    ttk.Label(
        bottom_frame,
        text="註：完整應用需要重寫部分 UI 程式碼",
        font=("Microsoft JhengHei UI", 9),
        bootstyle="secondary"
    ).pack(pady=(5, 0))

    root.mainloop()


if __name__ == "__main__":
    show_ui_preview()
