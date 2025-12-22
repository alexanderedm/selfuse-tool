"""羅技裝置電池監控（透過 LGSTray HTTP API）"""

import requests
import xml.etree.ElementTree as ET
import re
from src.core.logger import logger


class LogitechBatteryMonitor:
    """羅技裝置電池監控器（使用 LGSTray API）"""

    BASE_URL = "http://localhost:12321"

    def __init__(self):
        """初始化羅技電池監控器"""
        self.last_update = None
        self.cached_devices = []

    def is_lgstraybattery_running(self):
        """檢查 LGSTray 是否正在執行

        Returns:
            bool: True 如果執行中，False 否則
        """
        try:
            response = requests.get(self.BASE_URL, timeout=2)
            return response.status_code == 200 and "LGSTray" in response.text
        except requests.exceptions.RequestException:
            return False

    def _parse_device_list_html(self, html):
        """解析裝置列表 HTML

        Args:
            html (str): HTML 內容

        Returns:
            list: 裝置名稱列表
        """
        devices = []
        # 使用正則表達式提取裝置名稱
        # 格式: <a href="/device/DEVICE_NAME">DEVICE_NAME</a>
        pattern = r'<a href="/device/([^"]+)">[^<]+</a>'
        matches = re.findall(pattern, html)

        for match in matches:
            # URL decode
            device_name = match.replace('%20', ' ').replace('%2F', '/')
            if device_name not in devices and not device_name.startswith('dev'):
                devices.append(device_name)

        return devices

    def get_devices(self):
        """獲取所有羅技裝置的電池資訊

        Returns:
            list: 裝置資訊列表，每個項目包含 {
                'name': 裝置名稱,
                'battery_percentage': 電池百分比,
                'is_charging': 是否充電中,
                'device_type': 裝置類型
            }
        """
        try:
            # 先獲取裝置列表
            response = requests.get(self.BASE_URL, timeout=5)

            if response.status_code != 200:
                logger.error(f"LGSTray API 回應錯誤: {response.status_code}")
                return []

            device_names = self._parse_device_list_html(response.text)
            logger.debug(f"找到 {len(device_names)} 個裝置")

            devices = []
            for device_name in device_names:
                device_info = self._get_device_info(device_name)
                if device_info:
                    devices.append(device_info)

            self.cached_devices = devices
            logger.debug(f"成功獲取 {len(devices)} 個裝置的電池資訊")
            return devices

        except requests.exceptions.Timeout:
            logger.error("LGSTray API 請求逾時")
            return []
        except requests.exceptions.ConnectionError:
            logger.debug("LGSTray 未執行")
            return []
        except Exception as e:
            logger.error(f"獲取羅技裝置資訊時發生錯誤: {e}")
            return []

    def _get_device_info(self, device_name):
        """獲取單個裝置的詳細資訊

        Args:
            device_name (str): 裝置名稱

        Returns:
            dict: 裝置資訊
        """
        try:
            url = f"{self.BASE_URL}/device/{device_name}"
            response = requests.get(url, timeout=3)

            if response.status_code != 200:
                return None

            # 解析 XML
            root = ET.fromstring(response.text)

            battery_percent = root.find('battery_percent')
            charging = root.find('charging')
            device_type = root.find('device_type')

            return {
                'name': device_name,
                'battery_percentage': float(battery_percent.text) if battery_percent is not None else None,
                'is_charging': charging.text == 'True' if charging is not None else False,
                'device_type': device_type.text if device_type is not None else 'Unknown'
            }

        except Exception as e:
            logger.error(f"獲取 {device_name} 資訊時發生錯誤: {e}")
            return None

    def get_headset_battery(self):
        """獲取耳機裝置的電池資訊

        Returns:
            dict: 耳機電池資訊，如果找不到則返回 None
        """
        devices = self.get_devices()

        if not devices:
            return None

        # 尋找耳機裝置
        for device in devices:
            name = device.get('name', '').lower()
            if any(keyword in name for keyword in ['headset', 'headphone', 'g535', 'g733']):
                return {
                    'device': device.get('name'),
                    'battery_level': device.get('battery_percentage'),
                    'is_charging': device.get('is_charging', False),
                    'status': 'ok',
                    'message': None
                }

        # 如果沒有找到耳機，返回第一個裝置
        if devices:
            device = devices[0]
            return {
                'device': device.get('name'),
                'battery_level': device.get('battery_percentage'),
                'is_charging': device.get('is_charging', False),
                'status': 'ok',
                'message': None
            }

        return None

    def format_battery_display(self, battery_info):
        """格式化電池資訊顯示

        Args:
            battery_info (dict): 電池資訊

        Returns:
            str: 格式化後的顯示文字
        """
        if battery_info is None or battery_info.get('battery_level') is None:
            return "耳機: 未連接"

        level = battery_info['battery_level']
        device = battery_info['device']
        is_charging = battery_info.get('is_charging', False)

        # 簡化裝置名稱
        short_name = device
        if len(short_name) > 20:
            short_name = short_name[:17] + "..."

        # 根據電量和充電狀態顯示不同的 emoji
        if is_charging:
            emoji = "🔌"
        elif level >= 80:
            emoji = "🔋"
        elif level >= 50:
            emoji = "🔋"
        elif level >= 20:
            emoji = "🪫"
        else:
            emoji = "🪫"

        return f"{emoji} {short_name}: {level}%"
