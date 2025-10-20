"""設定檔管理模組"""
import json
import os
import threading
from src.core.constants import DEFAULT_MUSIC_VOLUME, DEFAULT_MUSIC_ROOT_PATH


class ConfigManager:
    """管理應用程式設定的類別"""

    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = self._load_config()

        # 批量寫入機制
        self.save_timer = None
        self.save_delay = 1.0  # 1 秒後寫入
        self.save_lock = threading.Lock()

    def _load_config(self):
        """載入設定檔

        Returns:
            dict: 設定資料
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"載入設定檔失敗: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()

    def _get_default_config(self):
        """取得預設設定

        Returns:
            dict: 預設設定
        """
        return {
            'device_a': None,
            'device_b': None,
            'current_device': None,
            'auto_start': False,
            'usage_stats': {},  # 格式: {'device_id': {'name': 'xxx', 'total_seconds': 0, 'switch_count': 0}}
            'last_switch_time': None,
            'rss_feeds': {},  # 格式: {'url': {'title': 'xxx', 'added_time': timestamp}}
            'music_volume': DEFAULT_MUSIC_VOLUME,  # 音樂播放器音量 (0-100)
            'music_root_path': DEFAULT_MUSIC_ROOT_PATH  # 音樂根目錄
        }

    def save_config(self):
        """儲存設定檔（立即寫入，用於程式關閉時）

        Returns:
            bool: 是否成功
        """
        return self._perform_save()

    def _schedule_save(self):
        """排程延遲儲存（批量寫入優化）"""
        with self.save_lock:
            # 取消現有計時器
            if self.save_timer and self.save_timer.is_alive():
                self.save_timer.cancel()

            # 建立新的延遲計時器
            self.save_timer = threading.Timer(
                self.save_delay,
                self._perform_save
            )
            self.save_timer.daemon = True
            self.save_timer.start()

    def _perform_save(self):
        """執行實際的儲存操作

        Returns:
            bool: 是否成功
        """
        try:
            with self.save_lock:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"儲存設定檔失敗: {e}")
            return False

    def get_device_a(self):
        """取得裝置 A"""
        return self.config.get('device_a')

    def get_device_b(self):
        """取得裝置 B"""
        return self.config.get('device_b')

    def set_device_a(self, device_info):
        """設定裝置 A

        Args:
            device_info (dict): {'id': str, 'name': str}
        """
        self.config['device_a'] = device_info
        self._schedule_save()

    def set_device_b(self, device_info):
        """設定裝置 B

        Args:
            device_info (dict): {'id': str, 'name': str}
        """
        self.config['device_b'] = device_info
        self._schedule_save()

    def get_current_device(self):
        """取得當前裝置"""
        return self.config.get('current_device')

    def set_current_device(self, device_info):
        """設定當前裝置

        Args:
            device_info (dict): {'id': str, 'name': str}
        """
        self.config['current_device'] = device_info
        self._schedule_save()

    def get_auto_start(self):
        """取得開機自啟動設定"""
        return self.config.get('auto_start', False)

    def set_auto_start(self, enabled):
        """設定開機自啟動

        Args:
            enabled (bool): 是否啟用
        """
        self.config['auto_start'] = enabled
        self._schedule_save()

        # 實際設定 Windows 註冊表
        self._set_windows_auto_start(enabled)

    def _set_windows_auto_start(self, enabled):
        """設定 Windows 開機自啟動

        Args:
            enabled (bool): 是否啟用
        """
        import winreg
        import sys

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "AudioSwitcher"

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)

            if enabled:
                # 取得執行檔路徑
                if getattr(sys, 'frozen', False):
                    # 打包後的 exe
                    app_path = sys.executable
                else:
                    # 開發環境
                    app_path = f'pythonw "{os.path.abspath(sys.argv[0])}"'

                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            else:
                # 移除自啟動
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass

            winreg.CloseKey(key)
        except Exception as e:
            print(f"設定開機自啟動失敗: {e}")

    def record_device_usage(self, device_info):
        """記錄裝置使用統計

        Args:
            device_info (dict): {'id': str, 'name': str}
        """
        import time

        if not device_info:
            return

        current_time = time.time()

        # 初始化 usage_stats 如果不存在
        if 'usage_stats' not in self.config:
            self.config['usage_stats'] = {}

        device_id = device_info['id']

        # 如果是新裝置,初始化統計資料
        if device_id not in self.config['usage_stats']:
            self.config['usage_stats'][device_id] = {
                'name': device_info['name'],
                'total_seconds': 0,
                'switch_count': 0
            }

        # 更新切換次數
        self.config['usage_stats'][device_id]['switch_count'] += 1

        # 計算上一個裝置的使用時間
        if 'last_switch_time' in self.config and self.config['last_switch_time']:
            last_device = self.config.get('current_device')
            if last_device and last_device['id'] in self.config['usage_stats']:
                elapsed = current_time - self.config['last_switch_time']
                self.config['usage_stats'][last_device['id']]['total_seconds'] += elapsed

        # 更新最後切換時間
        self.config['last_switch_time'] = current_time

        self._schedule_save()

    def get_usage_stats(self):
        """取得使用統計

        Returns:
            dict: 使用統計資料
        """
        if 'usage_stats' not in self.config:
            self.config['usage_stats'] = {}
        return self.config['usage_stats']

    def update_current_usage(self):
        """更新當前裝置的使用時間(在程式關閉前呼叫)"""
        import time

        if 'last_switch_time' not in self.config or not self.config['last_switch_time']:
            return

        current_device = self.config.get('current_device')
        if not current_device:
            return

        device_id = current_device['id']
        if device_id not in self.config.get('usage_stats', {}):
            return

        elapsed = time.time() - self.config['last_switch_time']
        self.config['usage_stats'][device_id]['total_seconds'] += elapsed
        self.config['last_switch_time'] = time.time()

        self.save_config()

    def get_rss_feeds(self):
        """取得 RSS 訂閱列表

        Returns:
            dict: RSS 訂閱 {url: {'title': str, 'added_time': float}}
        """
        if 'rss_feeds' not in self.config:
            self.config['rss_feeds'] = {}
        return self.config['rss_feeds']

    def set_rss_feeds(self, feeds):
        """設定 RSS 訂閱列表

        Args:
            feeds (dict): RSS 訂閱字典
        """
        self.config['rss_feeds'] = feeds
        self._schedule_save()

    # ==================== RSS 文章狀態管理 ====================

    def get_read_articles(self):
        """取得已讀文章列表

        Returns:
            list: 已讀文章 ID 列表
        """
        if 'read_articles' not in self.config:
            self.config['read_articles'] = []
        return self.config['read_articles']

    def set_read_articles(self, articles):
        """設定已讀文章列表

        Args:
            articles (list): 文章 ID 列表
        """
        self.config['read_articles'] = articles
        self._schedule_save()

    def get_favorite_articles(self):
        """取得收藏文章

        Returns:
            dict: {article_id: article_data}
        """
        if 'favorite_articles' not in self.config:
            self.config['favorite_articles'] = {}
        return self.config['favorite_articles']

    def set_favorite_articles(self, favorites):
        """設定收藏文章

        Args:
            favorites (dict): 收藏文章字典
        """
        self.config['favorite_articles'] = favorites
        self._schedule_save()

    def get_feed_categories(self):
        """取得 RSS 分類

        Returns:
            dict: {category_name: [feed_url1, feed_url2, ...]}
        """
        if 'feed_categories' not in self.config:
            self.config['feed_categories'] = {'未分類': []}
        return self.config['feed_categories']

    def set_feed_categories(self, categories):
        """設定 RSS 分類

        Args:
            categories (dict): 分類字典
        """
        self.config['feed_categories'] = categories
        self._schedule_save()

    def add_feed_to_category(self, feed_url, category):
        """將 RSS 加入分類

        Args:
            feed_url (str): RSS URL
            category (str): 分類名稱
        """
        categories = self.get_feed_categories()

        # 從所有分類中移除此 feed
        for cat_feeds in categories.values():
            if feed_url in cat_feeds:
                cat_feeds.remove(feed_url)

        # 加入新分類
        if category not in categories:
            categories[category] = []
        if feed_url not in categories[category]:
            categories[category].append(feed_url)

        self.set_feed_categories(categories)

    def get_feed_category(self, feed_url):
        """取得 RSS 的分類

        Args:
            feed_url (str): RSS URL

        Returns:
            str: 分類名稱,如果沒有則回傳 '未分類'
        """
        categories = self.get_feed_categories()
        for category, feeds in categories.items():
            if feed_url in feeds:
                return category
        return '未分類'

    # ==================== 音樂播放器設定 ====================

    def get_music_volume(self):
        """取得音樂播放器音量

        Returns:
            int: 音量 (0-100)
        """
        if 'music_volume' not in self.config:
            self.config['music_volume'] = DEFAULT_MUSIC_VOLUME
        return self.config['music_volume']

    def set_music_volume(self, volume):
        """設定音樂播放器音量

        Args:
            volume (int): 音量 (0-100)
        """
        self.config['music_volume'] = max(0, min(100, int(volume)))
        self._schedule_save()

    # ==================== 通用配置存取方法 ====================

    def get(self, key, default=None):
        """取得配置值(通用方法)

        Args:
            key (str): 配置鍵名
            default: 預設值(如果鍵不存在)

        Returns:
            配置值或預設值
        """
        return self.config.get(key, default)

    def set(self, key, value):
        """設定配置值(通用方法)

        Args:
            key (str): 配置鍵名
            value: 配置值
        """
        self.config[key] = value
        self._schedule_save()
