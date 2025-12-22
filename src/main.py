"""音訊切換工具主程式"""

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
from src.core.audio_manager import AudioManager
from src.core.config_manager import ConfigManager
from src.windows.settings_window import SettingsWindow
from src.windows.stats_window import StatsWindow
from src.windows.changelog_window import ChangelogWindow
from src.core.logger import logger
from src.plugins.plugin_manager import PluginManager
import threading
from tkinter import messagebox
import tkinter as tk

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
            self.changelog_window = None

            # 初始化插件管理器
            self.plugin_manager = PluginManager(self.config_manager, self)
            self.plugin_manager.discover_plugins()
            self.plugin_manager.load_enabled_plugins()

            logger.info("應用程式初始化完成")
        except Exception as e:
            logger.exception("初始化應用程式時發生錯誤")

    def create_icon_image(self, color="blue"):
        """建立托盤圖示圖片"""
        width = 64
        height = 64
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # 根據當前裝置繪製不同顏色
        fill_color = color
        draw.ellipse([8, 8, 56, 56], fill=fill_color, outline="black", width=2)

        # 繪製音訊圖示
        draw.polygon(
            [20, 28, 28, 28, 28, 20, 36, 20, 36, 44, 28, 44, 28, 36, 20, 36],
            fill="white",
        )
        draw.arc([38, 24, 46, 32], 270, 90, fill="white", width=2)
        draw.arc([38, 32, 46, 40], 0, 90, fill="white", width=2)

        return image

    def get_icon_color(self):
        """根據當前裝置取得圖示顏色"""
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
            # 更新選單（雖然裝置切換可能不影響菜單，但有些插件可能需要刷新狀態）
            self.update_menu()
        else:
            self.show_notification("切換失敗", "錯誤")

    def show_notification(self, message, title="音訊切換工具"):
        """顯示系統通知"""
        if self.icon:
            self.icon.notify(message, title)

    def update_icon(self):
        """更新托盤圖示"""
        if self.icon:
            color = self.get_icon_color()
            self.icon.icon = self.create_icon_image(color)
            current = self.audio_manager.get_default_device()
            if current:
                self.icon.title = f"音訊切換工具 - 當前: {current['name']}"
            else:
                self.icon.title = "音訊切換工具"

    def update_menu(self):
        """更新托盤選單"""
        if self.icon:
            self.icon.menu = self.create_menu()

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
        
        # 核心選單項目
        menu_items = [
            item("切換輸出裝置", self.switch_device),
            item("設定", self.open_settings),
            item("使用統計", self.open_stats),
            pystray.Menu.SEPARATOR
        ]

        # 插件選單項目
        plugin_items = []
        # 按順序添加，這裡簡單遍歷
        # 可以定義優先級，但暫時依賴字典順序或載入順序
        # 為了更好的體驗，可以指定一些順序 (e.g. Battery -> AI -> RSS -> Music)
        # 或者在 PluginManager 提供 sorted_plugins
        
        # 我們希望 Battery 在上方
        priority_order = ["battery_monitor", "ai_web_assistant", "rss_reader", "music_player"]
        
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

        # 系統項目
        menu_items.extend([
            item("查看日誌", self.open_log_viewer),
            item("📝 更新日誌", self.open_changelog),
            pystray.Menu.SEPARATOR,
            item("🔄 重新啟動", self.restart_app),
            item("結束", self.quit_app)
        ])

        return pystray.Menu(*menu_items)

    def run(self):
        """執行應用程式"""
        
        icon_image = self.create_icon_image(self.get_icon_color())
        menu = self.create_menu()

        current = self.audio_manager.get_default_device()
        tooltip = f"音訊切換工具 - 當前: {current['name']}" if current else "音訊切換工具"

        self.icon = pystray.Icon("audio_switcher", icon_image, tooltip, menu)

        icon_thread = threading.Thread(target=self.icon.run, daemon=False)
        icon_thread.start()

        logger.info("托盤圖示已在背景執行緒啟動,開始 Tkinter 主循環")
        self.tk_root.mainloop()

def main():
    """主程式進入點"""
    app = AudioSwitcherApp()
    app.run()

if __name__ == "__main__":
    main()
