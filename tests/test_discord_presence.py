"""測試 Discord Rich Presence 模組"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discord_presence import DiscordPresence  # noqa: E402


class TestDiscordPresenceInit:
    """測試 DiscordPresence 初始化"""

    def test_init_without_client_id(self):
        """測試沒有 client_id 時初始化"""
        presence = DiscordPresence()
        assert presence.client_id is None
        assert presence.rpc is None
        assert presence.connected is False

    def test_init_with_client_id(self):
        """測試有 client_id 時初始化"""
        presence = DiscordPresence(client_id="123456789")
        assert presence.client_id == "123456789"
        assert presence.rpc is None
        assert presence.connected is False

    def test_init_from_env(self):
        """測試從環境變數讀取 client_id"""
        with patch.dict(os.environ, {'DISCORD_CLIENT_ID': '987654321'}):
            presence = DiscordPresence()
            assert presence.client_id == "987654321"


class TestDiscordPresenceConnect:
    """測試 Discord 連接功能"""

    @patch('discord_presence.Presence')
    def test_connect_success(self, mock_presence_class):
        """測試成功連接 Discord"""
        mock_rpc = MagicMock()
        mock_presence_class.return_value = mock_rpc

        presence = DiscordPresence(client_id="123456789")
        result = presence.connect()

        assert result is True
        assert presence.connected is True
        assert presence.rpc == mock_rpc
        mock_presence_class.assert_called_once_with("123456789")
        mock_rpc.connect.assert_called_once()

    @patch('discord_presence.Presence')
    def test_connect_failure(self, mock_presence_class):
        """測試連接 Discord 失敗"""
        mock_rpc = MagicMock()
        mock_rpc.connect.side_effect = Exception("Connection failed")
        mock_presence_class.return_value = mock_rpc

        presence = DiscordPresence(client_id="123456789")
        result = presence.connect()

        assert result is False
        assert presence.connected is False

    def test_connect_without_client_id(self):
        """測試沒有 client_id 時連接"""
        presence = DiscordPresence()
        result = presence.connect()

        assert result is False
        assert presence.connected is False

    @patch('discord_presence.Presence')
    def test_connect_already_connected(self, mock_presence_class):
        """測試已經連接時再次連接"""
        mock_rpc = MagicMock()
        mock_presence_class.return_value = mock_rpc

        presence = DiscordPresence(client_id="123456789")
        presence.connect()
        # 再次連接
        result = presence.connect()

        assert result is True
        # 應該只呼叫一次
        mock_presence_class.assert_called_once()


class TestDiscordPresenceUpdate:
    """測試更新 Discord 狀態"""

    @patch('discord_presence.Presence')
    def test_update_playing(self, mock_presence_class):
        """測試更新正在播放的歌曲"""
        mock_rpc = MagicMock()
        mock_presence_class.return_value = mock_rpc

        presence = DiscordPresence(client_id="123456789")
        presence.connect()

        presence.update_playing(
            song_name="Test Song",
            artist="Test Artist",
            album="Test Album"
        )

        mock_rpc.update.assert_called_once()
        call_args = mock_rpc.update.call_args[1]
        assert "Test Song" in call_args['details']
        assert "Test Artist" in call_args['state']

    @patch('discord_presence.Presence')
    def test_update_playing_with_progress(self, mock_presence_class):
        """測試更新播放進度"""
        mock_rpc = MagicMock()
        mock_presence_class.return_value = mock_rpc

        presence = DiscordPresence(client_id="123456789")
        presence.connect()

        presence.update_playing(
            song_name="Test Song",
            artist="Test Artist",
            current_time=60,
            total_time=240
        )

        mock_rpc.update.assert_called_once()

    @patch('discord_presence.Presence')
    def test_update_playing_not_connected(self, mock_presence_class):
        """測試未連接時更新狀態"""
        presence = DiscordPresence(client_id="123456789")
        # 不連接直接更新
        presence.update_playing(song_name="Test")

        # 應該自動嘗試連接
        mock_presence_class.assert_called_once()

    @patch('discord_presence.Presence')
    def test_update_playing_minimal_info(self, mock_presence_class):
        """測試只提供歌曲名稱時更新"""
        mock_rpc = MagicMock()
        mock_presence_class.return_value = mock_rpc

        presence = DiscordPresence(client_id="123456789")
        presence.connect()

        presence.update_playing(song_name="Test Song")

        mock_rpc.update.assert_called_once()


class TestDiscordPresenceClear:
    """測試清除 Discord 狀態"""

    @patch('discord_presence.Presence')
    def test_clear_presence(self, mock_presence_class):
        """測試清除狀態"""
        mock_rpc = MagicMock()
        mock_presence_class.return_value = mock_rpc

        presence = DiscordPresence(client_id="123456789")
        presence.connect()
        presence.clear()

        mock_rpc.clear.assert_called_once()

    def test_clear_not_connected(self):
        """測試未連接時清除狀態"""
        presence = DiscordPresence(client_id="123456789")
        # 不應該拋出異常
        presence.clear()


class TestDiscordPresenceDisconnect:
    """測試斷開 Discord 連接"""

    @patch('discord_presence.Presence')
    def test_disconnect(self, mock_presence_class):
        """測試斷開連接"""
        mock_rpc = MagicMock()
        mock_presence_class.return_value = mock_rpc

        presence = DiscordPresence(client_id="123456789")
        presence.connect()
        presence.disconnect()

        mock_rpc.close.assert_called_once()
        assert presence.connected is False
        assert presence.rpc is None

    def test_disconnect_not_connected(self):
        """測試未連接時斷開"""
        presence = DiscordPresence(client_id="123456789")
        # 不應該拋出異常
        presence.disconnect()

    @patch('discord_presence.Presence')
    def test_disconnect_with_exception(self, mock_presence_class):
        """測試斷開時發生異常"""
        mock_rpc = MagicMock()
        mock_rpc.close.side_effect = Exception("Close failed")
        mock_presence_class.return_value = mock_rpc

        presence = DiscordPresence(client_id="123456789")
        presence.connect()
        presence.disconnect()

        # 應該標記為已斷開
        assert presence.connected is False


class TestDiscordPresenceContextManager:
    """測試 Context Manager 功能"""

    @patch('discord_presence.Presence')
    def test_context_manager(self, mock_presence_class):
        """測試作為 context manager 使用"""
        mock_rpc = MagicMock()
        mock_presence_class.return_value = mock_rpc

        with DiscordPresence(client_id="123456789") as presence:
            assert presence.connected is True

        # 離開 context 時應該斷開
        mock_rpc.close.assert_called_once()
