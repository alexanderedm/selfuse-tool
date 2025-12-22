"""
安全配置管理模組

使用 Windows DPAPI (Data Protection API) 加密敏感資訊（如 API Keys）
並安全地儲存在配置文件中。

特點：
- Windows 系統層級加密
- 只有當前用戶和當前機器可以解密
- 不會將明文 API Key 寫入配置文件
- 自動處理加密/解密
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional
from src.core.logger import logger

# Windows DPAPI
try:
    import win32crypt
    HAS_DPAPI = True
except ImportError:
    HAS_DPAPI = False
    logger.warning("無法導入 win32crypt，將使用明文儲存（不安全）")


class SecureConfig:
    """安全配置管理器"""

    def __init__(self, config_path: str = "secure_config.json"):
        """初始化安全配置管理器

        Args:
            config_path: 配置文件路徑
        """
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """載入配置文件

        Returns:
            dict: 配置資料
        """
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入安全配置失敗: {e}")
            return {}

    def _save_config(self) -> bool:
        """儲存配置文件

        Returns:
            bool: 是否成功
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"儲存安全配置失敗: {e}")
            return False

    def _encrypt_data(self, data: str) -> str:
        """使用 Windows DPAPI 加密資料

        Args:
            data: 要加密的明文字串

        Returns:
            str: Base64 編碼的加密資料
        """
        if not HAS_DPAPI:
            logger.warning("DPAPI 不可用，將以明文儲存（不建議）")
            return base64.b64encode(data.encode('utf-8')).decode('utf-8')

        try:
            # 使用 DPAPI 加密
            encrypted_bytes = win32crypt.CryptProtectData(
                data.encode('utf-8'),
                "Selftool Secure Config",  # 描述
                None,  # 可選的附加熵
                None,  # 保留
                None,  # 提示結構
                0      # 標誌
            )
            # 轉換為 Base64 以便儲存在 JSON
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"加密資料失敗: {e}")
            raise

    def _decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """使用 Windows DPAPI 解密資料

        Args:
            encrypted_data: Base64 編碼的加密資料

        Returns:
            Optional[str]: 解密後的明文，失敗時返回 None
        """
        if not encrypted_data:
            return None

        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))

            if not HAS_DPAPI:
                # 如果沒有 DPAPI，假設資料是 Base64 編碼的明文
                return encrypted_bytes.decode('utf-8')

            # 使用 DPAPI 解密
            _, decrypted_bytes = win32crypt.CryptUnprotectData(
                encrypted_bytes,
                None,
                None,
                None,
                0
            )
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"解密資料失敗: {e}")
            return None

    def set_api_key(self, service: str, api_key: str) -> bool:
        """設定 API Key（加密儲存）

        Args:
            service: 服務名稱（例如：'openai', 'anthropic'）
            api_key: API Key 明文

        Returns:
            bool: 是否成功
        """
        try:
            encrypted = self._encrypt_data(api_key)
            self._config[f"api_key_{service}"] = encrypted
            return self._save_config()
        except Exception as e:
            logger.error(f"設定 API Key 失敗 ({service}): {e}")
            return False

    def get_api_key(self, service: str) -> Optional[str]:
        """取得 API Key（自動解密）

        Args:
            service: 服務名稱

        Returns:
            Optional[str]: 解密後的 API Key，不存在時返回 None
        """
        key_name = f"api_key_{service}"
        encrypted = self._config.get(key_name)

        if not encrypted:
            return None

        return self._decrypt_data(encrypted)

    def remove_api_key(self, service: str) -> bool:
        """移除 API Key

        Args:
            service: 服務名稱

        Returns:
            bool: 是否成功
        """
        key_name = f"api_key_{service}"
        if key_name in self._config:
            del self._config[key_name]
            return self._save_config()
        return False

    def has_api_key(self, service: str) -> bool:
        """檢查是否有設定 API Key

        Args:
            service: 服務名稱

        Returns:
            bool: 是否已設定
        """
        key_name = f"api_key_{service}"
        return key_name in self._config

    def get_or_env(self, service: str, env_var: str) -> Optional[str]:
        """優先從配置取得 API Key，否則從環境變數取得

        Args:
            service: 服務名稱
            env_var: 環境變數名稱

        Returns:
            Optional[str]: API Key，兩者都不存在時返回 None
        """
        # 優先從配置文件取得
        api_key = self.get_api_key(service)
        if api_key:
            logger.info(f"從加密配置載入 {service} API Key")
            return api_key

        # 從環境變數取得
        api_key = os.environ.get(env_var)
        if api_key:
            logger.info(f"從環境變數載入 {service} API Key")
            return api_key

        return None

    def list_configured_services(self) -> list[str]:
        """列出所有已配置 API Key 的服務

        Returns:
            list[str]: 服務名稱列表
        """
        services = []
        for key in self._config.keys():
            if key.startswith("api_key_"):
                service = key.replace("api_key_", "")
                services.append(service)
        return services


# 全域實例（單例模式）
_secure_config_instance = None


def get_secure_config() -> SecureConfig:
    """取得全域安全配置實例

    Returns:
        SecureConfig: 安全配置管理器實例
    """
    global _secure_config_instance
    if _secure_config_instance is None:
        _secure_config_instance = SecureConfig()
    return _secure_config_instance


# 便利函數
def get_openai_api_key() -> Optional[str]:
    """取得 OpenAI API Key（配置優先，環境變數次之）

    Returns:
        Optional[str]: API Key
    """
    return get_secure_config().get_or_env("openai", "OPENAI_API_KEY")


def set_openai_api_key(api_key: str) -> bool:
    """設定 OpenAI API Key

    Args:
        api_key: API Key

    Returns:
        bool: 是否成功
    """
    return get_secure_config().set_api_key("openai", api_key)
