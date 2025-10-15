"""測試等化器對話框的現代化 UI"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from music_equalizer import MusicEqualizer
from music_equalizer_dialog import MusicEqualizerDialog
from config_manager import ConfigManager


def test_equalizer_dialog():
    """測試等化器對話框"""
    # 創建主視窗
    root = ttk.Window(themename="darkly")
    root.title("測試等化器 UI")
    root.geometry("400x300")

    # 創建等化器
    config_manager = ConfigManager()
    equalizer = MusicEqualizer(config_manager)

    # 創建對話框
    dialog = MusicEqualizerDialog(
        parent=root,
        equalizer=equalizer,
        on_equalizer_change=lambda: print("等化器已變更")
    )

    # 創建按鈕來顯示對話框
    btn = ttk.Button(
        root,
        text="🎚️ 開啟等化器",
        command=dialog.show,
        bootstyle=SUCCESS,
        width=20
    )
    btn.pack(expand=YES)

    root.mainloop()


if __name__ == "__main__":
    test_equalizer_dialog()
