"""更新日誌視窗模組

提供查看專案更新歷史的圖形化介面。
"""
import tkinter as tk
from tkinter import scrolledtext
import os
from logger import logger


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
                self.window.lift()
                self.window.focus_force()
                return
            except:
                self.window = None

        # 創建新視窗
        if self.tk_root:
            self.window = tk.Toplevel(self.tk_root)
        else:
            self.window = tk.Tk()

        self.window.title("📝 更新日誌")
        self.window.geometry("900x700")
        self.window.configure(bg=self.bg_color)

        # 設定視窗圖示（如果需要）
        try:
            # 可以在這裡設定圖示
            pass
        except:
            pass

        # 創建主框架
        main_frame = tk.Frame(self.window, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        title_label = tk.Label(
            main_frame,
            text="📝 更新日誌",
            font=("Microsoft JhengHei UI", 16, "bold"),
            bg=self.bg_color,
            fg=self.title_color
        )
        title_label.pack(pady=(0, 15))

        # 副標題
        subtitle_label = tk.Label(
            main_frame,
            text="專案版本更新歷史",
            font=("Microsoft JhengHei UI", 10),
            bg=self.bg_color,
            fg=self.text_color
        )
        subtitle_label.pack(pady=(0, 20))

        # 創建文字框架
        text_frame = tk.Frame(main_frame, bg=self.bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # 創建可滾動文字區域
        self.text_widget = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=self.text_bg_color,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            padx=15,
            pady=15,
            state=tk.DISABLED
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # 配置文字標籤樣式
        self._configure_text_tags()

        # 載入並顯示 CHANGELOG
        self._load_changelog()

        # 關閉按鈕
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=(15, 0))

        close_button = tk.Button(
            button_frame,
            text="關閉",
            command=self._close_window,
            bg=self.accent_color,
            fg="white",
            font=("Microsoft JhengHei UI", 10, "bold"),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor="hand2"
        )
        close_button.pack()

        # 綁定關閉事件
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        logger.info("更新日誌視窗已開啟")

    def _configure_text_tags(self):
        """配置文字標籤樣式"""
        # 標題樣式 (# 開頭)
        self.text_widget.tag_config(
            "h1",
            font=("Microsoft JhengHei UI", 14, "bold"),
            foreground="#0078d4",
            spacing1=10,
            spacing3=10
        )

        self.text_widget.tag_config(
            "h2",
            font=("Microsoft JhengHei UI", 12, "bold"),
            foreground="#4db8ff",
            spacing1=8,
            spacing3=5
        )

        self.text_widget.tag_config(
            "h3",
            font=("Microsoft JhengHei UI", 11, "bold"),
            foreground="#80ccff",
            spacing1=5,
            spacing3=3
        )

        # 強調文字 (✅, ❌, ⚠️ 等)
        self.text_widget.tag_config(
            "emoji",
            font=("Segoe UI Emoji", 10)
        )

        # 程式碼/檔案名稱 (` ` 包圍)
        self.text_widget.tag_config(
            "code",
            font=("Consolas", 10),
            foreground="#ce9178",
            background="#3c3c3c"
        )

        # 列表項目
        self.text_widget.tag_config(
            "list",
            lmargin1=30,
            lmargin2=50
        )

    def _load_changelog(self):
        """載入並顯示 CHANGELOG.md"""
        changelog_path = os.path.join(
            os.path.dirname(__file__),
            "CHANGELOG.md"
        )

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
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)

        lines = content.split('\n')

        for line in lines:
            # 根據不同的 Markdown 語法添加樣式
            if line.startswith('# '):
                # 一級標題
                self.text_widget.insert(tk.END, line + '\n', 'h1')
            elif line.startswith('## '):
                # 二級標題
                self.text_widget.insert(tk.END, line + '\n', 'h2')
            elif line.startswith('### '):
                # 三級標題
                self.text_widget.insert(tk.END, line + '\n', 'h3')
            elif line.strip().startswith(('- ', '* ')):
                # 列表項目
                self.text_widget.insert(tk.END, line + '\n', 'list')
            else:
                # 普通文字
                self._insert_formatted_line(line + '\n')

        self.text_widget.config(state=tk.DISABLED)
        # 滾動到頂部
        self.text_widget.see("1.0")

    def _insert_formatted_line(self, line):
        """插入格式化的行（處理程式碼標記）

        Args:
            line (str): 要插入的行
        """
        # 簡單處理 `code` 標記
        import re

        parts = re.split(r'(`[^`]+`)', line)

        for part in parts:
            if part.startswith('`') and part.endswith('`'):
                # 程式碼部分
                self.text_widget.insert(tk.END, part[1:-1], 'code')
            else:
                # 普通文字
                self.text_widget.insert(tk.END, part)

    def _show_error(self, message):
        """顯示錯誤訊息

        Args:
            message (str): 錯誤訊息
        """
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(
            tk.END,
            f"❌ 錯誤\n\n{message}",
            'h2'
        )
        self.text_widget.config(state=tk.DISABLED)

    def _close_window(self):
        """關閉視窗"""
        if self.window:
            self.window.destroy()
            self.window = None
            logger.info("更新日誌視窗已關閉")
