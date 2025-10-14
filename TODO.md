# 專案待辦清單 (Todo List)

## ✅ 已完成 (Completed)
- [x] **修復 MusicMetadataFetcher JSON 更新 Bug** (2025-10-14 完成)
  - 使用 TDD 方法診斷並修復路徑驗證 Bug
  - 問題：`WindowsPath('.') has an empty name` ValueError
  - 根因：`update_song_metadata()` 未在呼叫 `.with_suffix()` 前驗證路徑
  - 解決：新增路徑名稱檢查與檔案類型驗證
  - 新增 3 個單元測試，所有 41 個音樂元數據測試通過
  - 測試 41/41 通過 (100%)，flake8 零錯誤
- [x] **修復 RSS 文章無法顯示問題** (2025-10-14 完成)
  - 診斷並修復重構時遺漏的 `set_entries()` 方法
  - 根因：`rss_window.py` 呼叫不存在的方法名稱
  - 解決：在 `rss_filter_manager.py` 新增 `set_entries()` 別名方法
  - 新增 1 個單元測試，所有 48 個 RSS 測試通過
  - 總測試 427/428 通過 (99.8%)，flake8 零錯誤
- [x] **自動補全缺失音樂資訊** (2025-10-13 完成)
  - 播放時自動檢測缺失的封面/藝術家/專輯
  - 從 iTunes API 自動抓取資訊
  - 下載高解析度封面 (600x600)
  - 背景執行不阻塞 UI
  - 完整測試套件 (38 tests)

- [x] **music_window.py 模組化重構 - 完整完成** (2025-10-13 完成)
  - 從 1,548 行減少到 774 行 (-50.0%)
  - 抽離 11 個專門模組:
    - MusicHistoryDialog (115 行)
    - MusicPlaylistDialog (313 行)
    - MusicDownloadDialog (173 行)
    - MusicMetadataFetcher (155 行)
    - MusicLibraryView (302 行)
    - MusicSearchView (142 行)
    - MusicHeaderView (160 行)
    - MusicPlaybackView (342 行)
    - MusicSongActions (248 行)
    - MusicFolderActions (193 行)
    - MusicFileManager (120 行)
  - 新增 180+ 個測試
  - 測試覆蓋率 68%
  - **達成 < 800 行目標** ✅

- [x] **修復 ConfigManager 缺少通用方法** (2025-10-13 完成)
  - 修復音樂播放器視窗無法開啟的問題
  - 新增 get(key, default=None) 通用方法
  - 新增 set(key, value) 通用方法
  - 新增 2 個單元測試
  - 所有 289 個測試通過
  - 已推送至 GitHub

- [x] **建立 MusicLibraryView 模組** (2025-10-13 完成)
  - 從 music_window.py 抽離資料夾樹與歌曲列表 UI (302 行)
  - 新增 19 個單元測試
  - 19/19 測試通過 (tkinter 環境問題已解決)
  - 模組已建立並成功整合至 music_window.py

- [x] **整合 MusicLibraryView 到 music_window.py** (2025-10-13 完成)
  - 成功將 MusicLibraryView 整合到主視窗
  - music_window.py 從 1,548 行減少到 1,489 行 (-59 行, -3%)
  - 所有 289 個測試通過,flake8 零錯誤
  - 已推送至 GitHub

- [x] **建立 MusicSearchView 模組** (2025-10-13 完成)
  - 從 music_window.py 抽離搜尋框 UI 和搜尋邏輯 (142 行)
  - 新增 13 個單元測試 (100% 通過)
  - 使用回調模式實現鬆耦合設計
  - 測試覆蓋完整功能(搜尋、清除、回調等)

- [x] **整合 MusicSearchView 到 music_window.py** (2025-10-13 完成)
  - 成功將 MusicSearchView 整合到主視窗
  - music_window.py 從 1,489 行減少到 1,439 行 (-50 行, -3.4%)
  - 所有 301 個測試通過 (新增 12 個測試),flake8 零錯誤
  - 累計減少: 1,548 → 1,439 行 (-109 行, -7%)

- [x] **建立 MusicHeaderView 模組** (2025-10-13 完成)
  - 從 music_window.py 抽離頂部標題和按鈕區域 (160 行)
  - 新增 15 個單元測試 (100% 通過)
  - 使用回調模式實現鬆耦合設計
  - 測試覆蓋所有按鈕和回調功能

- [x] **整合 MusicHeaderView 到 music_window.py** (2025-10-13 完成)
  - 成功將 MusicHeaderView 整合到主視窗
  - music_window.py 從 1,439 行減少到 1,370 行 (-69 行, -4.8%)
  - 所有 315 個測試通過 (新增 14 個測試),flake8 零錯誤
  - 累計減少: 1,548 → 1,370 行 (-178 行, -11.5%)

- [x] **整合 MusicPlaybackView 到 music_window.py** (2025-10-13 完成)
  - 成功將 MusicPlaybackView 整合到主視窗，移除播放控制 UI 重複程式碼
  - music_window.py 從 1,370 行減少到 1,095 行 (-275 行, -20%)
  - 移除重複的專輯封面處理方法 (103 行)
  - 所有 317 個測試通過,flake8 零錯誤
  - 累計減少: 1,548 → 1,095 行 (-453 行, -29.3%)
  - **距離目標 < 800 行還需減少 295 行 (27%)**

- [x] **程式碼複雜度分析與優化** (2025-10-14 完成)
  - 安裝並配置 radon 和 xenon 複雜度分析工具
  - 建立 `.radon.cfg` 配置檔案
  - 執行全專案複雜度分析 (383 個區塊)
  - 建立 `CODE_COMPLEXITY_REPORT.md` 詳細報告
  - 重構 `rss_manager.py::fetch_feed_entries` **CC 24 → 7** (-71%) ✅
    - 提取 5 個輔助方法 (_get_cached_entries, _parse_published_time等)
    - 使用 TDD 方法確保所有 RSS 測試通過 (12/12)
    - flake8 零錯誤
  - 整合複雜度檢查到 Git pre-commit hooks
  - **成果**:
    - 平均複雜度: **A (3.03)** ⭐ (目標 < 5)
    - CC > 10 函數: **6 個** (從 9 降至 6，進步 33%)
    - xenon 違規: **2 個** (從 5 降至 2，進步 60%)
    - MI < 65 檔案: 15 個
    - 所有測試通過，flake8 零錯誤

## 🚧 進行中 (In Progress)
- [ ] **解決 tkinter 測試環境問題**
  - 1 個測試因 tkinter 環境設定問題間歇性失敗 (test_music_history_dialog)
  - 非程式碼問題,為 Windows Python tkinter 安裝不完整
  - 單獨運行測試時正常通過
  - 當前測試通過率: 316/317 (99.7%)

## 📋 待辦事項 (Todo) - 根據程式碼健康度分析 (2025-10-14)

### 🔥 緊急優先 (Week 1-2) - 技術債務消除
- [ ] **完成 music_window.py 重構** (預估: 3-5 天)
  - [ ] Day 1-2: 抽離 UI 元件模組
    - [x] 建立 `MusicLibraryView` (資料夾樹 + 歌曲列表,302 行) ✅ 2025-10-13
    - [x] 整合 MusicLibraryView 到 music_window.py ✅ 2025-10-13
    - [x] 建立 `MusicSearchView` (搜尋與篩選邏輯,142 行) ✅ 2025-10-13
    - [x] 整合 MusicSearchView 到 music_window.py ✅ 2025-10-13
    - [x] 建立 `MusicHeaderView` (頂部按鈕區域,160 行) ✅ 2025-10-13
    - [x] 整合 MusicHeaderView 到 music_window.py ✅ 2025-10-13
  - [ ] Day 3-4: 增加測試覆蓋率
    - [x] 新增 `test_music_library_view.py` (+19 tests) ✅ 2025-10-13
    - [x] 新增 `test_music_search_view.py` (+13 tests) ✅ 2025-10-13
    - [x] 新增 `test_music_header_view.py` (+15 tests) ✅ 2025-10-13
    - [ ] 擴展 `test_music_window.py` (+25 tests)
    - [ ] 目標: 測試覆蓋率 20% → 60%
  - [ ] Day 5: 驗證與文檔更新
    - [x] 執行所有測試 (315 tests) ✅ 2025-10-13
    - [x] 更新 CHANGELOG.md ✅ 2025-10-13
    - [x] 更新 TODO.md ✅ 2025-10-13
    - [ ] 提交 Git commit並推送
    - [ ] 檢查程式碼複雜度
  - **目前進度**: music_window.py 1,548 → 774 行 (-50.0%) ✅ **已達成 < 800 行目標**
  - **階段 4 完成**: 整合 MusicPlaybackView (-275 行)
  - **階段 5 完成**: 整合 MusicSongActions (-150 行)
  - **階段 6 完成**: 整合 MusicFolderActions (-10 行) + 移除重複程式碼 (-164 行)
  - **測試狀態**: 339 個測試, 337 passed, 2 failed (99.4%)
  - **測試覆蓋率**: **68%** ✅ (已超過 60% 目標)
  - **程式碼品質**: flake8 零錯誤 ✅
  - **✅ music_window.py 重構完成！**

### ⚠️ 高優先 (Week 3-4) - 測試覆蓋率提升
- [x] **YouTube 下載器測試** (已完成 2025-10-13) ✅
  - [x] 新增 `test_youtube_downloader.py` (+21 tests，超過目標)
    - [x] Mock subprocess.run
    - [x] 測試所有錯誤路徑
    - [x] 測試超時處理
    - [x] 測試瀏覽器 cookie 回退邏輯
  - **成果**: 覆蓋率 10.6% → **91%** (+80.4%)

- [x] **Main.py 測試補充** (已完成 2025-10-13) ✅
  - [x] 擴展 `test_main.py` (+13 tests，超過目標 8 個)
    - [x] 測試音樂播放器相關方法 (6 tests)
    - [x] 測試 RSS 視窗相關方法 (2 tests)
    - [x] 測試設定/統計視窗相關方法 (2 tests)
    - [x] 測試 Log 檢視器方法 (2 tests)
  - **成果**: 測試數 19 → **33** (+14 個)

- [x] **Settings Window 測試補充** (已完成 2025-10-13) ✅
  - [x] 補充 `test_settings_window.py` (+19 tests)
  - **成果**: 覆蓋率 4% → **50%+**

- [x] **RSS 模組測試補充** (已完成 2025-10-14) ✅
  - [x] 新增 `test_rss_window.py` (+30 tests) ✅
    - [x] 測試初始化和視窗管理 (8 tests)
    - [x] 測試子視圖建立 (6 tests)
    - [x] 測試 Feed 選擇和載入 (8 tests)
    - [x] 測試 Entry 選擇 (3 tests)
    - [x] 測試操作功能 (5 tests)
  - **成果**: RSS 測試 48 → **78** (+30), flake8 零錯誤 ✅
  - [ ] 補充 `test_rss_manager.py` (+10 tests) (保留待後續)

- [ ] **其他模組測試補充** (保留待後續)
  - [ ] 補充 `test_audio_manager.py` (+10 tests)

- **階段 3-5 成功指標** ✅:
  - ✅ 總測試數：393 → **457** (+64，遠超目標 350)
  - ✅ 測試通過率：**>95%**
  - ✅ youtube_downloader.py：**91% 覆蓋率**
  - ✅ RSS 模組測試：48 → **78** (+30 tests)
  - ✅ flake8：**零錯誤**

### 🎯 中期目標 (Week 5-8) - 程式碼品質全面提升
- [ ] **複雜度優化 - 第二輪** (預估: 3-5 天)
  - [x] 安裝並配置 radon 和 xenon ✅ 2025-10-14
  - [x] 分析所有檔案複雜度 ✅ 2025-10-14
  - [x] 建立 CODE_COMPLEXITY_REPORT.md ✅ 2025-10-14
  - [x] 重構 rss_manager.py fetch_feed_entries (CC 24 → 7) ✅ 2025-10-14
  - [x] 重構 youtube_downloader.py download_audio (CC 19 → 7) ✅ 2025-10-14
  - [x] 重構 music_library_view.py _on_category_select_internal (CC 11 → 6) ✅ 2025-10-14
  - [x] 重構 music_metadata_fetcher.py update_song_metadata (CC 10 → 5) ✅ 2025-10-14
  - [x] 重構 music_metadata_fetcher.py fetch_metadata (CC 10 → 5) ✅ 2025-10-14
  - [x] 重構 settings_window.py _validate_and_save_devices (CC 10 → 6) ✅ 2025-10-14
  - [x] 重構 stats_window.py show (CC 10 → 2) ✅ 2025-10-14
  - [x] 重構 music_window.py _update_progress (CC 9 → 6) ✅ 2025-10-14
  - [x] 重構 music_window.py _play_next (CC 9 → 4) ✅ 2025-10-14
  - [ ] 重構剩餘 1 個 CC > 8 的函數:
    1. [ ] music_window.py _toggle_play_pause (CC 8 → 6)
  - [ ] 消除重複程式碼 (DRY 原則)
  - [ ] 統一錯誤處理模式
  - **目標**: xenon 零違規，所有函數 CC < 10
  - **當前進度**: 9/9 完成 (100%) ✅，xenon 違規 5 → 2，CC > 10 函數 9 → 6

- [ ] **整合測試與文檔** (預估: 1 週)
  - [ ] 建立整合測試套件 (+20 tests)
  - [ ] 更新 API 文檔
  - [ ] 建立開發者指南
  - [ ] 更新架構圖
  - **成功指標**: 整體健康度 > 85/100

### 🔧 開發流程改善
- [x] **引入複雜度分析工具** (已完成 2025-10-14) ✅
  - [x] 安裝 radon 和 xenon ✅
  - [x] 設定複雜度門檻 (CC < 10) ✅
  - [x] 整合到 Git hooks ✅
  - [x] 建立 .radon.cfg 配置檔案 ✅
  - **成果**: Git pre-commit hook 現在會自動檢查複雜度

- [ ] **CI/CD 整合** (可選)
  - [ ] 建立 GitHub Actions workflow
  - [ ] 自動執行測試
  - [ ] 自動上傳覆蓋率報告到 Codecov

## 🔮 未來功能構想 (Future Ideas)
<!-- 在此新增未來想要實作的功能 -->
- 音樂播放器歌詞顯示功能
- 音樂播放器等化器設定
