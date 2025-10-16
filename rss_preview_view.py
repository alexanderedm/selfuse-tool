"""RSS Preview View 模組 - 預覽視圖"""
import customtkinter as ctk
from tkinter import messagebox
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

        # 右側容器（圓角框架）
        right_container = ctk.CTkFrame(
            self.parent,
            corner_radius=15,
            fg_color=card_bg
        )
        right_container.pack(side="left", fill="both", expand=True)

        # 標題框架
        preview_header_frame = ctk.CTkFrame(right_container, fg_color=header_bg, corner_radius=(12, 12, 0, 0))
        preview_header_frame.pack(fill="x")

        preview_header = ctk.CTkLabel(
            preview_header_frame,
            text="📖 完整內文",
            font=("Microsoft JhengHei UI", 12, "bold"),
            text_color="white",
            height=40
        )
        preview_header.pack(side="left", padx=10)

        # 在瀏覽器開啟按鈕
        self.open_browser_button = ctk.CTkButton(
            preview_header_frame,
            text="🌐 在瀏覽器開啟",
            command=self._open_in_browser,
            corner_radius=10,
            width=150,
            height=35,
            font=("Microsoft JhengHei UI", 10)
        )
        self.open_browser_button.pack(side="right", padx=10, pady=5)

        # 內文預覽文字框（使用 CTkTextbox）
        self.preview_text = ctk.CTkTextbox(
            right_container,
            wrap="word",
            font=("Microsoft JhengHei UI", 10),
            corner_radius=10,
            fg_color="#252525",
            text_color=text_color
        )
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=10)

        # 初始化顯示提示
        self.clear_preview()

    def show_preview(self, entry):
        """顯示文章完整內容

        Args:
            entry (dict): 文章資料
        """
        self.current_entry = entry

        self.preview_text.configure(state="normal")
        self.preview_text.delete("0.0", "end")

        # 標題
        self.preview_text.insert("end", f"{entry['title']}\n\n")

        # 發布時間和連結
        meta_text = f"📅 發布時間: {entry['published']}\n🔗 連結: {entry['link']}\n\n"
        self.preview_text.insert("end", meta_text)

        # 分隔線
        self.preview_text.insert("end", "─" * 80 + "\n\n")

        # 完整內文
        content = entry.get('content', entry.get('summary', '無內容'))
        if content and content != '無內容':
            # 解碼 HTML 實體
            content = html.unescape(content)
            self.preview_text.insert("end", content)
        else:
            self.preview_text.insert("end", "無法取得完整內容,請點擊「在瀏覽器開啟」查看")

        self.preview_text.configure(state="disabled")

    def clear_preview(self):
        """清空預覽"""
        self.current_entry = None

        self.preview_text.configure(state="normal")
        self.preview_text.delete("0.0", "end")
        self.preview_text.insert("end", "請選擇文章以閱讀完整內容")
        self.preview_text.configure(state="disabled")

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
