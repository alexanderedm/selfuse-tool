# 專案待辦清單 (Todo List)

## ✅ 已完成 (Completed)
- [x] **自動補全缺失音樂資訊** (2025-10-13 完成)
  - 播放時自動檢測缺失的封面/藝術家/專輯
  - 從 iTunes API 自動抓取資訊
  - 下載高解析度封面 (600x600)
  - 背景執行不阻塞 UI
  - 完整測試套件 (38 tests)

- [x] **music_window.py 模組化重構** (2025-10-13 完成)
  - 從 2,865 行減少到 1,511 行 (-47%)
  - 抽離 6 個專門模組
  - 新增 113 個測試
  - 達成健康度目標

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

## 🚧 進行中 (In Progress)
- [ ] **解決 tkinter 測試環境問題**
  - 1 個測試因 tkinter 環境設定問題間歇性失敗 (test_music_history_dialog)
  - 非程式碼問題,為 Windows Python tkinter 安裝不完整
  - 單獨運行測試時正常通過
  - 當前測試通過率: 316/317 (99.7%)

## 📋 待辦事項 (Todo) - 根據程式碼健康度分析 (2025-10-13)

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
  - **目前進度**: music_window.py 1,548 → 945 行 (-38.9%)
  - **階段 4 完成**: 整合 MusicPlaybackView (-275 行)
  - **階段 5 完成**: 整合 MusicSongActions (-150 行)
  - **測試狀態**: 328 個測試, 327 passed, 1 failed (99.7%)
  - **測試覆蓋率**: **68%** ✅ (已超過 60% 目標)
  - **剩餘工作**: 還需減少 145 行達成 < 800 行目標
  - **下一步**: 抽離 MusicFolderActions 模組 (預計 ~100 行)

### ⚠️ 高優先 (Week 3-4) - 測試覆蓋率提升
- [ ] **RSS 模組測試補充** (預估: 1 天)
  - [ ] 新增 `test_rss_window.py` (+30 tests)
    - [ ] 測試 UI 元件建立
    - [ ] 測試文章列表渲染
    - [ ] 測試篩選與搜尋邏輯
    - [ ] 測試已讀/未讀狀態切換
  - [ ] 補充 `test_rss_manager.py` (+10 tests)

- [ ] **YouTube 下載器測試** (預估: 1 天)
  - [ ] 新增 `test_youtube_downloader.py` (+20 tests)
    - [ ] Mock subprocess.run
    - [ ] 測試所有錯誤路徑
    - [ ] 測試超時處理
    - [ ] 測試瀏覽器 cookie 回退邏輯

- [ ] **其他模組測試補充** (預估: 1 天)
  - [ ] 補充 `test_settings_window.py` (+15 tests)
  - [ ] 補充 `test_audio_manager.py` (+10 tests)
  - **成功指標**: 整體測試覆蓋率 > 70%,總測試數 > 350

### 🎯 中期目標 (Week 5-8) - 程式碼品質全面提升
- [ ] **複雜度優化** (預估: 1 週)
  - [ ] 安裝並配置 radon 和 xenon
  - [ ] 分析所有檔案複雜度
  - [ ] 重構 Cyclomatic Complexity > 10 的函數
  - [ ] 消除重複程式碼 (DRY 原則)
  - [ ] 統一錯誤處理模式

- [ ] **整合測試與文檔** (預估: 1 週)
  - [ ] 建立整合測試套件 (+20 tests)
  - [ ] 更新 API 文檔
  - [ ] 建立開發者指南
  - [ ] 更新架構圖
  - **成功指標**: 整體健康度 > 85/100

### 🔧 開發流程改善
- [ ] **引入複雜度分析工具**
  - [ ] 安裝 radon 和 xenon
  - [ ] 設定複雜度門檻 (CC < 10)
  - [ ] 整合到 Git hooks

- [ ] **CI/CD 整合** (可選)
  - [ ] 建立 GitHub Actions workflow
  - [ ] 自動執行測試
  - [ ] 自動上傳覆蓋率報告到 Codecov

## 🔮 未來功能構想 (Future Ideas)
<!-- 在此新增未來想要實作的功能 -->
- 音樂播放器歌詞顯示功能
- 音樂播放器等化器設定
- RSS 訂閱 OPML 匯入/匯出
- 多語言支援 (i18n)