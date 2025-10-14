"""測試 ConfigManager 模組"""
import pytest
import os
import json
from config_manager import ConfigManager


class TestConfigManager:
    """ConfigManager 測試類別"""

    def test_init_with_default_config(self, temp_config_file):
        """測試使用預設配置初始化"""
        # 刪除臨時檔案,測試預設配置
        os.unlink(temp_config_file)

        config_manager = ConfigManager(temp_config_file)

        assert config_manager.config is not None
        assert config_manager.config['device_a'] is None
        assert config_manager.config['device_b'] is None
        assert config_manager.config['auto_start'] is False
        assert config_manager.config['music_volume'] == 70

    def test_load_existing_config(self, temp_config_file):
        """測試載入現有配置"""
        config_manager = ConfigManager(temp_config_file)

        assert config_manager.config is not None
        assert 'device_a' in config_manager.config
        assert 'rss_feeds' in config_manager.config

    def test_save_config(self, temp_config_file):
        """測試儲存配置"""
        config_manager = ConfigManager(temp_config_file)
        config_manager.config['test_key'] = 'test_value'

        result = config_manager.save_config()

        assert result is True

        # 重新載入驗證
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        assert loaded_config['test_key'] == 'test_value'

    def test_set_and_get_device_a(self, temp_config_file):
        """測試設定和取得裝置 A"""
        config_manager = ConfigManager(temp_config_file)
        device_info = {'id': 'device_a_id', 'name': 'Device A'}

        config_manager.set_device_a(device_info)
        result = config_manager.get_device_a()

        assert result == device_info
        assert result['id'] == 'device_a_id'
        assert result['name'] == 'Device A'

    def test_set_and_get_device_b(self, temp_config_file):
        """測試設定和取得裝置 B"""
        config_manager = ConfigManager(temp_config_file)
        device_info = {'id': 'device_b_id', 'name': 'Device B'}

        config_manager.set_device_b(device_info)
        result = config_manager.get_device_b()

        assert result == device_info

    def test_get_auto_start_default(self, temp_config_file):
        """測試取得開機自啟動預設值"""
        config_manager = ConfigManager(temp_config_file)

        result = config_manager.get_auto_start()

        assert result is False

    def test_get_usage_stats_empty(self, temp_config_file):
        """測試取得空的使用統計"""
        config_manager = ConfigManager(temp_config_file)

        stats = config_manager.get_usage_stats()

        assert stats == {}

    def test_record_device_usage(self, temp_config_file):
        """測試記錄裝置使用"""
        config_manager = ConfigManager(temp_config_file)
        device_info = {'id': 'test_device', 'name': 'Test Device'}

        config_manager.record_device_usage(device_info)
        stats = config_manager.get_usage_stats()

        assert 'test_device' in stats
        assert stats['test_device']['name'] == 'Test Device'
        assert stats['test_device']['switch_count'] == 1
        assert stats['test_device']['total_seconds'] >= 0

    def test_get_rss_feeds_empty(self, temp_config_file):
        """測試取得空的 RSS 訂閱"""
        config_manager = ConfigManager(temp_config_file)

        feeds = config_manager.get_rss_feeds()

        assert feeds == {}

    def test_set_rss_feeds(self, temp_config_file):
        """測試設定 RSS 訂閱"""
        config_manager = ConfigManager(temp_config_file)
        feeds = {
            'https://example.com/rss': {
                'title': 'Example RSS',
                'added_time': 1234567890
            }
        }

        config_manager.set_rss_feeds(feeds)
        result = config_manager.get_rss_feeds()

        assert result == feeds

    def test_get_music_volume_default(self, temp_config_file):
        """測試取得音樂音量預設值"""
        config_manager = ConfigManager(temp_config_file)

        volume = config_manager.get_music_volume()

        assert volume == 70

    def test_set_music_volume(self, temp_config_file):
        """測試設定音樂音量"""
        config_manager = ConfigManager(temp_config_file)

        config_manager.set_music_volume(85)
        result = config_manager.get_music_volume()

        assert result == 85

    def test_set_music_volume_bounds(self, temp_config_file):
        """測試音量邊界限制"""
        config_manager = ConfigManager(temp_config_file)

        # 測試超過上限
        config_manager.set_music_volume(150)
        assert config_manager.get_music_volume() == 100

        # 測試低於下限
        config_manager.set_music_volume(-10)
        assert config_manager.get_music_volume() == 0

    def test_read_articles_management(self, temp_config_file):
        """測試已讀文章管理"""
        config_manager = ConfigManager(temp_config_file)

        # 初始應為空
        read_articles = config_manager.get_read_articles()
        assert read_articles == []

        # 設定已讀文章
        test_articles = ['article1', 'article2', 'article3']
        config_manager.set_read_articles(test_articles)

        result = config_manager.get_read_articles()
        assert result == test_articles

    def test_favorite_articles_management(self, temp_config_file):
        """測試收藏文章管理"""
        config_manager = ConfigManager(temp_config_file)

        # 初始應為空
        favorites = config_manager.get_favorite_articles()
        assert favorites == {}

        # 設定收藏
        test_favorites = {
            'article1': {'title': 'Test Article', 'link': 'http://example.com'}
        }
        config_manager.set_favorite_articles(test_favorites)

        result = config_manager.get_favorite_articles()
        assert result == test_favorites

    def test_generic_get_method(self, temp_config_file):
        """測試通用 get() 方法"""
        config_manager = ConfigManager(temp_config_file)

        # 測試取得現有的配置
        volume = config_manager.get('music_volume')
        assert volume == 70

        # 測試取得不存在的鍵,應返回預設值
        result = config_manager.get('non_existent_key', 'default_value')
        assert result == 'default_value'

        # 測試不提供預設值,應返回 None
        result = config_manager.get('another_non_existent_key')
        assert result is None

    def test_generic_set_method(self, temp_config_file):
        """測試通用 set() 方法"""
        config_manager = ConfigManager(temp_config_file)

        # 測試設定新的配置項
        config_manager.set('auto_fetch_metadata', True)
        result = config_manager.get('auto_fetch_metadata')
        assert result is True

        # 測試修改現有配置項
        config_manager.set('music_volume', 50)
        result = config_manager.get('music_volume')
        assert result == 50

        # 測試設定複雜型別
        config_manager.set('custom_settings', {'key1': 'value1', 'key2': 123})
        result = config_manager.get('custom_settings')
        assert result == {'key1': 'value1', 'key2': 123}
