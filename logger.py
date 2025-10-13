"""日誌系統模組"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class AppLogger:
    """應用程式日誌管理器"""

    def __init__(self, log_dir='logs', log_file='app.log', max_bytes=5*1024*1024, backup_count=3):
        """初始化日誌系統

        Args:
            log_dir (str): 日誌目錄
            log_file (str): 日誌檔名
            max_bytes (int): 單個日誌檔案最大大小(預設5MB)
            backup_count (int): 保留的備份檔案數量(預設3個)
        """
        self.log_dir = log_dir
        self.log_file = log_file

        # 建立日誌目錄
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 完整日誌路徑
        log_path = os.path.join(log_dir, log_file)

        # 清空日誌檔案(每次啟動時重新開始)
        if os.path.exists(log_path):
            try:
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.truncate()
            except Exception as e:
                print(f"無法清空日誌檔案: {e}")

        # 設定日誌記錄器
        self.logger = logging.getLogger('AudioSwitcher')
        self.logger.setLevel(logging.DEBUG)

        # 清除現有的處理器(避免重複)
        self.logger.handlers.clear()

        # 檔案處理器 - 使用輪轉機制
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 設定格式
        detailed_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '[%(levelname)s] %(message)s'
        )

        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(console_formatter)

        # 加入處理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # 記錄啟動訊息
        self.info("=" * 80)
        self.info(f"應用程式啟動 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info("=" * 80)

    def debug(self, message):
        """除錯訊息"""
        self.logger.debug(message)

    def info(self, message):
        """一般資訊"""
        self.logger.info(message)

    def warning(self, message):
        """警告訊息"""
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        """錯誤訊息

        Args:
            message (str): 錯誤訊息
            exc_info (bool): 是否包含例外堆疊追蹤
        """
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message, exc_info=False):
        """嚴重錯誤"""
        self.logger.critical(message, exc_info=exc_info)

    def exception(self, message):
        """記錄例外(自動包含堆疊追蹤)"""
        self.logger.exception(message)

    def log_function_call(self, func_name, *args, **kwargs):
        """記錄函數呼叫"""
        args_str = ', '.join([str(arg) for arg in args])
        kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
        params = ', '.join(filter(None, [args_str, kwargs_str]))
        self.debug(f"呼叫函數: {func_name}({params})")

    def log_window_event(self, window_name, event):
        """記錄視窗事件"""
        self.info(f"[視窗事件] {window_name}: {event}")

    def log_audio_event(self, event, device_name=None):
        """記錄音訊事件"""
        if device_name:
            self.info(f"[音訊事件] {event} - 裝置: {device_name}")
        else:
            self.info(f"[音訊事件] {event}")

    def log_rss_event(self, event, url=None):
        """記錄 RSS 事件"""
        if url:
            self.info(f"[RSS事件] {event} - URL: {url}")
        else:
            self.info(f"[RSS事件] {event}")


# 建立全域日誌實例
logger = AppLogger()
