"""更新日誌視窗模組

提供查看專案更新歷史的圖形化介面。
"""
import customtkinter as ctk
import os
from src.core.logger import logger


class ChangelogWindow:
    """更新日誌視窗類別

    顯示 CHANGELOG.md 的內容，提供版本更新歷史查看功能。
    """

    def __init__(self, tk_root=None):
        """初始化更新日誌視窗

        Args:
            tk_root: Tkinter 根視窗（可選）
        """
        self.tk_root = tk_root
        self.window = None

        # 深色主題顏色
        self.bg_color = "#1e1e1e"
        self.text_bg_color = "#2d2d2d"
        self.text_color = "#e0e0e0"
        self.title_color = "#0078d4"
        self.accent_color = "#0078d4"

    def show(self):
        """顯示更新日誌視窗"""
        if self.window is not None:
            try:
                self.window.deiconify()  # 顯示被隱藏的視窗
                self.window.lift()
                self.window.focus_force()
                return
            except:
                self.window = None

        # 創建新視窗
        if self.tk_root:
            self.window = ctk.CTkToplevel(self.tk_root)
            self.window.transient(self.tk_root)
        else:
            self.window = ctk.CTk()

        self.window.title("📝 更新日誌")
        self.window.geometry("900x700")

        # 自動置頂並聚焦
        self.window.lift()
        self.window.focus_force()

        # 創建主框架
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 標題
        title_label = ctk.CTkLabel(
            main_frame,
            text="📝 更新日誌",
            font=("Microsoft JhengHei UI", 18, "bold"),
            text_color=self.title_color
        )
        title_label.pack(pady=(0, 15))

        # 副標題
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="專案版本更新歷史",
            font=("Microsoft JhengHei UI", 10),
            text_color=self.text_color
        )
        subtitle_label.pack(pady=(0, 20))

        # 創建文字框架
        text_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        text_frame.pack(fill="both", expand=True)

        # 創建可滾動文字區域（使用 CTkTextbox）
        self.text_widget = ctk.CTkTextbox(
            text_frame,
            wrap="word",
            font=("Consolas", 13),
            corner_radius=10,
            fg_color=self.text_bg_color,
            text_color=self.text_color
        )
        self.text_widget.pack(fill="both", expand=True)

        # 載入並顯示 CHANGELOG
        self._load_changelog()

        # 綁定關閉事件
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        logger.info("更新日誌視窗已開啟")

    def _load_changelog(self):
        """載入並顯示 CHANGELOG.md"""
        # 從專案根目錄的 docs 資料夾中讀取 CHANGELOG.md
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        changelog_path = os.path.join(project_root, "docs", "CHANGELOG.md")

        if not os.path.exists(changelog_path):
            self._show_error("找不到 CHANGELOG.md 文件")
            return

        try:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self._display_changelog(content)
            logger.info("成功載入更新日誌")

        except Exception as e:
            logger.error(f"載入更新日誌失敗: {e}")
            self._show_error(f"載入失敗: {e}")

    def _display_changelog(self, content):
        """顯示更新日誌內容

        Args:
            content (str): CHANGELOG.md 的內容
        """
        self.text_widget.insert("0.0", content)
        self.text_widget.configure(state="disabled")

    def _show_error(self, message):
        """顯示錯誤訊息

        Args:
            message (str): 錯誤訊息
        """
        self.text_widget.insert("0.0", f"❌ 錯誤\n\n{message}")
        self.text_widget.configure(state="disabled")

    def _close_window(self):
        """關閉視窗（隱藏而非銷毀）"""
        if self.window:
            self.window.withdraw()
            logger.info("更新日誌視窗已隱藏")
