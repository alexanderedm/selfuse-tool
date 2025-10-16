"""音訊裝置管理模組"""
import warnings
# 隱藏 pycaw 的警告訊息
warnings.filterwarnings('ignore', module='pycaw')

from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL, CoCreateInstance, GUID
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, EDataFlow, ERole
from pycaw.constants import CLSID_MMDeviceEnumerator
from pycaw.api.mmdeviceapi import IMMDeviceEnumerator, IMMDevice


class AudioManager:
    """管理音訊裝置的類別"""

    def __init__(self):
        self.device_enumerator = None
        self._init_device_enumerator()

    def _init_device_enumerator(self):
        """初始化裝置列舉器"""
        from src.core.logger import logger
        try:
            self.device_enumerator = CoCreateInstance(
                CLSID_MMDeviceEnumerator,
                IMMDeviceEnumerator,
                CLSCTX_ALL
            )
        except Exception as e:
            logger.error(f"初始化音訊裝置失敗: {e}", exc_info=True)
            self.device_enumerator = None

    def get_all_output_devices(self):
        """取得所有音訊輸出裝置

        Returns:
            list: 裝置列表，每個項目包含 {'id': str, 'name': str}
        """
        devices = []
        try:
            # 初始化 COM (對於新執行緒很重要)
            import comtypes
            try:
                comtypes.CoInitialize()
            except:
                pass  # 如果已經初始化就忽略

            # 直接使用 AudioUtilities 的方法
            all_devices = AudioUtilities.GetAllDevices()

            for device in all_devices:
                # 只取輸出裝置
                try:
                    # 檢查是否為輸出裝置 (有 FriendlyName 屬性)
                    if hasattr(device, 'id') and hasattr(device, 'FriendlyName'):
                        devices.append({
                            'id': device.id,
                            'name': device.FriendlyName
                        })
                except Exception:
                    # 個別裝置讀取失敗時跳過,不影響其他裝置
                    continue

        except Exception as e:
            from src.core.logger import logger
            logger.error(f"取得音訊裝置列表失敗: {e}", exc_info=True)

        return devices

    def get_default_device(self):
        """取得當前預設的音訊輸出裝置

        Returns:
            dict: {'id': str, 'name': str} 或 None
        """
        try:
            # 初始化 COM (對於新執行緒很重要)
            import comtypes
            try:
                comtypes.CoInitialize()
            except:
                pass  # 如果已經初始化就忽略

            if not self.device_enumerator:
                self._init_device_enumerator()

            device = self.device_enumerator.GetDefaultAudioEndpoint(EDataFlow.eRender.value, ERole.eMultimedia.value)
            device_id = device.GetId()

            # 使用 AudioUtilities 的方法
            devices_list = AudioUtilities.GetAllDevices()
            name = "Unknown"
            for d in devices_list:
                if d.id == device_id:
                    name = d.FriendlyName
                    break

            return {
                'id': device_id,
                'name': name
            }
        except Exception as e:
            from src.core.logger import logger
            logger.error(f"取得預設裝置失敗: {e}", exc_info=True)
            return None

    def set_default_device(self, device_id):
        """設定預設音訊輸出裝置

        Args:
            device_id (str): 裝置 ID

        Returns:
            bool: 是否成功
        """
        try:
            # 初始化 COM
            import comtypes
            try:
                comtypes.CoInitialize()
            except:
                pass

            # 使用 PolicyConfig COM 介面來設定預設裝置
            from comtypes import CoCreateInstance, GUID
            from ctypes import POINTER, c_wchar_p

            # PolicyConfig GUID (Windows 10/11)
            CLSID_PolicyConfig = GUID('{870AF99C-171D-4F9E-AF0D-E63DF40C2BC9}')

            # 定義 IPolicyConfig 介面
            class IPolicyConfig(comtypes.IUnknown):
                _iid_ = GUID('{F8679F50-850A-41CF-9C72-430F290290C8}')
                _methods_ = [
                    comtypes.STDMETHOD(comtypes.HRESULT, 'GetMixFormat'),
                    comtypes.STDMETHOD(comtypes.HRESULT, 'GetDeviceFormat'),
                    comtypes.STDMETHOD(comtypes.HRESULT, 'ResetDeviceFormat'),
                    comtypes.STDMETHOD(comtypes.HRESULT, 'SetDeviceFormat'),
                    comtypes.STDMETHOD(comtypes.HRESULT, 'GetProcessingPeriod'),
                    comtypes.STDMETHOD(comtypes.HRESULT, 'SetProcessingPeriod'),
                    comtypes.STDMETHOD(comtypes.HRESULT, 'GetShareMode'),
                    comtypes.STDMETHOD(comtypes.HRESULT, 'SetShareMode'),
                    comtypes.STDMETHOD(comtypes.HRESULT, 'GetPropertyValue'),
                    comtypes.STDMETHOD(comtypes.HRESULT, 'SetPropertyValue'),
                    comtypes.STDMETHOD(comtypes.HRESULT, 'SetDefaultEndpoint', [c_wchar_p, comtypes.c_int]),
                    comtypes.STDMETHOD(comtypes.HRESULT, 'SetEndpointVisibility'),
                ]

            # 建立 PolicyConfig 實例
            try:
                policy_config = CoCreateInstance(CLSID_PolicyConfig, IPolicyConfig, CLSCTX_ALL)
                # 設定為預設裝置 (0 = eConsole, 1 = eMultimedia, 2 = eCommunications)
                # 設定所有角色
                for role in [0, 1, 2]:
                    policy_config.SetDefaultEndpoint(device_id, role)
                return True
            except Exception as e:
                # 嘗試備用 GUID (Windows 7/8)
                CLSID_PolicyConfig_Win7 = GUID('{294935CE-F637-4E7C-A41B-AB255460B862}')
                try:
                    policy_config = CoCreateInstance(CLSID_PolicyConfig_Win7, IPolicyConfig, CLSCTX_ALL)
                    for role in [0, 1, 2]:
                        policy_config.SetDefaultEndpoint(device_id, role)
                    return True
                except Exception as e2:
                    return False

        except Exception as e:
            return False
