"""RSS 訂閱管理模組"""
import feedparser
import time
import re
from datetime import datetime
from urllib.parse import urlparse
from constants import RSS_CACHE_TIMEOUT, RSS_MAX_ENTRIES


class RSSManager:
    """管理 RSS 訂閱的類別"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.cache = {}  # 快取 RSS 內容 {url: {'entries': [], 'last_update': timestamp}}
        self.cache_timeout = RSS_CACHE_TIMEOUT  # 快取有效期

    def is_valid_rss_url(self, url):
        """檢查 URL 是否可能是 RSS 連結

        Args:
            url (str): 要檢查的 URL

        Returns:
            bool: 是否可能是 RSS 連結
        """
        if not url:
            return False

        # 檢查是否為有效 URL
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False
        except:
            return False

        # 檢查常見的 RSS 路徑和副檔名
        rss_patterns = [
            r'/rss',
            r'/feed',
            r'/atom',
            r'\.rss',
            r'\.xml',
            r'rss\.php',
            r'feed\.php',
        ]

        url_lower = url.lower()
        for pattern in rss_patterns:
            if re.search(pattern, url_lower):
                return True

        # 檢查 URL 中是否包含 rss/feed 關鍵字
        if 'rss' in url_lower or 'feed' in url_lower or 'atom' in url_lower:
            return True

        return False

    def validate_rss_feed(self, url):
        """驗證 URL 是否為有效的 RSS feed

        Args:
            url (str): RSS feed URL

        Returns:
            dict: {'valid': bool, 'title': str, 'error': str}
        """
        try:
            feed = feedparser.parse(url)

            # 檢查是否有解析錯誤
            if feed.bozo:
                # 有些 feed 雖然 bozo 為 True 但仍可用
                if not feed.entries and not feed.get('feed'):
                    return {
                        'valid': False,
                        'title': None,
                        'error': '無法解析 RSS feed 格式'
                    }

            # 檢查是否有內容
            if not feed.get('feed') and not feed.entries:
                return {
                    'valid': False,
                    'title': None,
                    'error': 'RSS feed 沒有內容'
                }

            # 取得 feed 標題
            title = feed.feed.get('title', url)

            return {
                'valid': True,
                'title': title,
                'error': None
            }

        except Exception as e:
            return {
                'valid': False,
                'title': None,
                'error': f'網路錯誤: {str(e)}'
            }

    def add_feed(self, url):
        """新增 RSS 訂閱

        Args:
            url (str): RSS feed URL

        Returns:
            dict: {'success': bool, 'message': str, 'title': str}
        """
        # 驗證 feed
        validation = self.validate_rss_feed(url)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['error'],
                'title': None
            }

        # 檢查是否已訂閱
        feeds = self.config_manager.get_rss_feeds()
        if url in feeds:
            return {
                'success': False,
                'message': '此 RSS 已經訂閱過了',
                'title': validation['title']
            }

        # 新增訂閱
        feeds[url] = {
            'title': validation['title'],
            'added_time': time.time()
        }
        self.config_manager.set_rss_feeds(feeds)

        return {
            'success': True,
            'message': f'已成功訂閱: {validation["title"]}',
            'title': validation['title']
        }

    def remove_feed(self, url):
        """移除 RSS 訂閱

        Args:
            url (str): RSS feed URL

        Returns:
            bool: 是否成功
        """
        feeds = self.config_manager.get_rss_feeds()
        if url in feeds:
            del feeds[url]
            self.config_manager.set_rss_feeds(feeds)
            # 清除快取
            if url in self.cache:
                del self.cache[url]
            return True
        return False

    def get_all_feeds(self):
        """取得所有訂閱的 RSS feeds

        Returns:
            dict: {url: {'title': str, 'added_time': float}}
        """
        return self.config_manager.get_rss_feeds()

    def fetch_feed_entries(self, url, force_refresh=False):
        """抓取指定 RSS feed 的文章列表

        Args:
            url (str): RSS feed URL
            force_refresh (bool): 是否強制重新抓取(忽略快取)

        Returns:
            list: 文章列表 [{'title': str, 'link': str, 'published': str, 'summary': str}]
        """
        # 檢查快取
        if not force_refresh and url in self.cache:
            cache_data = self.cache[url]
            if time.time() - cache_data['last_update'] < self.cache_timeout:
                return cache_data['entries']

        # 抓取 feed
        try:
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                return []

            entries = []
            for entry in feed.entries[:RSS_MAX_ENTRIES]:  # 最多取設定數量的文章
                # 處理發布時間
                published = '未知時間'
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published = time.strftime('%Y-%m-%d %H:%M', entry.published_parsed)
                    except:
                        pass
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    try:
                        published = time.strftime('%Y-%m-%d %H:%M', entry.updated_parsed)
                    except:
                        pass

                # 處理內容 - 優先使用完整內容,其次使用摘要
                content = ''
                summary = ''

                # 嘗試取得完整內容
                if hasattr(entry, 'content') and entry.content:
                    # content 通常是列表
                    if isinstance(entry.content, list) and len(entry.content) > 0:
                        content = entry.content[0].get('value', '')
                    else:
                        content = str(entry.content)

                # 如果沒有完整內容,使用摘要
                if not content and hasattr(entry, 'summary'):
                    content = entry.summary

                # 如果有 description 欄位也嘗試使用
                if not content and hasattr(entry, 'description'):
                    content = entry.description

                # 移除 HTML 標籤建立純文字版本
                if content:
                    # 保留原始 HTML 內容
                    content_html = content
                    # 建立純文字版本
                    content_text = re.sub('<[^<]+?>', '', content)
                    # 清理多餘空白
                    content_text = re.sub(r'\s+', ' ', content_text).strip()

                    # 建立摘要 (前200字)
                    if len(content_text) > 200:
                        summary = content_text[:200] + '...'
                    else:
                        summary = content_text
                else:
                    content_html = ''
                    content_text = '無內容'
                    summary = '無內容'

                # 產生文章唯一 ID (使用 link 作為 ID)
                article_id = entry.get('link', '')

                entries.append({
                    'id': article_id,
                    'title': entry.get('title', '無標題'),
                    'link': entry.get('link', ''),
                    'published': published,
                    'summary': summary,
                    'content': content_text,  # 完整純文字內容
                    'content_html': content_html  # 原始 HTML 內容
                })

            # 更新快取
            self.cache[url] = {
                'entries': entries,
                'last_update': time.time()
            }

            return entries

        except Exception as e:
            print(f"抓取 RSS feed 失敗: {e}")
            return []

    def fetch_all_feeds(self, force_refresh=False):
        """抓取所有訂閱的 RSS feeds

        Args:
            force_refresh (bool): 是否強制重新抓取

        Returns:
            dict: {url: {'title': str, 'entries': list, 'error': str}}
        """
        result = {}
        feeds = self.get_all_feeds()

        for url, feed_info in feeds.items():
            try:
                entries = self.fetch_feed_entries(url, force_refresh)
                result[url] = {
                    'title': feed_info['title'],
                    'entries': entries,
                    'error': None if entries else '無法抓取內容'
                }
            except Exception as e:
                result[url] = {
                    'title': feed_info['title'],
                    'entries': [],
                    'error': str(e)
                }

        return result

    def clear_cache(self):
        """清除所有快取"""
        self.cache = {}

    # ==================== 文章狀態管理 ====================

    def mark_as_read(self, article_id):
        """標記文章為已讀

        Args:
            article_id (str): 文章 ID (通常是 link)
        """
        read_articles = self.config_manager.get_read_articles()
        if article_id not in read_articles:
            read_articles.append(article_id)
            self.config_manager.set_read_articles(read_articles)

    def mark_as_unread(self, article_id):
        """標記文章為未讀

        Args:
            article_id (str): 文章 ID
        """
        read_articles = self.config_manager.get_read_articles()
        if article_id in read_articles:
            read_articles.remove(article_id)
            self.config_manager.set_read_articles(read_articles)

    def is_read(self, article_id):
        """檢查文章是否已讀

        Args:
            article_id (str): 文章 ID

        Returns:
            bool: 是否已讀
        """
        read_articles = self.config_manager.get_read_articles()
        return article_id in read_articles

    def add_favorite(self, article_id, article_data):
        """新增收藏文章

        Args:
            article_id (str): 文章 ID
            article_data (dict): 文章資料
        """
        favorites = self.config_manager.get_favorite_articles()
        favorites[article_id] = {
            'title': article_data.get('title', ''),
            'link': article_data.get('link', ''),
            'published': article_data.get('published', ''),
            'summary': article_data.get('summary', ''),
            'added_time': time.time()
        }
        self.config_manager.set_favorite_articles(favorites)

    def remove_favorite(self, article_id):
        """移除收藏

        Args:
            article_id (str): 文章 ID
        """
        favorites = self.config_manager.get_favorite_articles()
        if article_id in favorites:
            del favorites[article_id]
            self.config_manager.set_favorite_articles(favorites)

    def is_favorite(self, article_id):
        """檢查文章是否已收藏

        Args:
            article_id (str): 文章 ID

        Returns:
            bool: 是否已收藏
        """
        favorites = self.config_manager.get_favorite_articles()
        return article_id in favorites

    def get_all_favorites(self):
        """取得所有收藏的文章

        Returns:
            dict: {article_id: article_data}
        """
        return self.config_manager.get_favorite_articles()
