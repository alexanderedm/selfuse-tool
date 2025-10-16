"""測試 RSSManager 模組"""
import pytest
from src.rss.rss_manager import RSSManager


class TestRSSManager:
    """RSSManager 測試類別"""

    @pytest.fixture
    def mock_config_manager(self, temp_config_file):
        """建立 mock ConfigManager"""
        from src.core.config_manager import ConfigManager
        return ConfigManager(temp_config_file)

    @pytest.fixture
    def rss_manager(self, mock_config_manager):
        """建立 RSSManager 實例"""
        return RSSManager(mock_config_manager)

    def test_init(self, rss_manager):
        """測試初始化"""
        assert rss_manager.cache == {}
        assert rss_manager.cache_timeout == 300

    def test_is_valid_rss_url_valid(self, rss_manager):
        """測試有效的 RSS URL"""
        valid_urls = [
            'https://example.com/rss',
            'https://example.com/feed',
            'https://example.com/feed.xml',
            'https://blog.example.com/atom.xml',
            'https://example.com/rss.php'
        ]

        for url in valid_urls:
            assert rss_manager.is_valid_rss_url(url) is True

    def test_is_valid_rss_url_invalid(self, rss_manager):
        """測試無效的 RSS URL"""
        invalid_urls = [
            '',
            None,
            'not a url',
            'https://example.com/page',
            'ftp://example.com/file'  # ftp 協議但不包含 RSS 關鍵字
        ]

        for url in invalid_urls:
            assert rss_manager.is_valid_rss_url(url) is False

    def test_get_all_feeds_empty(self, rss_manager):
        """測試取得空的訂閱列表"""
        feeds = rss_manager.get_all_feeds()

        assert feeds == {}

    def test_clear_cache(self, rss_manager):
        """測試清除快取"""
        rss_manager.cache = {'test': 'data'}

        rss_manager.clear_cache()

        assert rss_manager.cache == {}

    def test_mark_as_read(self, rss_manager):
        """測試標記為已讀"""
        article_id = 'test_article_123'

        rss_manager.mark_as_read(article_id)

        assert rss_manager.is_read(article_id) is True

    def test_mark_as_unread(self, rss_manager):
        """測試標記為未讀"""
        article_id = 'test_article_123'

        # 先標記為已讀
        rss_manager.mark_as_read(article_id)
        assert rss_manager.is_read(article_id) is True

        # 再標記為未讀
        rss_manager.mark_as_unread(article_id)
        assert rss_manager.is_read(article_id) is False

    def test_is_read_new_article(self, rss_manager):
        """測試檢查未讀文章"""
        assert rss_manager.is_read('new_article') is False

    def test_add_favorite(self, rss_manager):
        """測試新增收藏"""
        article_id = 'fav_article_123'
        article_data = {
            'title': 'Favorite Article',
            'link': 'https://example.com/article',
            'published': '2025-10-13',
            'summary': 'Test summary'
        }

        rss_manager.add_favorite(article_id, article_data)

        assert rss_manager.is_favorite(article_id) is True

    def test_remove_favorite(self, rss_manager):
        """測試移除收藏"""
        article_id = 'fav_article_123'
        article_data = {'title': 'Test', 'link': 'http://test.com'}

        # 先加入收藏
        rss_manager.add_favorite(article_id, article_data)
        assert rss_manager.is_favorite(article_id) is True

        # 移除收藏
        rss_manager.remove_favorite(article_id)
        assert rss_manager.is_favorite(article_id) is False

    def test_get_all_favorites_empty(self, rss_manager):
        """測試取得空的收藏列表"""
        favorites = rss_manager.get_all_favorites()

        assert favorites == {}

    def test_get_all_favorites_with_data(self, rss_manager):
        """測試取得包含資料的收藏列表"""
        article_id = 'fav_1'
        article_data = {'title': 'Test', 'link': 'http://test.com'}

        rss_manager.add_favorite(article_id, article_data)
        favorites = rss_manager.get_all_favorites()

        assert article_id in favorites
        assert favorites[article_id]['title'] == 'Test'
