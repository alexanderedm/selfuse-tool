from src.plugins.plugin_base import Plugin
from src.rss.rss_manager import RSSManager
from src.rss.rss_window import RSSWindow
from src.utils.clipboard_monitor import ClipboardMonitor
from src.core.logger import logger
from pystray import MenuItem as item
import tkinter as tk
from tkinter import messagebox
import threading

class RSSPlugin(Plugin):
    @property
    def name(self) -> str:
        return "rss_reader"

    @property
    def description(self) -> str:
        return "RSS Feed Reader with clipboard detection."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def default_enabled(self) -> bool:
        return True

    def start(self) -> None:
        if self.clipboard_monitor:
            self.clipboard_monitor.start()

    def on_load(self, context) -> None:
        super().on_load(context)
        self.app = context
        try:
            self.rss_manager = RSSManager(self.app.config_manager)
            self.rss_window = None
            self.clipboard_monitor = ClipboardMonitor(on_rss_detected=self.on_url_detected)
            logger.info("RSSPlugin loaded.")
        except Exception as e:
            logger.error(f"Failed to initialize RSSPlugin: {e}")

    def on_unload(self) -> None:
        if self.clipboard_monitor:
            self.clipboard_monitor.stop()
        if self.rss_window:
            try:
                self.rss_window.window.destroy()
            except:
                pass
        super().on_unload()

    def get_menu_items(self) -> list:
        return [
            item("📰 RSS 訂閱管理", self.open_rss_viewer)
        ]

    def open_rss_viewer(self):
        try:
            if self.rss_window is None or self.rss_window.window is None:
                self.rss_window = RSSWindow(self.rss_manager, tk_root=self.app.tk_root)
                self.rss_window.show()
            else:
                try:
                    self.rss_window.window.lift()
                    self.rss_window.window.focus_force()
                except:
                    self.rss_window.show()
        except Exception as e:
            logger.exception("Error opening RSS window")

    def on_url_detected(self, url):
        # 檢查是否可能是 RSS URL
        if self.rss_manager.is_valid_rss_url(url):
            self.ask_subscribe_rss(url)

    def ask_subscribe_rss(self, url):
        def ask_in_thread():
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            answer = messagebox.askyesno(
                "偵測到 RSS 連結",
                f"偵測到可能的 RSS 連結:\n\n{url}\n\n是否要訂閱此 RSS?",
                parent=root
            )
            if answer:
                result = self.rss_manager.add_feed(url)
                if result["success"]:
                    self.app.show_notification(result["message"], "RSS 訂閱")
                else:
                    messagebox.showerror("錯誤", result["message"], parent=root)
            root.destroy()

        thread = threading.Thread(target=ask_in_thread, daemon=True)
        thread.start()
