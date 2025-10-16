# 更新日誌

所有重要的專案變更都會記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
版本編號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

---

## [未發布]

### 新增 (Added)
- **CustomTkinter UI 現代化升級** (2025-10-16 - Overnight Development)
  - 遷移核心視窗到 CustomTkinter，獲得現代化圓角 UI
  - 遷移完成的模組：
    - `music_window.py` - 主視窗（ctk.CTk）
    - `music_header_view.py` - 頂部按鈕區域（圓角按鈕，更大按鈕設計）
    - `music_search_view.py` - 搜尋框（圓角輸入框 + placeholder）
    - `music_playback_view.py` - 播放控制區域（圓角框架 + 現代化控制元件）
  - 播放控制區域升級：
    - 大圓角主框架（corner_radius=15）
    - 播放按鈕：75x75px 大圓形按鈕（最顯眼）
    - 上一首/下一首：55x55px 中等圓角按鈕
    - 進度條：使用 CTkSlider 可拖動滑桿（粗 20px）
    - 音量滑桿：現代化 CTkSlider（藍色主題）
    - 專輯封面：圓角框架 230x230px
    - 歌曲資訊：圓角資訊卡片
    - 播放模式：圓角按鈕，不同模式不同顏色
  - 所有按鈕使用圓角設計（corner_radius=10-38）
  - 所有框架使用透明背景或圓角設計
  - CustomTkinter 自動管理深色主題
  - 移除舊的 ttkbootstrap 測試檔案
  - 15 個單元測試全部通過
  - flake8 零錯誤
  - 待遷移：library_view、lyrics_view、dialogs、windows

- **Discord Rich Presence 整合** (2025-10-16)
  - 在 Discord 顯示當前播放的音樂資訊
  - 顯示歌曲名稱、藝術家、專輯資訊
  - 顯示播放進度條和總時長
  - 支援專輯封面顯示（透過 URL）
  - 自動連接 Discord，播放時即時更新狀態
  - 可透過環境變數 `DISCORD_CLIENT_ID` 設定 Application ID
  - 新增模組：`discord_presence.py`（17 個測試全部通過）

- **多來源音樂元數據補全** (2025-10-16)
  - 整合多個音樂元數據來源，提高補全成功率
  - 支援 YouTube Music API（ytmusicapi）
  - 支援 iTunes API
  - 未來支援 Spotify API（框架已建立）
  - 智慧 Fallback 機制：YouTube Music → iTunes → Spotify
  - 自動選擇最高解析度封面圖片
  - 新增模組：`music_metadata_multi_source.py`（16 個測試全部通過）
  - 依賴：ytmusicapi >= 1.0.0

### 變更 (Changed)
- **music_window.py 整合 Discord Rich Presence**
  - 播放歌曲時自動更新 Discord 狀態
  - 應用程式關閉時自動清除 Discord 狀態
  - 支援透過 config.json 的 `discord_rpc_enabled` 設定啟用/停用

### 修復 (Fixed)
- 修復等化器對話框導致主視窗背景變白的問題（回退 ttkbootstrap）
  - 原因：ttkbootstrap 會影響全域 tkinter 主題，需整個應用遷移才能使用
  - 解決：改用原生 tkinter + 手動深色主題配色（#1e1e1e 背景、#2d2d2d 卡片）
  - Commits: 79eca1c, 3baaeee

### 技術細節 (Technical)
- 新增依賴套件：
  - pypresence >= 4.2.0（Discord Rich Presence）
  - ytmusicapi >= 1.0.0（YouTube Music API）
  - chromadb >= 0.4.0（RAG 助理，待實作）
  - openai >= 1.0.0（RAG 助理，待實作）
  - langchain >= 0.1.0（RAG 助理，待實作）
  - python-dotenv >= 1.0.0（環境變數管理）
- 新增環境變數範本檔案：`.env.example`
- 總測試數量：677 → 708 個測試（+33 個）

---

## [1.0.0] - 2025-10-15

### 新增 (Added)
- **即時等化器功能**
  - 10 頻段參數等化器（60Hz ~ 16kHz），增益範圍 -12dB 到 +12dB
  - 8 種預設模式（流行、搖滾、古典、爵士、人聲、重低音、柔和、自定義）
  - 調整滑桿立即生效，無需重新載入音樂
  - 新增模組：EqualizerFilter、AudioProcessor、AudioPlayer
- **音樂播放器架構升級**
  - 新增 AudioPlayer 模組（基於 sounddevice + librosa）
  - 支援即時音訊處理和等化器效果
  - 向後相容 pygame.mixer（自動 fallback）
- **歌詞顯示功能**
  - 支援 LRC 格式歌詞解析，自動同步高亮當前播放歌詞
  - 點擊歌詞行跳轉播放，自動滾動到當前位置
  - 自動從 YouTube 字幕下載並轉換為 LRC 格式
- **托盤更新日誌功能**
  - 系統托盤新增「更新日誌」選項，支援 Markdown 格式渲染
- **自動補全音樂資訊**
  - 從 iTunes API 自動抓取封面/藝術家/專輯
  - 下載高解析度封面（600x600），背景執行不阻塞 UI
- **UI 主題系統**
  - 統一的深色主題配色管理（ui_theme.py）
  - Spotify 風格配色方案，支援懸停效果

### 變更 (Changed)
- **music_window.py 模組化重構**
  - 從 1,548 行減少到 774 行（-50%）
  - 抽離 11 個專門模組：MusicLibraryView、MusicSearchView、MusicHeaderView、MusicPlaybackView、MusicPlaylistDialog、MusicDownloadDialog、MusicHistoryDialog、MusicMetadataFetcher、MusicSongActions、MusicFolderActions、MusicFileManager
  - 測試覆蓋率從 20% 提升到 68%
- **程式碼複雜度優化**
  - 平均複雜度從 3.03 降至 2.72（A 級）
  - 重構 10 個高複雜度函數（CC > 8）
  - xenon 違規從 5 降至 1（已消除 D 級違規）
  - 整合複雜度檢查到 Git pre-commit hooks
- **測試覆蓋大幅提升**
  - 總測試數：393 → 677（+284 個測試）
  - 測試通過率：98.6%
  - 新增測試模組：test_audio_player.py、test_equalizer_filter.py、test_audio_processor.py、test_music_library_view.py、test_music_search_view.py、test_music_header_view.py、test_youtube_downloader.py、test_rss_window.py 等

### 修復 (Fixed)
- 修復設定視窗裝置選擇器顯示問題
- 修復 MusicMetadataFetcher JSON 更新路徑驗證 Bug（WindowsPath('.') has an empty name）
- 修復 RSS 文章無法顯示問題（補充 set_entries 方法）
- 修復 ConfigManager 缺少通用 get/set 方法
- 修復等化器對話框測試失敗（Mock 設定問題）
- 修復 pre-commit hook xenon 檢查 bug

### 文檔 (Documentation)
- 新增 `PROJECT_HEALTH_REPORT.md` - 專案健康度分析報告（整體評級 A 級）
- 新增 `CODE_COMPLEXITY_REPORT.md` - 程式碼複雜度報告
- 新增 `EQUALIZER_INTEGRATION_GUIDE.md` - 等化器整合指南
- 更新 README.md - 新增等化器和歌詞功能說明

### 技術細節 (Technical)
- 整合 radon 和 xenon 複雜度分析工具
- 建立 `.radon.cfg` 配置檔案
- 所有模組達到 flake8 零錯誤
- 平均可維護性指數 > 65（A 級）
- 新增依賴：sounddevice、numpy、scipy、librosa、soundfile

### 專案統計
- **總程式碼行數**: ~15,000 行
- **總測試數量**: 677 個測試
- **測試通過率**: 98.6% (667/677)
- **平均複雜度**: CC=2.72（A 級）
- **測試覆蓋率**: 92% (35/38 檔案)
- **健康度評級**: A 級（優秀）

---

## 格式說明

- `Added` - 新增功能
- `Changed` - 現有功能的變更
- `Deprecated` - 即將移除的功能
- `Removed` - 已移除的功能
- `Fixed` - Bug 修復
- `Security` - 安全性修復
- `Documentation` - 文檔更新
- `Technical` - 技術改進（不影響使用者體驗）
