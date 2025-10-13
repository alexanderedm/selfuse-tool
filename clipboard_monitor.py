"""剪貼簿監控模組"""
import threading
import time
import pyperclip


class ClipboardMonitor:
    """監控剪貼簿變化的類別"""

    def __init__(self, on_rss_detected=None, check_interval=1.0):
        """初始化剪貼簿監控器

        Args:
            on_rss_detected (callable): 偵測到 RSS 連結時的回調函數,接收 url 參數
            check_interval (float): 檢查間隔(秒),預設 1.0 秒
        """
        self.on_rss_detected = on_rss_detected
        self.check_interval = check_interval
        self.last_clipboard = ""
        self.running = False
        self.thread = None

    def _is_url(self, text):
        """檢查文字是否為 URL

        Args:
            text (str): 要檢查的文字

        Returns:
            bool: 是否為 URL
        """
        if not text or not isinstance(text, str):
            return False

        text = text.strip()

        # 基本 URL 格式檢查
        if text.startswith('http://') or text.startswith('https://'):
            # 確保沒有換行或空白(單一 URL)
            if '\n' in text or ' ' in text:
                return False
            # 確保長度合理
            if len(text) > 2000:
                return False
            return True

        return False

    def _check_clipboard(self):
        """檢查剪貼簿內容"""
        try:
            # 取得剪貼簿內容
            current_clipboard = pyperclip.paste()

            # 如果內容改變且是 URL
            if current_clipboard != self.last_clipboard:
                self.last_clipboard = current_clipboard

                if self._is_url(current_clipboard):
                    # 觸發回調函數
                    if self.on_rss_detected:
                        self.on_rss_detected(current_clipboard.strip())

        except Exception as e:
            # 忽略剪貼簿錯誤(例如剪貼簿被其他程式佔用)
            pass

    def _monitor_loop(self):
        """監控循環"""
        while self.running:
            self._check_clipboard()
            time.sleep(self.check_interval)

    def start(self):
        """啟動監控"""
        if self.running:
            return

        self.running = True

        # 初始化剪貼簿內容
        try:
            self.last_clipboard = pyperclip.paste()
        except:
            self.last_clipboard = ""

        # 啟動監控執行緒
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """停止監控"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None

    def set_callback(self, callback):
        """設定回調函數

        Args:
            callback (callable): 偵測到 RSS 連結時的回調函數
        """
        self.on_rss_detected = callback
