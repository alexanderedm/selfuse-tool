"""系統工具箱主程式"""

import sys
import os

# 確保可以找到 src 模組（支援從任意位置執行）
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from src.core.config_manager import ConfigManager
from src.windows.settings_window import SettingsWindow
from src.windows.stats_window import StatsWindow
from src.windows.changelog_window import ChangelogWindow
from src.core.logger import logger
from src.plugins.plugin_manager import PluginManager
import threading
from tkinter import messagebox
import tkinter as tk

class ToolboxApp:
    """系統工具箱應用程式"""

    def __init__(self):
        logger.info("初始化工具箱應用程式...")
        try:
            # 建立隱藏的 Tk 根視窗供所有子視窗使用
            self.tk_root = tk.Tk()
            self.tk_root.withdraw()

            # Remove direct AudioManager dependency
            # self.audio_manager = AudioManager() 
            self.config_manager = ConfigManager()
            self.icon = None
            self.settings_window = None
            self.stats_window = None
            self.changelog_window = None

            # 初始化插件管理器
            self.plugin_manager = PluginManager(self.config_manager, self)
            self.plugin_manager.discover_plugins()
            self.plugin_manager.load_enabled_plugins()

            logger.info("應用程式初始化完成")
        except Exception as e:
            logger.exception("初始化應用程式時發生錯誤")

    def create_default_icon(self):
        """建立預設工具箱圖示"""
        width = 64
        height = 64
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # 繪製一個簡單的工具箱樣式圖示 (灰色圓形 + 矩形)
        draw.ellipse([8, 8, 56, 56], fill="#404040", outline="black", width=2)
        # Toolbox handle
        draw.rectangle([26, 16, 38, 22], fill="white")
        # Toolbox body
        draw.rectangle([18, 22, 46, 44], fill="#606060", outline="white")

        return image

    def reset_icon(self):
        """重置為預設圖示"""
        if self.icon:
            self.icon.icon = self.create_default_icon()
            self.icon.title = "系統工具箱"

    def show_notification(self, message, title="系統工具箱"):
        """顯示系統通知"""
        if self.icon:
            self.icon.notify(message, title)

    def update_menu(self):
        """更新托盤選單"""
        if self.icon:
            self.icon.menu = self.create_menu()

    def open_settings(self):
        """開啟設定視窗"""
        try:
            logger.log_window_event("設定視窗", "嘗試開啟")
            if self.settings_window is None or self.settings_window.window is None:
                # 判斷是否需要傳入 audio_manager (如果 AudioPlugin 存在)
                audio_mgr = None
                audio_plugin = self.plugin_manager.get_plugin("audio_switcher")
                if audio_plugin and hasattr(audio_plugin, 'audio_manager'):
                    audio_mgr = audio_plugin.audio_manager

                self.settings_window = SettingsWindow(
                    self.config_manager,
                    audio_manager=audio_mgr,
                    tk_root=self.tk_root,
                    # Callback update icon? Maybe generic update
                    on_save_callback=lambda: self.plugin_manager.get_plugin("audio_switcher").update_app_icon() if self.plugin_manager.get_plugin("audio_switcher") else None,
                    plugin_manager=self.plugin_manager
                )
                self.settings_window.show()
                logger.log_window_event("設定視窗", "已開啟")
            else:
                self.settings_window.window.lift()
                self.settings_window.window.focus_force()
                logger.log_window_event("設定視窗", "已帶到前景")
        except Exception as e:
            logger.exception("開啟設定視窗時發生錯誤")

    def open_stats(self):
        """開啟統計視窗"""
        self.config_manager.update_current_usage()
        if self.stats_window is None or self.stats_window.window is None:
            self.stats_window = StatsWindow(self.config_manager, tk_root=self.tk_root)
            self.stats_window.show()
        else:
            self.stats_window.window.lift()
            self.stats_window.window.focus_force()

    def open_log_viewer(self):
        """開啟 Log 檢視器"""
        import os
        log_file = os.path.join(os.path.dirname(__file__), "logs", "app.log")
        if not os.path.exists(log_file):
            self.show_notification("Log 檔案不存在", "錯誤")
            return
        try:
            os.startfile(log_file)
        except Exception as e:
            logger.error(f"無法開啟 Log 檔案: {e}")
            self.show_notification(f"無法開啟 Log: {e}", "錯誤")

    def open_changelog(self):
        """開啟更新日誌視窗"""
        try:
            if self.changelog_window is None or self.changelog_window.window is None:
                self.changelog_window = ChangelogWindow(tk_root=self.tk_root)
                self.changelog_window.show()
            else:
                try:
                    self.changelog_window.window.lift()
                    self.changelog_window.window.focus_force()
                except Exception as e:
                    self.changelog_window = ChangelogWindow(tk_root=self.tk_root)
                    self.changelog_window.show()
        except Exception as e:
            logger.exception("開啟更新日誌視窗時發生錯誤")

    def restart_app(self):
        """重新啟動應用程式"""
        import subprocess
        logger.info("準備重新啟動應用程式...")
        try:
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                python_dir = os.path.dirname(sys.executable)
                pythonw_exe = os.path.join(python_dir, 'pythonw.exe')
                if not os.path.exists(pythonw_exe):
                    pythonw_exe = sys.executable
                current_exe = pythonw_exe
                script_path = os.path.abspath(__file__)

            self.config_manager.update_current_usage()
            self.config_manager.save_config()

            if getattr(sys, 'frozen', False):
                subprocess.Popen(
                    [current_exe],
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
                    close_fds=True
                )
            else:
                subprocess.Popen(
                    [current_exe, script_path],
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
                    close_fds=True
                )

            logger.info("新實例已啟動，準備關閉當前實例")
            self.show_notification("應用程式正在重新啟動...", "系統")
            import time
            time.sleep(0.5)
            self.quit_app()

        except Exception as e:
            logger.error(f"重新啟動失敗: {e}", exc_info=True)
            self.show_notification(f"重新啟動失敗: {e}", "錯誤")

    def quit_app(self):
        """結束應用程式"""
        # 卸載所有插件（觸發清理）
        for name in list(self.plugin_manager.plugins.keys()):
            self.plugin_manager.unload_plugin(name)
            
        self.config_manager.update_current_usage()
        
        if self.tk_root:
            self.tk_root.quit()
        if self.icon:
            self.icon.stop()

    def create_menu(self):
        """建立右鍵選單"""
        
        menu_items = []

        # 1. 插件項目
        plugin_items = []
        
        # 優先級: 倒數計時 -> 音訊切換 -> Battery -> AI -> RSS -> Music
        priority_order = ["countdown_timer", "audio_switcher", "battery_monitor", "ai_web_assistant", "rss_reader", "music_player"]
        
        # 先加入有優先級的
        for name in priority_order:
            plugin = self.plugin_manager.get_plugin(name)
            if plugin and getattr(plugin, "_enabled", False):
                 items = plugin.get_menu_items()
                 if items:
                     plugin_items.extend(items)
                     plugin_items.append(pystray.Menu.SEPARATOR)

        # 再加入其他未列出的
        for name, plugin in self.plugin_manager.plugins.items():
            if name not in priority_order and getattr(plugin, "_enabled", False):
                 items = plugin.get_menu_items()
                 if items:
                     plugin_items.extend(items)
                     plugin_items.append(pystray.Menu.SEPARATOR)

        menu_items.extend(plugin_items)

        # 2. 核心選單項目 (Settings always available)
        menu_items.extend([
            item("設定", self.open_settings),
            item("使用統計", self.open_stats),
            pystray.Menu.SEPARATOR,
            item("查看日誌", self.open_log_viewer),
            item("📝 更新日誌", self.open_changelog),
            pystray.Menu.SEPARATOR,
            item("🔄 重新啟動", self.restart_app),
            item("結束", self.quit_app)
        ])

        return pystray.Menu(*menu_items)

    def run(self):
        """執行應用程式"""
        
        # 初始圖示 (會被插件覆蓋，如果有載入的話)
        image = self.create_default_icon()
        tooltip = "系統工具箱"

        self.icon = pystray.Icon("toolbox", image, tooltip, self.create_menu())

        # 如果 Audio Plugin 已經載入，嘗試更新圖示
        audio_plugin = self.plugin_manager.get_plugin("audio_switcher")
        if audio_plugin and getattr(audio_plugin, "_enabled", False):
            audio_plugin.update_app_icon()

        icon_thread = threading.Thread(target=self.icon.run, daemon=False)
        icon_thread.start()

        logger.info("托盤圖示已在背景執行緒啟動,開始 Tkinter 主循環")
        self.tk_root.mainloop()

def main():
    """主程式進入點"""
    app = ToolboxApp()
    app.run()

if __name__ == "__main__":
    main()
