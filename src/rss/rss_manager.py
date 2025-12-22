"""RSS 訂閱管理模組"""
import feedparser
import time
import re
from datetime import datetime
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.core.constants import RSS_CACHE_TIMEOUT, RSS_MAX_ENTRIES
from src.core.logger import logger


class RSSManager:
    """管理 RSS 訂閱的類別"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.cache = {}  # 快取 RSS 內容 {url: {'entries': [], 'last_update': timestamp}}
        self.cache_timeout = RSS_CACHE_TIMEOUT  # 快取有效期
        self.executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="RSS-Fetcher")

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

    def _get_cached_entries(self, url):
        """從快取取得文章列表

        Args:
            url (str): RSS feed URL

        Returns:
            list or None: 快取的文章列表，如果快取無效則返回 None
        """
        if url not in self.cache:
            return None

        cache_data = self.cache[url]
        if time.time() - cache_data['last_update'] < self.cache_timeout:
            return cache_data['entries']

        return None

    def _parse_publish_time(self, entry):
        """解析文章發布時間

        Args:
            entry: feedparser entry 物件

        Returns:
            str: 格式化的發布時間
        """
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                return time.strftime('%Y-%m-%d %H:%M', entry.published_parsed)
            except:
                pass

        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            try:
                return time.strftime('%Y-%m-%d %H:%M', entry.updated_parsed)
            except:
                pass

        return '未知時間'

    def _extract_entry_content(self, entry):
        """提取文章內容

        Args:
            entry: feedparser entry 物件

        Returns:
            str: 文章內容（可能包含 HTML）
        """
        # 嘗試取得完整內容
        if hasattr(entry, 'content') and entry.content:
            if isinstance(entry.content, list) and len(entry.content) > 0:
                return entry.content[0].get('value', '')
            return str(entry.content)

        # 如果沒有完整內容，使用摘要
        if hasattr(entry, 'summary'):
            return entry.summary

        # 如果有 description 欄位也嘗試使用
        if hasattr(entry, 'description'):
            return entry.description

        return ''

    def _process_content_and_summary(self, content):
        """處理內容並生成摘要

        Args:
            content (str): 原始內容（可能包含 HTML）

        Returns:
            tuple: (content_html, content_text, summary)
        """
        if not content:
            return '', '無內容', '無內容'

        content_html = content
        # 移除 HTML 標籤建立純文字版本
        content_text = re.sub('<[^<]+?>', '', content)
        # 清理多餘空白
        content_text = re.sub(r'\s+', ' ', content_text).strip()

        # 建立摘要（前200字）
        if len(content_text) > 200:
            summary = content_text[:200] + '...'
        else:
            summary = content_text

        return content_html, content_text, summary

    def _parse_feed_entry(self, entry):
        """解析單個 feed entry

        Args:
            entry: feedparser entry 物件

        Returns:
            dict: 解析後的文章資料
        """
        published = self._parse_publish_time(entry)
        content = self._extract_entry_content(entry)
        content_html, content_text, summary = self._process_content_and_summary(content)

        return {
            'id': entry.get('link', ''),
            'title': entry.get('title', '無標題'),
            'link': entry.get('link', ''),
            'published': published,
            'summary': summary,
            'content': content_text,
            'content_html': content_html
        }

    def _update_cache(self, url, entries):
        """更新快取

        Args:
            url (str): RSS feed URL
            entries (list): 文章列表
        """
        self.cache[url] = {
            'entries': entries,
            'last_update': time.time()
        }

    def fetch_feed_entries(self, url, force_refresh=False):
        """抓取指定 RSS feed 的文章列表

        Args:
            url (str): RSS feed URL
            force_refresh (bool): 是否強制重新抓取(忽略快取)

        Returns:
            list: 文章列表 [{'title': str, 'link': str, 'published': str, 'summary': str}]
        """
        # 檢查快取
        if not force_refresh:
            cached_entries = self._get_cached_entries(url)
            if cached_entries is not None:
                return cached_entries

        # 抓取 feed
        try:
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                return []

            entries = []
            for entry in feed.entries[:RSS_MAX_ENTRIES]:
                entries.append(self._parse_feed_entry(entry))

            self._update_cache(url, entries)
            return entries

        except Exception as e:
            print(f"抓取 RSS feed 失敗: {e}")
            return []

    def fetch_all_feeds(self, force_refresh=False):
        """抓取所有訂閱的 RSS feeds（同步版本，保留向後相容）

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

    def _fetch_single_feed_with_info(self, url, feed_info, force_refresh):
        """抓取單一 RSS feed（內部方法，用於多執行緒）

        Args:
            url (str): RSS feed URL
            feed_info (dict): feed 資訊 {'title': str, 'added_time': float}
            force_refresh (bool): 是否強制重新抓取

        Returns:
            tuple: (url, result_dict)
        """
        try:
            entries = self.fetch_feed_entries(url, force_refresh)
            result = {
                'title': feed_info['title'],
                'entries': entries,
                'error': None if entries else '無法抓取內容'
            }
            logger.info(f"成功抓取 RSS: {feed_info['title']} ({len(entries)} 篇文章)")
            return (url, result)
        except Exception as e:
            logger.error(f"抓取 RSS 失敗: {feed_info['title']} - {str(e)}")
            result = {
                'title': feed_info['title'],
                'entries': [],
                'error': str(e)
            }
            return (url, result)

    def fetch_all_feeds_async(self, force_refresh=False, progress_callback=None):
        """並行抓取所有訂閱的 RSS feeds（優化版本）

        Args:
            force_refresh (bool): 是否強制重新抓取
            progress_callback (callable): 進度回調函數 callback(url, title, current, total)

        Returns:
            dict: {url: {'title': str, 'entries': list, 'error': str}}
        """
        feeds = self.get_all_feeds()
        total = len(feeds)

        if total == 0:
            logger.info("沒有訂閱的 RSS feeds")
            return {}

        logger.info(f"開始並行抓取 {total} 個 RSS feeds")
        result = {}

        # 提交所有任務到執行緒池
        futures = {
            self.executor.submit(
                self._fetch_single_feed_with_info,
                url,
                feed_info,
                force_refresh
            ): (url, feed_info)
            for url, feed_info in feeds.items()
        }

        # 收集結果
        current = 0
        for future in as_completed(futures, timeout=60):
            url, feed_info = futures[future]
            current += 1

            try:
                url_result, feed_result = future.result(timeout=30)
                result[url_result] = feed_result

                # 呼叫進度回調
                if progress_callback:
                    progress_callback(
                        url=url,
                        title=feed_info['title'],
                        current=current,
                        total=total
                    )

            except Exception as e:
                logger.error(f"處理 RSS future 時發生錯誤: {feed_info['title']} - {str(e)}")
                result[url] = {
                    'title': feed_info['title'],
                    'entries': [],
                    'error': f'執行緒錯誤: {str(e)}'
                }

        logger.info(f"完成抓取 {len(result)}/{total} 個 RSS feeds")
        return result

    def clear_cache(self):
        """清除所有快取"""
        self.cache = {}

    def shutdown(self):
        """關閉執行緒池，釋放資源"""
        logger.info("正在關閉 RSS Manager 執行緒池...")
        self.executor.shutdown(wait=True)
        logger.info("RSS Manager 執行緒池已關閉")

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
