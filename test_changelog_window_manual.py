"""手動測試 ChangelogWindow

執行此腳本以測試更新日誌視窗功能。
"""
import tkinter as tk
from changelog_window import ChangelogWindow


def test_changelog_window():
    """測試更新日誌視窗"""
    print("正在啟動更新日誌視窗測試...")

    # 創建 Tkinter 根視窗
    root = tk.Tk()
    root.withdraw()  # 隱藏主視窗

    # 創建並顯示更新日誌視窗
    changelog_window = ChangelogWindow(tk_root=root)
    changelog_window.show()

    print("更新日誌視窗已開啟，請檢查視窗內容")
    print("關閉視窗後測試將結束")

    # 啟動 Tkinter 主循環
    root.mainloop()

    print("測試完成")


if __name__ == "__main__":
    test_changelog_window()
