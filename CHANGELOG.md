# 更新日誌

所有重要的專案變更都會記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
版本編號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

---

## [未發布]

### 修復 (Fixed)
- 修復等化器對話框導致主視窗背景變白的問題（回退 ttkbootstrap）
  - 原因：ttkbootstrap 會影響全域 tkinter 主題，需整個應用遷移才能使用
  - 解決：改用原生 tkinter + 手動深色主題配色（#1e1e1e 背景、#2d2d2d 卡片）
  - Commits: 79eca1c, 3baaeee

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
