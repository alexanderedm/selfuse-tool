"""音樂歌詞視圖模組 - 負責歌詞顯示與同步"""
import customtkinter as ctk
from src.music.utils.lyrics_parser import LyricsParser
from src.core.logger import logger


class MusicLyricsView:
    """管理歌詞顯示區域的 UI 與互動"""

    def __init__(self, parent_frame, on_lyric_click=None):
        """初始化歌詞視圖

        Args:
            parent_frame: 父框架
            on_lyric_click: 點擊歌詞回調 (傳遞時間參數)
        """
        self.parent_frame = parent_frame
        self.on_lyric_click = on_lyric_click

        # 歌詞數據
        self.current_lyrics = []  # [{'time': float, 'text': str}, ...]
        self.current_index = -1  # 當前高亮的歌詞索引

        # UI 元件
        self.lyrics_container = None
        self.lyrics_text = None
        self.scrollbar = None

        # 狀態
        self.auto_scroll = True  # 是否自動滾動
        self.is_visible_flag = True  # 是否可見

        # 顏色主題
        self.bg_color = "#1e1e1e"
        self.text_color = "#e0e0e0"
        self.highlight_color = "#0078d4"
        self.highlight_bg = "#2d4a5e"

    def create_view(self):
        """建立歌詞顯示視圖"""
        # 歌詞容器（圓角框架）
        self.lyrics_container = ctk.CTkFrame(
            self.parent_frame,
            corner_radius=15,
            fg_color=self.bg_color
        )
        self.lyrics_container.pack(side="top", fill="both", expand=True)

        # 標題
        header = ctk.CTkLabel(
            self.lyrics_container,
            text="🎤 歌詞",
            font=("Microsoft JhengHei UI", 14, "bold"),
            fg_color="#0d47a1",
            text_color="white",
            corner_radius=12,
            height=40
        )
        header.pack(fill="x", padx=5, pady=(5, 0))

        # 歌詞文字框（使用 CTkTextbox）
        self.lyrics_text = ctk.CTkTextbox(
            self.lyrics_container,
            wrap="word",
            fg_color=self.bg_color,
            text_color=self.text_color,
            font=("Microsoft JhengHei UI", 11),
            corner_radius=10,
            border_width=0
        )
        self.lyrics_text.pack(fill="both", expand=True, padx=10, pady=10)

        # 禁用編輯
        self.lyrics_text.configure(state="disabled")

        # 綁定點擊事件
        self.lyrics_text.bind('<Button-1>', self._on_text_click)

        # 綁定滾動事件 (用於偵測手動滾動)
        self.lyrics_text.bind('<MouseWheel>', self._on_manual_scroll)

    def set_lyrics(self, lyrics):
        """設定歌詞

        Args:
            lyrics (list): 歌詞列表 [{'time': float, 'text': str}, ...]
        """
        self.current_lyrics = lyrics
        self.current_index = -1

        if not self.lyrics_text:
            return

        # 清除現有內容
        self.lyrics_text.configure(state="normal")
        self.lyrics_text.delete("1.0", "end")

        if not lyrics:
            self.show_no_lyrics_message()
        else:
            # 插入歌詞（CTkTextbox 不支援 tag，需手動處理）
            for i, lyric in enumerate(lyrics):
                line_text = f"{lyric['text']}\n\n"
                self.lyrics_text.insert("end", line_text)

        self.lyrics_text.configure(state="disabled")

    def show_no_lyrics_message(self):
        """顯示無歌詞訊息"""
        if not self.lyrics_text:
            return

        self.lyrics_text.configure(state="normal")
        self.lyrics_text.delete("1.0", "end")
        self.lyrics_text.insert(
            "end",
            "\n\n\n暫無歌詞\n\n請將 .lrc 歌詞文件放在與音樂文件相同的目錄"
        )
        self.lyrics_text.configure(state="disabled")

    def update_current_time(self, current_time):
        """更新當前播放時間,高亮對應歌詞

        Args:
            current_time (float): 當前播放時間(秒)
        """
        if not self.current_lyrics or not self.lyrics_text:
            return

        # 找出當前時間對應的歌詞索引
        new_index = -1
        for i, lyric in enumerate(self.current_lyrics):
            if lyric['time'] <= current_time:
                new_index = i
            else:
                break

        # 如果索引改變,更新高亮
        if new_index != self.current_index:
            self.current_index = new_index
            self._highlight_lyric(new_index)

            # 自動滾動到當前歌詞
            if self.auto_scroll and new_index >= 0:
                self.scroll_to_line(new_index)

    def _highlight_lyric(self, index):
        """高亮指定索引的歌詞

        Args:
            index (int): 歌詞索引
        """
        if not self.lyrics_text:
            return

        # CTkTextbox 不支援 tag，暫時跳過高亮功能
        # 可在未來版本使用自定義渲染或其他方式實現
        pass

    def scroll_to_line(self, line_index):
        """滾動到指定歌詞行

        Args:
            line_index (int): 歌詞索引
        """
        if not self.lyrics_text:
            return

        try:
            # 計算實際行號
            line_num = line_index * 2 + 1

            # 滾動到該行
            # 使用 see() 方法確保該行可見
            self.lyrics_text.see(f"{line_num}.0")

            # 將該行置於視窗中央
            total_lines = int(self.lyrics_text.index('end-1c').split('.')[0])
            visible_lines = int(self.lyrics_text.winfo_height()
                                / self.lyrics_text.winfo_reqheight() * 10)

            if visible_lines > 0:
                offset = max(0, line_num - visible_lines // 2)
                self.lyrics_text.yview(f"{offset}.0")

        except Exception as e:
            logger.error(f"滾動歌詞失敗: {e}")

    def clear(self):
        """清除歌詞"""
        self.current_lyrics = []
        self.current_index = -1

        if self.lyrics_text:
            self.lyrics_text.configure(state="normal")
            self.lyrics_text.delete("1.0", "end")
            self.lyrics_text.configure(state="disabled")

    def toggle_visibility(self):
        """切換顯示/隱藏"""
        if self.is_visible_flag:
            self.set_visible(False)
        else:
            self.set_visible(True)

    def set_visible(self, visible):
        """設定可見性

        Args:
            visible (bool): 是否可見
        """
        self.is_visible_flag = visible

        if self.lyrics_container:
            if visible:
                self.lyrics_container.pack(
                    side=tk.TOP,
                    fill=tk.BOTH,
                    expand=True
                )
            else:
                self.lyrics_container.pack_forget()

    def is_visible(self):
        """檢查是否可見

        Returns:
            bool: 是否可見
        """
        return self.is_visible_flag

    def set_auto_scroll(self, enabled):
        """設定自動滾動

        Args:
            enabled (bool): 是否啟用自動滾動
        """
        self.auto_scroll = enabled

    def is_auto_scroll_enabled(self):
        """檢查自動滾動是否啟用

        Returns:
            bool: 是否啟用自動滾動
        """
        return self.auto_scroll

    def get_lyric_lines_count(self):
        """獲取歌詞行數

        Returns:
            int: 歌詞行數
        """
        return len(self.current_lyrics)

    def _on_text_click(self, event):
        """文字框點擊事件

        Args:
            event: 點擊事件
        """
        if not self.lyrics_text or not self.current_lyrics:
            return

        try:
            # 獲取點擊位置的行號
            index = self.lyrics_text.index(f"@{event.x},{event.y}")
            line_num = int(index.split('.')[0])

            # 計算歌詞索引 (每句歌詞佔 2 行)
            lyric_index = (line_num - 1) // 2

            if 0 <= lyric_index < len(self.current_lyrics):
                self._on_lyric_line_click(lyric_index)

        except Exception as e:
            logger.error(f"處理歌詞點擊失敗: {e}")

    def _on_lyric_line_click(self, line_index):
        """歌詞行點擊回調

        Args:
            line_index (int): 歌詞索引
        """
        if self.on_lyric_click and 0 <= line_index < len(self.current_lyrics):
            time = self.current_lyrics[line_index]['time']
            self.on_lyric_click(time)

    def _on_manual_scroll(self, event):
        """手動滾動事件

        Args:
            event: 滾動事件
        """
        # 當用戶手動滾動時,暫時停用自動滾動
        # (可選功能,視需求決定)
        pass
