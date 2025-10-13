"""路徑工具模組

提供跨平台和網路路徑的處理工具函數
"""
import os
import re
from pathlib import Path
from logger import logger


# 已知的網路磁碟機映射
# 格式: 磁碟機代號 -> UNC 根路徑
NETWORK_DRIVE_MAPPINGS = {
    'Z:': '//ShuviNAS',
}


def normalize_network_path(path):
    """標準化網路路徑格式

    將 Windows 映射的網路磁碟機 (如 Z:) 轉換為 UNC 路徑格式
    同時標準化路徑分隔符為正斜線

    Args:
        path (str): 原始路徑

    Returns:
        str: 標準化後的路徑

    Examples:
        >>> normalize_network_path('Z:/Shuvi')
        '//ShuviNAS/Shuvi'
        >>> normalize_network_path('//ShuviNAS/Shuvi')
        '//ShuviNAS/Shuvi'
        >>> normalize_network_path('C:/Users')
        'C:/Users'
    """
    if not path:
        return path

    # 標準化反斜線為正斜線
    normalized = path.replace('\\', '/')

    # 檢查是否已經是 UNC 路徑格式
    if normalized.startswith('//'):
        return normalized

    # 檢查是否是已知的網路磁碟機
    for drive_letter, unc_path in NETWORK_DRIVE_MAPPINGS.items():
        drive_pattern = drive_letter.replace(':', '')
        # 匹配 Z:/ 或 Z: 開頭的路徑
        if normalized.upper().startswith(drive_letter.upper() + '/') or \
           normalized.upper() == drive_letter.upper():
            # 替換磁碟機代號為 UNC 路徑
            remaining_path = normalized[len(drive_letter):]
            if remaining_path.startswith('/'):
                remaining_path = remaining_path[1:]
            if remaining_path:
                return f"{unc_path}/{remaining_path}"
            return unc_path

    # 其他路徑保持不變
    return normalized


def is_network_path(path):
    """判斷路徑是否為網路路徑

    Args:
        path (str): 要檢查的路徑

    Returns:
        bool: 如果是網路路徑返回 True,否則返回 False

    Examples:
        >>> is_network_path('//ShuviNAS/Shuvi')
        True
        >>> is_network_path('Z:/Shuvi')
        True
        >>> is_network_path('C:/Users')
        False
    """
    if not path:
        return False

    # 標準化路徑
    normalized = path.replace('\\', '/')

    # 檢查是否是 UNC 路徑
    if normalized.startswith('//'):
        return True

    # 檢查是否是已知的網路磁碟機
    for drive_letter in NETWORK_DRIVE_MAPPINGS.keys():
        if normalized.upper().startswith(drive_letter.upper()):
            return True

    return False


def path_exists_safe(path):
    """安全地檢查路徑是否存在

    此函數會處理網路路徑和特殊字元,避免拋出異常

    Args:
        path (str): 要檢查的路徑

    Returns:
        bool: 如果路徑存在返回 True,否則返回 False

    Examples:
        >>> path_exists_safe('C:/Windows')
        True
        >>> path_exists_safe('Z:/NonExistent')
        False
        >>> path_exists_safe(None)
        False
    """
    if not path:
        return False

    try:
        # 先嘗試標準化為 UNC 路徑(如果是網路磁碟機)
        normalized_path = normalize_network_path(path)

        # 使用 os.path.exists 檢查
        return os.path.exists(normalized_path)

    except (OSError, ValueError, TypeError) as e:
        logger.debug(f"檢查路徑存在時發生錯誤: {path}, 錯誤: {e}")
        return False


def get_network_path_info(path):
    """取得網路路徑的詳細資訊

    Args:
        path (str): 網路路徑

    Returns:
        dict: 包含路徑資訊的字典
            {
                'original': 原始路徑,
                'normalized': 標準化後的路徑,
                'is_network': 是否為網路路徑,
                'exists': 路徑是否存在,
                'accessible': 路徑是否可訪問
            }
    """
    info = {
        'original': path,
        'normalized': normalize_network_path(path) if path else None,
        'is_network': is_network_path(path),
        'exists': False,
        'accessible': False
    }

    if info['normalized']:
        info['exists'] = path_exists_safe(info['normalized'])
        info['accessible'] = info['exists']

    return info
