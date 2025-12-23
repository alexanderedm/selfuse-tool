
from src.plugins.plugin_base import Plugin
from src.windows.timer_window import TimerWindow
from pystray import MenuItem as item
from src.core.logger import logger

class TimerPlugin(Plugin):
    @property
    def name(self) -> str:
        return "countdown_timer"

    @property
    def description(self) -> str:
        return "Simple countdown timer with notifications."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def default_enabled(self) -> bool:
        return True

    def start(self) -> None:
        pass

    def on_load(self, context) -> None:
        super().on_load(context)
        self.app = context
        self.timer_window = None

    def on_unload(self) -> None:
        if self.timer_window:
            try:
                self.timer_window.window.destroy()
            except:
                pass
        super().on_unload()

    def get_menu_items(self) -> list:
        return [
            item("⏲️ 倒數計時", self.open_timer)
        ]

    def open_timer(self):
        try:
            if self.timer_window is None or self.timer_window.window is None:
                self.timer_window = TimerWindow(
                    tk_root=self.app.tk_root,
                    on_timer_complete=self.on_timer_complete
                )
                self.timer_window.show()
            else:
                self.timer_window.show()
        except Exception as e:
            logger.exception("Error opening timer window")

    def on_timer_complete(self, title):
        self.app.show_notification(f"時間到: {title}", "計時器提醒")
