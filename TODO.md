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

## 🚧 進行中 (In Progress)
<!-- 目前正在進行的工作 -->

## 📋 待辦事項 (Todo) - 根據程式碼健康度分析 (2025-10-13)

### 🔥 緊急優先 (Week 1-2) - 技術債務消除
- [ ] **完成 music_window.py 重構** (預估: 3-5 天)
  - [ ] Day 1-2: 抽離 UI 元件模組
    - [ ] 建立 `MusicLibraryView` (資料夾樹 + 歌曲列表,約 300 行)
    - [ ] 建立 `MusicSearchView` (搜尋與篩選邏輯,約 150 行)
    - [ ] 建立 `MusicHeaderView` (頂部按鈕區域,約 100 行)
    - [ ] 更新 music_window.py 使用新元件
  - [ ] Day 3-4: 增加測試覆蓋率
    - [ ] 新增 `test_music_library_view.py` (+20 tests)
    - [ ] 新增 `test_music_search_view.py` (+15 tests)
    - [ ] 擴展 `test_music_window.py` (+25 tests)
    - [ ] 目標: 測試覆蓋率 20% → 60%
  - [ ] Day 5: 驗證與文檔更新
    - [ ] 執行所有測試 (目標: >320 tests)
    - [ ] 檢查程式碼複雜度
    - [ ] 更新 CHANGELOG.md
    - [ ] 提交 Git commit
  - **成功指標**: music_window.py < 800 行,測試覆蓋率 > 60%

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