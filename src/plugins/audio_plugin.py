
from src.plugins.plugin_base import Plugin
from src.core.audio_manager import AudioManager
from src.core.logger import logger
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import threading

class AudioPlugin(Plugin):
    @property
    def name(self) -> str:
        return "audio_switcher"

    @property
    def description(self) -> str:
        return "Core audio device switching functionality."

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def default_enabled(self) -> bool:
        return True

    def start(self) -> None:
        pass

    def on_load(self, context) -> None:
        super().on_load(context)
        self.app = context
        try:
            self.audio_manager = AudioManager()
            # Invalidate/Reload Settings Window if open, to show Audio controls
            if hasattr(self.app, 'settings_window') and self.app.settings_window:
                 # We can't easily dynamic reload complex UI without destroy/recreate
                 # But we can inject the manager so next open works
                 self.app.settings_window.audio_manager = self.audio_manager
            
            # Hook into app icon update if possible (Toolbox app needs to support this delegation)
            # For now, we will manually update icon logic in get_menu_items or similar
            self.update_app_icon()
            
        except Exception as e:
            logger.error(f"Failed to initialize AudioPlugin: {e}")

    def on_unload(self) -> None:
        self.audio_manager = None
        if hasattr(self.app, 'settings_window') and self.app.settings_window:
            self.app.settings_window.audio_manager = None
        
        # Reset app icon to default
        if hasattr(self.app, 'reset_icon'):
            self.app.reset_icon()
        super().on_unload()

    def get_menu_items(self) -> list:
        return [
            item("🎧 切換輸出裝置", self.switch_device)
        ]

    def update_app_icon(self):
        """Update the main app icon based on audio state."""
        if not hasattr(self.app, 'icon') or not self.app.icon:
            return
            
        color = self.get_icon_color()
        image = self.create_icon_image(color)
        self.app.icon.icon = image
        
        current = self.audio_manager.get_default_device()
        if current:
            self.app.icon.title = f"工具箱 - 音訊: {current['name']}"

    def create_icon_image(self, color="blue"):
        width = 64
        height = 64
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        fill_color = color
        draw.ellipse([8, 8, 56, 56], fill=fill_color, outline="black", width=2)
        # Audio icon
        draw.polygon(
            [20, 28, 28, 28, 28, 20, 36, 20, 36, 44, 28, 44, 28, 36, 20, 36],
            fill="white",
        )
        draw.arc([38, 24, 46, 32], 270, 90, fill="white", width=2)
        draw.arc([38, 32, 46, 40], 0, 90, fill="white", width=2)
        return image

    def get_icon_color(self):
        current = self.audio_manager.get_default_device()
        if not current:
            return "gray"

        device_a = self.app.config_manager.get_device_a()
        device_b = self.app.config_manager.get_device_b()
        
        # Determine color
        if device_a and current["id"] == device_a["id"]:
            return "blue"
        elif device_b and current["id"] == device_b["id"]:
            return "green"
        else:
            return "gray"

    def switch_device(self):
        device_a = self.app.config_manager.get_device_a()
        device_b = self.app.config_manager.get_device_b()

        if not device_a or not device_b:
            self.app.show_notification("請先在設定中選擇兩個裝置", "錯誤")
            return

        current = self.audio_manager.get_default_device()
        if not current:
            return

        target_device = None
        if current["id"] == device_a["id"]:
            target_device = device_b
        else:
            target_device = device_a

        success = self.audio_manager.set_default_device(target_device["id"])

        if success:
            self.app.config_manager.set_current_device(target_device)
            self.app.config_manager.record_device_usage(target_device)
            self.app.show_notification(f"已切換到: {target_device['name']}", "音訊切換")
            self.update_app_icon()
        else:
            self.app.show_notification("切換失敗", "錯誤")
