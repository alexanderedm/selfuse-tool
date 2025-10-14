"""RSS Preview View 模組 - 預覽視圖"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
import html
from logger import logger


class RSSPreviewView:
    """RSS 預覽視圖類別"""

    def __init__(self, parent):
        """初始化預覽視圖

        Args:
            parent: 父容器
        """
        self.parent = parent
        self.preview_text = None
        self.open_browser_button = None
        self.current_entry = None

        self._create_ui()

    def _create_ui(self):
        """建立預覽 UI"""
        # 深色主題顏色
        card_bg = "#2d2d2d"
        header_bg = "#0d47a1"
        text_color = "#e0e0e0"
        text_secondary = "#a0a0a0"

        # 右側容器
        right_container = tk.Frame(self.parent, bg=card_bg, relief=tk.RIDGE, bd=1)
        right_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 標題框架
        preview_header_frame = tk.Frame(right_container, bg=header_bg)
        preview_header_frame.pack(fill=tk.X)

        preview_header = tk.Label(
            preview_header_frame,
            text="📖 完整內文",
            font=("Microsoft JhengHei UI", 11, "bold"),
            bg=header_bg,
            fg="white",
            pady=8
        )
        preview_header.pack(side=tk.LEFT, padx=10)

        # 在瀏覽器開啟按鈕
        self.open_browser_button = ttk.Button(
            preview_header_frame,
            text="🌐 在瀏覽器開啟",
            command=self._open_in_browser,
            style="Accent.TButton"
        )
        self.open_browser_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # 內文預覽文字框
        preview_frame = tk.Frame(right_container, bg=card_bg)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.preview_text = scrolledtext.ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            font=("Microsoft JhengHei UI", 10),
            bg="#252525",
            fg=text_color,
            relief=tk.FLAT,
            padx=15,
            pady=15,
            insertbackground=text_color
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.config(state=tk.DISABLED)

        # 設定文字標籤樣式 - 深色主題
        self.preview_text.tag_config("title", font=("Microsoft JhengHei UI", 14, "bold"), foreground="#4fc3f7")
        self.preview_text.tag_config("meta", font=("Microsoft JhengHei UI", 9), foreground=text_secondary)
        self.preview_text.tag_config("content", font=("Microsoft JhengHei UI", 10), foreground=text_color, spacing1=5, spacing3=5)
        self.preview_text.tag_config("link", font=("Microsoft JhengHei UI", 9), foreground="#4fc3f7", underline=True)

        # 初始化顯示提示
        self.clear_preview()

    def show_preview(self, entry):
        """顯示文章完整內容

        Args:
            entry (dict): 文章資料
        """
        self.current_entry = entry

        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)

        # 標題
        self.preview_text.insert(tk.END, entry['title'] + "\n\n", "title")

        # 發布時間和連結
        meta_text = f"📅 發布時間: {entry['published']}\n🔗 連結: {entry['link']}\n\n"
        self.preview_text.insert(tk.END, meta_text, "meta")

        # 分隔線
        self.preview_text.insert(tk.END, "─" * 80 + "\n\n", "meta")

        # 完整內文
        content = entry.get('content', entry.get('summary', '無內容'))
        if content and content != '無內容':
            # 解碼 HTML 實體
            content = html.unescape(content)
            self.preview_text.insert(tk.END, content, "content")
        else:
            self.preview_text.insert(tk.END, "無法取得完整內容,請點擊「在瀏覽器開啟」查看", "meta")

        self.preview_text.config(state=tk.DISABLED)

    def clear_preview(self):
        """清空預覽"""
        self.current_entry = None

        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "請選擇文章以閱讀完整內容", "meta")
        self.preview_text.config(state=tk.DISABLED)

    def set_current_entry(self, entry):
        """設定當前文章

        Args:
            entry (dict): 文章資料
        """
        self.current_entry = entry

    def _open_in_browser(self):
        """在瀏覽器中開啟當前文章"""
        if not self.current_entry:
            messagebox.showwarning("提示", "請先選擇一篇文章")
            return

        link = self.current_entry.get('link', '')
        if link:
            try:
                webbrowser.open(link)
            except Exception as e:
                messagebox.showerror("錯誤", f"無法開啟連結: {e}")
                logger.error(f"無法開啟連結: {e}")
