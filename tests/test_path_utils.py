"""測試路徑工具模組"""
import pytest
import os
from src.utils.path_utils import (
    normalize_network_path,
    is_network_path,
    path_exists_safe
)


class TestPathUtils:
    """路徑工具測試類別"""

    def test_normalize_network_path_z_drive(self):
        """測試 Z: 磁碟機路徑轉換為 UNC 路徑"""
        # Z: 磁碟機應該轉換為 UNC 路徑
        result = normalize_network_path('Z:/Shuvi')
        assert result == '//ShuviNAS/Shuvi'

        result = normalize_network_path('Z:\\Shuvi\\Music')
        assert result == '//ShuviNAS/Shuvi/Music'

    def test_normalize_network_path_already_unc(self):
        """測試已經是 UNC 路徑的情況"""
        # 已經是 UNC 路徑,應該保持不變
        result = normalize_network_path('//ShuviNAS/Shuvi')
        assert result == '//ShuviNAS/Shuvi'

        result = normalize_network_path('\\\\ShuviNAS\\Shuvi')
        assert result == '//ShuviNAS/Shuvi'

    def test_normalize_network_path_local_drive(self):
        """測試本地磁碟機路徑不應被轉換"""
        # 本地磁碟機路徑應該保持不變
        result = normalize_network_path('C:/Users/Music')
        assert result == 'C:/Users/Music'

        result = normalize_network_path('D:\\Data')
        assert result == 'D:/Data'

    def test_normalize_network_path_relative(self):
        """測試相對路徑保持不變"""
        result = normalize_network_path('./music')
        assert result == './music'

        result = normalize_network_path('../data')
        assert result == '../data'

    def test_is_network_path_unc(self):
        """測試識別 UNC 路徑"""
        assert is_network_path('//ShuviNAS/Shuvi') is True
        assert is_network_path('\\\\ShuviNAS\\Shuvi') is True

    def test_is_network_path_mapped_drive(self):
        """測試識別映射的網路磁碟機"""
        # Z: 是已知的網路磁碟機
        assert is_network_path('Z:/Shuvi') is True
        assert is_network_path('Z:\\Shuvi') is True

    def test_is_network_path_local(self):
        """測試識別本地路徑"""
        assert is_network_path('C:/Users') is False
        assert is_network_path('D:\\Data') is False
        assert is_network_path('./music') is False

    def test_path_exists_safe_valid_path(self, temp_music_dir):
        """測試安全的路徑存在檢查 - 有效路徑"""
        result = path_exists_safe(temp_music_dir)
        assert result is True

    def test_path_exists_safe_invalid_path(self):
        """測試安全的路徑存在檢查 - 無效路徑"""
        result = path_exists_safe('Z:/NonExistentPath')
        assert result is False

    def test_path_exists_safe_none(self):
        """測試安全的路徑存在檢查 - None 輸入"""
        result = path_exists_safe(None)
        assert result is False

    def test_path_exists_safe_empty(self):
        """測試安全的路徑存在檢查 - 空字串"""
        result = path_exists_safe('')
        assert result is False

    def test_path_exists_safe_unc_path(self):
        """測試安全的路徑存在檢查 - UNC 路徑"""
        # 測試實際的 UNC 路徑
        result = path_exists_safe('//ShuviNAS/Shuvi')
        # 此測試依賴實際網路環境,如果網路可用應該返回 True
        # 但在測試環境中我們只驗證不會拋出異常
        assert isinstance(result, bool)
