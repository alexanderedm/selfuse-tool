"""專案常數定義"""
import os
from pathlib import Path

# ==================== 路徑配置 ====================

# 預設音樂根目錄 (可透過設定修改)
DEFAULT_MUSIC_ROOT_PATH = os.path.join(str(Path.home()), 'Music', 'AudioSwitcher')

# 預設下載目錄 (YouTube 音樂下載)
DEFAULT_DOWNLOAD_PATH = os.path.join(str(Path.home()), 'Downloads', 'AudioSwitcher')

# 日誌目錄
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# 配置檔案路徑
CONFIG_FILE = 'config.json'

# ==================== RSS 配置 ====================

# RSS 快取超時時間 (秒)
RSS_CACHE_TIMEOUT = 300  # 5 分鐘

# RSS 最大文章數
RSS_MAX_ENTRIES = 50

# ==================== 音樂播放器配置 ====================

# 預設音量 (0-100)
DEFAULT_MUSIC_VOLUME = 70

# 專輯封面最大尺寸 (像素)
ALBUM_COVER_MAX_SIZE = 250

# ==================== YouTube 下載器配置 ====================

# yt-dlp 搜尋超時時間 (秒)
YTDLP_SEARCH_TIMEOUT = 45

# yt-dlp 下載超時時間 (秒)
YTDLP_DOWNLOAD_TIMEOUT = 600  # 10 分鐘

# yt-dlp 最大搜尋結果數
YTDLP_MAX_SEARCH_RESULTS = 10

# ==================== UI 主題配置 ====================

# 深色主題顏色配置
THEME_COLORS = {
    'bg_color': '#1e1e1e',        # 深灰背景
    'card_bg': '#2d2d2d',          # 卡片背景
    'accent_color': '#0078d4',     # 藍色強調
    'text_color': '#e0e0e0',       # 淺色文字
    'text_secondary': '#a0a0a0',   # 次要文字
    'header_bg': '#0d47a1',        # 深藍標題
    'input_bg': '#353535',         # 輸入框背景
    'hover_bg': '#505050',         # 懸停背景
}

# Treeview 行高
TREEVIEW_ROW_HEIGHT = 30

# ==================== 應用程式資訊 ====================

APP_NAME = 'AudioSwitcher'
APP_VERSION = '2.6.0'
APP_AUTHOR = 'Your Name'

# ==================== 其他常數 ====================

# 托盤圖示尺寸
TRAY_ICON_SIZE = 64

# 圖示顏色映射
ICON_COLORS = {
    'device_a': 'blue',
    'device_b': 'green',
    'default': 'gray'
}

# 音訊裝置角色
DEVICE_ROLES = {
    'CONSOLE': 0,
    'MULTIMEDIA': 1,
    'COMMUNICATIONS': 2
}
