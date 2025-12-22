from src.plugins.plugin_base import Plugin
from src.battery.bluetooth_battery import BluetoothBatteryMonitor
from src.battery.logitech_battery import LogitechBatteryMonitor
from src.core.logger import logger
from pystray import MenuItem as item

class BatteryPlugin(Plugin):
    @property
    def name(self) -> str:
        return "battery_monitor"

    @property
    def description(self) -> str:
        return "Bluetooth and Logitech headset battery monitoring."

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
        self.battery_monitor = None
        self.logitech_battery_monitor = None
        
        try:
            self.battery_monitor = BluetoothBatteryMonitor()
            logger.info("BatteryPlugin: Bluetooth monitor initialized.")
        except Exception as e:
            logger.warning(f"BatteryPlugin: Bluetooth init failed: {e}")

        try:
            self.logitech_battery_monitor = LogitechBatteryMonitor()
            logger.info("BatteryPlugin: Logitech monitor initialized.")
        except Exception as e:
            logger.warning(f"BatteryPlugin: Logitech init failed: {e}")

    def on_unload(self) -> None:
        self.battery_monitor = None
        self.logitech_battery_monitor = None
        super().on_unload()

    def get_menu_items(self) -> list:
        text = self.get_headset_battery_text()
        return [
            item(text, None, enabled=False)
        ]

    def get_headset_battery_text(self):
        try:
            # Logitech
            if self.logitech_battery_monitor:
                if self.logitech_battery_monitor.is_lgstraybattery_running():
                    info = self.logitech_battery_monitor.get_headset_battery()
                    if info:
                        return self.logitech_battery_monitor.format_battery_display(info)
            
            # Bluetooth
            if self.battery_monitor:
                info = self.battery_monitor.get_headset_battery()
                if info:
                    return self.battery_monitor.format_battery_display(info)

            return "🎧 耳機: 不支援或未連接"
        except Exception as e:
            logger.error(f"Battery check error: {e}")
            return "🎧 耳機: 查詢失敗"
