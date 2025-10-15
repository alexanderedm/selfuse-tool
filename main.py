"""音訊切換工具主程式"""

"""測試"""
# This is a test on test-feature branch

import sys
import os
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from audio_manager import AudioManager
from config_manager import ConfigManager
from settings_window import SettingsWindow
from stats_window import StatsWindow
from rss_manager import RSSManager
from rss_window import RSSWindow
from clipboard_monitor import ClipboardMonitor
from music_manager import MusicManager
from music_window import MusicWindow
from changelog_window import ChangelogWindow
from logger import logger
import threading
from tkinter import messagebox
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class AudioSwitcherApp:
    """音訊切換工具應用程式"""

    def __init__(self):
        logger.info("初始化應用程式...")
        try:
            # 建立隱藏的 Tk 根視窗供所有子視窗使用
            self.tk_root = tk.Tk()
            self.tk_root.withdraw()

            self.audio_manager = AudioManager()
            self.config_manager = ConfigManager()
            self.icon = None
            self.settings_window = None
            self.stats_window = None
            self.rss_manager = RSSManager(self.config_manager)
            self.rss_window = None
            self.clipboard_monitor = ClipboardMonitor(
                on_rss_detected=self.on_url_detected
            )
            self.music_manager = MusicManager(self.config_manager)
            self.music_window = None
            self.changelog_window = None
            logger.info("應用程式初始化完成")
        except Exception as e:
            logger.exception("初始化應用程式時發生錯誤")

    def create_icon_image(self, color="blue"):
        """建立托盤圖示圖片

        Args:
            color (str): 圖示顏色 ('blue' 代表裝置A, 'green' 代表裝置B)

        Returns:
            PIL.Image: 圖示圖片
        """
        # 建立一個簡單的圓形圖示
        width = 64
        height = 64
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # 根據當前裝置繪製不同顏色
        fill_color = color
        draw.ellipse([8, 8, 56, 56], fill=fill_color, outline="black", width=2)

        # 繪製音訊圖示 (簡化的揚聲器)
        draw.polygon(
            [20, 28, 28, 28, 28, 20, 36, 20, 36, 44, 28, 44, 28, 36, 20, 36],
            fill="white",
        )
        draw.arc([38, 24, 46, 32], 270, 90, fill="white", width=2)
        draw.arc([38, 32, 46, 40], 0, 90, fill="white", width=2)

        return image

    def get_icon_color(self):
        """根據當前裝置取得圖示顏色

        Returns:
            str: 顏色名稱
        """
        current = self.audio_manager.get_default_device()
        if not current:
            return "gray"

        device_a = self.config_manager.get_device_a()
        device_b = self.config_manager.get_device_b()

        if device_a and current["id"] == device_a["id"]:
            return "blue"
        elif device_b and current["id"] == device_b["id"]:
            return "green"
        else:
            return "gray"

    def switch_device(self):
        """切換音訊裝置"""
        device_a = self.config_manager.get_device_a()
        device_b = self.config_manager.get_device_b()

        if not device_a or not device_b:
            self.show_notification("請先在設定中選擇兩個裝置", "錯誤")
            return

        current = self.audio_manager.get_default_device()
        if not current:
            self.show_notification("無法取得當前裝置", "錯誤")
            return

        # 決定要切換到哪個裝置
        target_device = None
        if current["id"] == device_a["id"]:
            target_device = device_b
        else:
            target_device = device_a

        # 執行切換
        success = self.audio_manager.set_default_device(target_device["id"])

        if success:
            self.config_manager.set_current_device(target_device)
            # 記錄使用統計
            self.config_manager.record_device_usage(target_device)
            self.show_notification(f"已切換到: {target_device['name']}", "音訊切換")
            # 更新圖示
            self.update_icon()
        else:
            self.show_notification("切換失敗", "錯誤")

    def show_notification(self, message, title="音訊切換工具"):
        """顯示系統通知

        Args:
            message (str): 通知訊息
            title (str): 通知標題
        """
        if self.icon:
            self.icon.notify(message, title)

    def update_icon(self):
        """更新托盤圖示"""
        if self.icon:
            color = self.get_icon_color()
            self.icon.icon = self.create_icon_image(color)
            # 更新 tooltip 顯示當前裝置
            current = self.audio_manager.get_default_device()
            if current:
                self.icon.title = f"音訊切換工具 - 當前: {current['name']}"
            else:
                self.icon.title = "音訊切換工具"

    def open_settings(self):
        """開啟設定視窗"""
        try:
            logger.log_window_event("設定視窗", "嘗試開啟")
            if self.settings_window is None or self.settings_window.window is None:
                self.settings_window = SettingsWindow(
                    self.audio_manager,
                    self.config_manager,
                    tk_root=self.tk_root,
                    on_save_callback=self.update_icon,
                )
                # 直接在主執行緒調用
                self.settings_window.show()
                logger.log_window_event("設定視窗", "已開啟")
            else:
                # 如果視窗已存在,將其帶到前景
                self.settings_window.window.lift()
                self.settings_window.window.focus_force()
                logger.log_window_event("設定視窗", "已帶到前景")
        except Exception as e:
            logger.exception("開啟設定視窗時發生錯誤")

    def open_stats(self):
        """開啟統計視窗"""
        # 在開啟統計視窗前先更新當前使用時間
        self.config_manager.update_current_usage()

        if self.stats_window is None or self.stats_window.window is None:
            self.stats_window = StatsWindow(self.config_manager, tk_root=self.tk_root)
            # 直接在主執行緒調用
            self.stats_window.show()
        else:
            # 如果視窗已存在,將其帶到前景
            self.stats_window.window.lift()
            self.stats_window.window.focus_force()

    def open_rss_viewer(self):
        """開啟 RSS 閱讀器"""
        try:
            logger.log_window_event("RSS視窗", "嘗試開啟")

            # 先檢查 self.rss_window 是否為 None,再檢查其 window 屬性
            window_status = None if self.rss_window is None else self.rss_window.window
            logger.debug(f"RSS視窗狀態: window={window_status}")

            if self.rss_window is None or self.rss_window.window is None:
                logger.info("建立新的 RSS 視窗實例")
                self.rss_window = RSSWindow(self.rss_manager, tk_root=self.tk_root)
                # 直接在主執行緒調用
                self.rss_window.show()
                logger.log_window_event("RSS視窗", "已開啟")
            else:
                # 如果視窗已存在,將其帶到前景
                logger.info("RSS 視窗已存在,嘗試帶到前景")
                try:
                    self.rss_window.window.lift()
                    self.rss_window.window.focus_force()
                    logger.log_window_event("RSS視窗", "已帶到前景")
                except Exception as e:
                    logger.error(f"無法將 RSS 視窗帶到前景: {e}")
                    # 視窗可能已關閉,重新建立
                    logger.info("重新建立 RSS 視窗")
                    self.rss_window = RSSWindow(self.rss_manager, tk_root=self.tk_root)
                    self.rss_window.show()
        except Exception as e:
            logger.exception("開啟 RSS 視窗時發生錯誤")

    def on_url_detected(self, url):
        """剪貼簿偵測到 URL 時的回調函數

        Args:
            url (str): 偵測到的 URL
        """
        # 檢查是否可能是 RSS URL
        if self.rss_manager.is_valid_rss_url(url):
            # 詢問使用者是否要訂閱
            self.ask_subscribe_rss(url)

    def ask_subscribe_rss(self, url):
        """詢問使用者是否要訂閱 RSS

        Args:
            url (str): RSS URL
        """

        def ask_in_thread():
            # 建立隱藏的 Tk 視窗以顯示對話框
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            answer = messagebox.askyesno(
                "偵測到 RSS 連結",
                f"偵測到可能的 RSS 連結:\n\n{url}\n\n是否要訂閱此 RSS?",
                parent=root,
            )

            if answer:
                result = self.rss_manager.add_feed(url)
                if result["success"]:
                    self.show_notification(result["message"], "RSS 訂閱")
                else:
                    messagebox.showerror("錯誤", result["message"], parent=root)

            root.destroy()

        # 在新執行緒中執行
        thread = threading.Thread(target=ask_in_thread, daemon=True)
        thread.start()

    def toggle_auto_start(self, icon, item):
        """切換開機自啟動"""
        current = self.config_manager.get_auto_start()
        self.config_manager.set_auto_start(not current)
        self.show_notification(
            f"開機自啟動已{'啟用' if not current else '停用'}", "設定"
        )

    def quit_app(self):
        """結束應用程式"""
        # 停止剪貼簿監控
        self.clipboard_monitor.stop()
        # 在結束前更新當前裝置的使用時間
        self.config_manager.update_current_usage()
        # 清理音樂播放器資源(包括 Discord Presence)
        if self.music_window:
            self.music_window.cleanup()
        # 停止 Tkinter 循環
        if self.tk_root:
            self.tk_root.quit()
        # 停止托盤圖示
        if self.icon:
            self.icon.stop()

    def open_log_viewer(self):
        """開啟 Log 檢視器"""
        import subprocess
        import os

        log_file = os.path.join(os.path.dirname(__file__), "logs", "app.log")

        if not os.path.exists(log_file):
            self.show_notification("Log 檔案不存在", "錯誤")
            return

        try:
            # 在 Windows 上用預設文字編輯器開啟
            os.startfile(log_file)
        except Exception as e:
            logger.error(f"無法開啟 Log 檔案: {e}")
            self.show_notification(f"無法開啟 Log: {e}", "錯誤")

    def open_changelog(self):
        """開啟更新日誌視窗"""
        try:
            logger.log_window_event("更新日誌視窗", "嘗試開啟")

            if self.changelog_window is None or self.changelog_window.window is None:
                logger.info("建立新的更新日誌視窗實例")
                self.changelog_window = ChangelogWindow(tk_root=self.tk_root)
                self.changelog_window.show()
                logger.log_window_event("更新日誌視窗", "已開啟")
            else:
                # 如果視窗已存在,將其帶到前景
                logger.info("更新日誌視窗已存在,嘗試帶到前景")
                try:
                    self.changelog_window.window.lift()
                    self.changelog_window.window.focus_force()
                    logger.log_window_event("更新日誌視窗", "已帶到前景")
                except Exception as e:
                    logger.error(f"無法將更新日誌視窗帶到前景: {e}")
                    # 視窗可能已關閉,重新建立
                    logger.info("重新建立更新日誌視窗")
                    self.changelog_window = ChangelogWindow(tk_root=self.tk_root)
                    self.changelog_window.show()
        except Exception as e:
            logger.exception("開啟更新日誌視窗時發生錯誤")

    def open_music_player(self):
        """開啟音樂播放器"""
        try:
            logger.log_window_event("音樂播放器", "嘗試開啟")

            if self.music_window is None:
                # 第一次打開,建立新實例
                logger.info("建立新的音樂播放器實例")
                self.music_window = MusicWindow(
                    self.music_manager, tk_root=self.tk_root
                )
                self.music_window.show()
                logger.log_window_event("音樂播放器", "已開啟")
            elif self.music_window.window is None:
                # 視窗已關閉但實例存在,重新顯示視窗(保留播放狀態)
                logger.info("重新顯示音樂播放器視窗(保留播放狀態)")
                self.music_window.show()
                logger.log_window_event("音樂播放器", "已重新開啟")
            else:
                # 視窗已存在,將其帶到前景
                logger.info("音樂播放器已存在,嘗試帶到前景")
                try:
                    self.music_window.window.lift()
                    self.music_window.window.focus_force()
                    logger.log_window_event("音樂播放器", "已帶到前景")
                except Exception as e:
                    logger.error(f"無法將音樂播放器帶到前景: {e}")
                    # 視窗可能已關閉,重新顯示
                    logger.info("重新顯示音樂播放器視窗")
                    self.music_window.show()
        except Exception as e:
            logger.exception("開啟音樂播放器時發生錯誤")

    def music_toggle_play_pause(self):
        """切換音樂播放/暫停"""
        if self.music_window is not None:
            try:
                self.music_window._toggle_play_pause()
                # 顯示通知
                if self.music_window.current_song:
                    status = "暫停" if self.music_window.is_paused else "播放中"
                    self.show_notification(
                        f"{status}: {self.music_window.current_song['title']}",
                        "音樂播放器",
                    )
                else:
                    self.show_notification("沒有正在播放的歌曲", "音樂播放器")
            except Exception as e:
                logger.error(f"切換播放/暫停時發生錯誤: {e}")
        else:
            self.show_notification("請先開啟音樂播放器", "音樂播放器")

    def music_play_next(self):
        """播放下一首歌"""
        if self.music_window is not None:
            try:
                self.music_window._play_next()
                if self.music_window.current_song:
                    self.show_notification(
                        f"播放: {self.music_window.current_song['title']}", "音樂播放器"
                    )
            except Exception as e:
                logger.error(f"播放下一首時發生錯誤: {e}")
        else:
            self.show_notification("請先開啟音樂播放器", "音樂播放器")

    def music_play_previous(self):
        """播放上一首歌"""
        if self.music_window is not None:
            try:
                self.music_window._play_previous()
                if self.music_window.current_song:
                    self.show_notification(
                        f"播放: {self.music_window.current_song['title']}", "音樂播放器"
                    )
            except Exception as e:
                logger.error(f"播放上一首時發生錯誤: {e}")
        else:
            self.show_notification("請先開啟音樂播放器", "音樂播放器")

    def music_stop(self):
        """停止音樂播放"""
        if self.music_window is not None:
            try:
                pygame.mixer.music.stop()
                self.music_window.is_playing = False
                self.music_window.is_paused = False
                self.show_notification("音樂已停止", "音樂播放器")
                logger.info("音樂已停止")
            except Exception as e:
                logger.error(f"停止音樂時發生錯誤: {e}")
        else:
            self.show_notification("沒有正在播放的音樂", "音樂播放器")

    def create_menu(self):
        """建立右鍵選單

        Returns:
            pystray.Menu: 選單物件
        """
        return pystray.Menu(
            item("切換輸出裝置", self.switch_device),
            item("設定", self.open_settings),
            item("使用統計", self.open_stats),
            pystray.Menu.SEPARATOR,
            item("RSS 訂閱管理", self.open_rss_viewer),
            item("本地音樂播放器", self.open_music_player),
            pystray.Menu.SEPARATOR,
            item(
                "🎵 音樂控制",
                pystray.Menu(
                    item("⏯ 播放/暫停", self.music_toggle_play_pause),
                    item("⏭ 下一首", self.music_play_next),
                    item("⏮ 上一首", self.music_play_previous),
                    item("⏹ 停止", self.music_stop),
                ),
            ),
            pystray.Menu.SEPARATOR,
            item("查看日誌", self.open_log_viewer),
            item("📝 更新日誌", self.open_changelog),
            item(
                "開機自動啟動",
                self.toggle_auto_start,
                checked=lambda item: self.config_manager.get_auto_start(),
            ),
            pystray.Menu.SEPARATOR,
            item("結束", self.quit_app),
        )

    def run(self):
        """執行應用程式"""
        # 啟動剪貼簿監控
        self.clipboard_monitor.start()

        # 建立托盤圖示
        icon_image = self.create_icon_image(self.get_icon_color())
        menu = self.create_menu()

        # 取得當前裝置名稱作為 tooltip
        current = self.audio_manager.get_default_device()
        if current:
            tooltip = f"音訊切換工具 - 當前: {current['name']}"
        else:
            tooltip = "音訊切換工具"

        self.icon = pystray.Icon("audio_switcher", icon_image, tooltip, menu)

        # 在背景執行緒中執行托盤圖示
        icon_thread = threading.Thread(target=self.icon.run, daemon=False)
        icon_thread.start()

        logger.info("托盤圖示已在背景執行緒啟動,開始 Tkinter 主循環")

        # 在主執行緒中執行 Tkinter 事件循環
        self.tk_root.mainloop()


def main():
    """主程式進入點"""
    app = AudioSwitcherApp()
    app.run()


if __name__ == "__main__":
    main()
