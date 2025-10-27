"""藍牙裝置電量監控"""

import subprocess
import re
from src.core.logger import logger


class BluetoothBatteryMonitor:
    """藍牙裝置電池狀態監控器"""

    # Windows PnP Device Property ID for Battery Level
    BATTERY_PROPERTY_ID = "{104EA319-6EE2-4701-BD47-8DDBF425BBE5} 2"

    def __init__(self):
        """初始化藍牙電池監控器"""
        self.cached_devices = {}
        self.last_update = None

    def get_bluetooth_devices(self):
        """獲取所有藍牙和無線音訊裝置列表

        Returns:
            list: 裝置名稱列表
        """
        try:
            # 使用 PowerShell 獲取所有藍牙裝置和音訊裝置
            # 包括藍牙類別和音訊端點類別的裝置
            ps_script = """
            Get-PnpDevice | Where-Object {
                ($_.Class -eq 'Bluetooth' -or
                 $_.Class -eq 'AudioEndpoint' -or
                 $_.Class -eq 'MEDIA' -or
                 $_.FriendlyName -like '*headset*' -or
                 $_.FriendlyName -like '*headphone*' -or
                 $_.FriendlyName -like '*G535*') -and
                $_.Status -eq 'OK'
            } |
            Select-Object -ExpandProperty FriendlyName -Unique
            """

            cmd = ["powershell", "-Command", ps_script.strip()]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                shell=True
            )

            if result.returncode == 0 and result.stdout.strip():
                devices = [
                    line.strip()
                    for line in result.stdout.strip().split("\n")
                    if line.strip()
                ]
                logger.debug(f"找到 {len(devices)} 個音訊裝置")
                return devices
            else:
                logger.debug(f"無法獲取音訊裝置: {result.stderr}")
                return []

        except subprocess.TimeoutExpired:
            logger.error("獲取音訊裝置逾時")
            return []
        except Exception as e:
            logger.error(f"獲取音訊裝置時發生錯誤: {e}")
            return []

    def get_device_battery(self, device_name):
        """獲取指定藍牙裝置的電池狀態

        Args:
            device_name (str): 裝置名稱（從裝置管理員中看到的名稱）

        Returns:
            dict: {
                'device': 裝置名稱,
                'battery_level': 電池百分比 (0-100) 或 None,
                'status': 'ok' 或 'error',
                'message': 錯誤訊息（如果有）
            }
        """
        try:
            # 使用 PowerShell 獲取裝置電池狀態
            # 轉義裝置名稱中的單引號
            escaped_name = device_name.replace("'", "''")

            ps_script = f"""
            $device = Get-PnpDevice | Where-Object {{
                $_.FriendlyName -eq '{escaped_name}' -and
                $_.Status -eq 'OK'
            }}
            if ($device) {{
                $property = $device | Get-PnpDeviceProperty -KeyName '{self.BATTERY_PROPERTY_ID}' -ErrorAction SilentlyContinue
                if ($property) {{
                    $property.Data
                }}
            }}
            """

            cmd = ["powershell", "-Command", ps_script.strip()]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                shell=True
            )

            if result.returncode == 0 and result.stdout.strip():
                # 嘗試解析電池百分比
                battery_str = result.stdout.strip()

                # 處理可能的數字格式
                battery_match = re.search(r"\d+", battery_str)
                if battery_match:
                    battery_level = int(battery_match.group())
                    logger.debug(f"{device_name} 電池: {battery_level}%")
                    return {
                        "device": device_name,
                        "battery_level": battery_level,
                        "status": "ok",
                        "message": None,
                    }
                else:
                    return {
                        "device": device_name,
                        "battery_level": None,
                        "status": "error",
                        "message": "無法解析電池資訊",
                    }
            else:
                # 裝置可能不支援電池狀態查詢
                return {
                    "device": device_name,
                    "battery_level": None,
                    "status": "error",
                    "message": "裝置不支援電池查詢",
                }

        except subprocess.TimeoutExpired:
            logger.error(f"獲取 {device_name} 電池狀態逾時")
            return {
                "device": device_name,
                "battery_level": None,
                "status": "error",
                "message": "查詢逾時",
            }
        except Exception as e:
            logger.error(f"獲取 {device_name} 電池狀態時發生錯誤: {e}")
            return {
                "device": device_name,
                "battery_level": None,
                "status": "error",
                "message": str(e),
            }

    def get_all_batteries(self):
        """獲取所有藍牙裝置的電池狀態

        Returns:
            list: 裝置電池資訊列表
        """
        devices = self.get_bluetooth_devices()
        battery_info = []

        for device in devices:
            info = self.get_device_battery(device)
            if info["battery_level"] is not None:
                battery_info.append(info)

        return battery_info

    def get_headset_battery(self, keywords=None):
        """獲取耳機裝置的電池狀態

        Args:
            keywords (list): 搜尋關鍵字列表，用於識別耳機裝置
                           預設會搜尋常見的耳機關鍵字

        Returns:
            dict: 耳機電池資訊，如果找不到則返回 None
        """
        if keywords is None:
            # 常見的耳機關鍵字
            keywords = [
                "headset",
                "headphone",
                "earphone",
                "earbud",
                "耳機",
                "airpods",
                "g535",  # 羅技 G535
                "wireless",
                "gaming",
            ]

        devices = self.get_bluetooth_devices()
        logger.debug(f"找到 {len(devices)} 個藍牙裝置: {devices}")

        # 嘗試找到耳機裝置
        for device in devices:
            device_lower = device.lower()
            for keyword in keywords:
                if keyword.lower() in device_lower:
                    logger.info(f"找到可能的耳機裝置: {device}")
                    battery_info = self.get_device_battery(device)
                    if battery_info["battery_level"] is not None:
                        return battery_info

        logger.debug("未找到支援電池查詢的耳機裝置")
        return None

    def format_battery_display(self, battery_info):
        """格式化電池資訊顯示

        Args:
            battery_info (dict): 電池資訊

        Returns:
            str: 格式化後的顯示文字
        """
        if battery_info is None or battery_info["battery_level"] is None:
            return "耳機: 未連接或不支援"

        level = battery_info["battery_level"]
        device = battery_info["device"]

        # 簡化裝置名稱（移除多餘文字）
        short_name = device
        if len(short_name) > 20:
            short_name = short_name[:17] + "..."

        # 根據電量顯示不同的 emoji
        if level >= 80:
            emoji = "🔋"  # 充滿
        elif level >= 50:
            emoji = "🔋"  # 中等
        elif level >= 20:
            emoji = "🪫"  # 低電量
        else:
            emoji = "🪫"  # 極低電量

        return f"{emoji} {short_name}: {level}%"
