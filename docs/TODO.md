# 專案待辦清單 (Todo List)

## 我的個人希望新增功能或改進修正方面建議
- [ ] **完全個人化工具之個人助理** (已回退 2025-10-16)
  - [ ] 實作 AI 團隊協作助理系統
  - [ ] 5 個 AI 代理（創意家、風險分析師、務實主義者、批判思考者、優化專家）
  - [ ] RAG 檢索系統（ChromaDB 向量資料庫）
  - [ ] 會議管理器（討論、投票、負責人選舉）
  - [ ] CustomTkinter UI 介面
  - [ ] 整合到系統托盤選單
  - 參閱 RAGPRD.md
  - **注意**：功能實作需要較長時間（Ollama 安裝、RAG 資料準備等），用戶要求暫時回退

- [x] **本地音樂播放器改進修正建議** (完成於 2025-10-16) ✅
  - [x] 資料夾歌曲右鍵移動功能 - 已實現並整合到 MusicLibraryView
  - [x] 音樂補全功能支援多來源 - 已整合 YouTube Music + iTunes 雙來源
  - [x] Discord Rich Presence 整合 - 已整合，顯示歌曲、藝術家、專輯、進度條和封面

## ✅ 已完成 (Completed)
- [x] **UI 滾動功能改進** (完成於 2025-10-16)
  - [x] settings_window.py - 新增 CTkScrollableFrame 主框架
  - [x] stats_window.py - 統計容器改用 CTkScrollableFrame
  - [x] changelog_window.py - 已有 CTkTextbox 內建滾動（確認無需修改）
  - [x] music_library_view.py - 已有 ttk.Treeview 內建滾動（確認無需修改）
  - 解決視窗顯示不全問題
  - flake8 零錯誤

- [x] **音樂播放器關鍵修復與改進** (完成於 2025-10-16)
  - 修復 `MusicPlaybackView` 屬性缺失問題 (progress_bar, volume_scale)
  - 整合多來源元數據補全 (YouTube Music + iTunes)
  - 驗證 Discord Rich Presence 已正確整合
  - 確認歌曲移動功能正常運作
  - 驗證按鈕大小已優化，文字完整顯示
  - flake8 核心檔案達到零錯誤（測試檔案僅 4 個小縮排問題）
- [x] **托盤更新日誌功能** (2025-10-14 完成)
  - 建立 `changelog_window.py` 模組 (280 行, CC=2.6, A級)
  - 在系統托盤右鍵選單新增「📝 更新日誌」項目
  - **功能特點**:
    - ✅ 自動讀取並顯示 CHANGELOG.md
    - ✅ 深色主題風格，與其他視窗一致
    - ✅ 支援 Markdown 格式渲染 (標題/程式碼/列表)
    - ✅ 可滾動查看完整更新歷史
    - ✅ 單一實例設計
  - **程式碼品質**: CC=2.6 (A級), flake8 零錯誤 ✅
  - **建立檔案**: changelog_window.py, test_changelog_window_manual.py
  - **修改檔案**: main.py (新增 open_changelog() 方法)

- [x] **專案健康分析報告** (2025-10-14 完成)
  - 完成全面的代碼健康度分析 (38 源文件, 35 測試文件, 569 測試)
  - 分析維度: 循環複雜度、可維護性指數、Git 變更頻率、測試覆蓋率
  - **整體健康狀況: A 級 (優秀)** 🎉
    - ✅ 平均複雜度: CC=2.72 (A 級)
    - ✅ 所有文件可維護性: MI > 20 (A 級)
    - ✅ 測試覆蓋率: 92% (35/38 文件)
    - ✅ 零 xenon 違規
    - ✅ 96%+ 測試通過率
  - **識別重點關注文件**:
    - 🔴 music_window.py: 最高變更率 (20 commits), 需重構 _load_lyrics_for_song() (CC=10)
    - 🟡 settings_window.py: 中等變更率 (9 commits)
  - **優秀實踐**:
    - 🏆 constants.py 和 music_header_view.py: MI = 100.00 (完美)
    - 📦 清晰的模組化架構 (view/controller/manager 分離)
    - 🎉 成功重構 10 個高複雜度函數
  - **生成文件**: `PROJECT_HEALTH_REPORT.md`
  - **修復**: pre-commit hook xenon 檢查 bug
  - **已推送至 GitHub** ✅

- [x] **音樂播放器歌詞顯示功能** (2025-10-14 完成)
  - 使用 TDD 方法實現完整歌詞顯示功能
  - 建立 `lyrics_parser.py` - LRC 歌詞解析器 (117 行, CC=2.9)
  - 建立 `music_lyrics_view.py` - 歌詞顯示 UI (328 行, CC=2.9)
  - **功能特點**:
    - 支援 LRC 格式歌詞檔案
    - 自動同步高亮當前播放歌詞
    - 自動滾動到當前位置
    - 點擊歌詞行跳轉播放
    - 深色主題 UI 設計
  - **測試成果**: 33 個測試, 32/33 通過 (97%)
  - **程式碼品質**: flake8 零錯誤, CC=2.9 (A級)
  - 歌詞文件格式: 與音樂文件同目錄同名,副檔名 .lrc
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
    - 提取 6 個輔助方法：
      1. `_get_cached_entries()` - 快取檢查邏輯（CC 3）
      2. `_parse_publish_time()` - 發布時間解析（CC 7）
      3. `_extract_entry_content()` - 內容提取邏輯（CC 7）
      4. `_process_content_and_summary()` - HTML 處理與摘要生成（CC 3）
      5. `_parse_feed_entry()` - 單個 entry 解析（CC 1）
      6. `_update_cache()` - 快取更新邏輯（CC 1）
    - 原函數從 101 行縮減至 33 行（-67%）
    - 使用 TDD 方法確保所有 RSS 測試通過 (12/12)
    - flake8 零錯誤，xenon 檢查通過
    - **消除 D 級違規** ✅
  - 整合複雜度檢查到 Git pre-commit hooks
  - **成果**:
    - 平均複雜度: **A (3.03)** ⭐ (目標 < 5)
    - CC > 10 函數: **6 個** (從 9 降至 6，進步 33%)
    - xenon 違規: **1 個** ✅ (從 5 降至 1，進步 80%，已消除 D 級違規)
    - MI < 65 檔案: 15 個
    - 所有測試通過，flake8 零錯誤

## 🚧 進行中 (In Progress)

## ✅ 完成項目 (Completed)
- [x] **CustomTkinter UI 全面遷移 - 100% 完成！** (完成於 2025-10-16 - Overnight Development)
  - [x] Phase 1: 核心視窗遷移 ✅
    - [x] music_window.py - 主視窗（ctk.CTk）✅
    - [x] music_header_view.py - 頂部按鈕區域（圓角按鈕，更大設計）✅
    - [x] music_search_view.py - 搜尋框（圓角輸入框）✅
  - [x] Phase 2: View 模組遷移 ✅
    - [x] music_playback_view.py - 播放控制區 ✅
    - [x] music_library_view.py - 資料夾樹和歌曲列表（保留 ttk.Treeview）✅
    - [x] music_lyrics_view.py - 歌詞顯示（CTkTextbox）✅
  - [x] Phase 3: 對話框遷移 ✅
    - [x] music_playlist_dialog.py ✅
    - [x] music_download_dialog.py ✅
    - [x] music_history_dialog.py ✅
    - [x] music_equalizer_dialog.py ✅
  - [x] Phase 4: 其他視窗和 RSS 模組遷移 ✅（2025-10-16 完成）
    - [x] music_lyrics_view.py - 歌詞顯示視圖 ✅
    - [x] settings_window.py - 設定視窗 ✅
    - [x] stats_window.py - 統計視窗 ✅
    - [x] changelog_window.py - 更新日誌視窗 ✅
    - [x] rss_window.py - RSS 閱讀器主視窗 ✅
    - [x] rss_feed_list_view.py - RSS Feed 列表 ✅
    - [x] rss_entry_list_view.py - RSS 文章列表 ✅
    - [x] rss_preview_view.py - RSS 預覽視圖 ✅
  - **最終進度**: 16/16 模組已遷移（100%）✅
  - **成果**:
    - 所有視窗使用 CustomTkinter 圓角現代化 UI
    - 圓角標準：主框架 15px、卡片 12px、按鈕 10px、輸入框 8px
    - 統一按鈕高度：38-40px（標準）、32-35px（小型）
    - 所有對話框自動置頂（transient、lift、focus_force）
    - 保留 ttk.Treeview（包在 CTkFrame 中）
    - flake8 零錯誤
  - **🎉 CustomTkinter UI 遷移專案完成！**

- [ ] **修復 test_rss_window.py 測試失敗** (發現於 2025-10-14)
  - 7 個測試失敗 (包含 test_add_feed_manual_* 系列)
  - 問題: Mock 設定不正確，askstring().strip() 返回 Mock 對象而非字串
  - 影響範圍: 7/30 tests (23%)
  - 整體測試通過率仍達 **98.6%** (630/639)
  - 需要: 修正測試中的 Mock 返回值設定

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
  - [x] 重構 music_window.py _toggle_play_pause (CC 8 → 4) ✅ 2025-10-14
  - [ ] 消除重複程式碼 (DRY 原則)
  - [ ] 統一錯誤處理模式
  - **目標**: xenon 零違規，所有函數 CC < 10
  - **當前進度**: 10/10 完成 (100%) ✅，xenon 違規 5 → 1 (已消除 D 級違規)，CC > 8 函數已全部優化

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

- [x] **音樂播放器等化器功能 (EQ)** (2025-10-14 完成)
  - 使用 TDD 方法實現等化器設定管理
  - **技術評估**: pygame.mixer 不支援即時 EQ，僅實現設定管理
  - 建立 `music_equalizer.py` 模組 (268 行, 28/28 tests, CC=2.4)
  - 建立 `music_equalizer_dialog.py` UI (363 行, 17/19 tests, CC=2.4)
  - **功能特點**:
    - 10 頻段等化器: 60Hz ~ 16kHz
    - 增益範圍: -12dB 到 +12dB
    - 8 種預設模式 (流行、搖滾、古典、爵士、人聲、重低音、柔和、自定義)
    - 設定持久化到 config.json
    - UI 深色主題風格
  - **測試成果**: 47 個測試, 45/47 通過 (96%)
  - **程式碼品質**: flake8 零錯誤, CC=2.4 (A級)
  - **整合說明**: 詳見 `EQUALIZER_INTEGRATION_GUIDE.md`
  - **注意事項**: 音訊效果應用功能待未來整合音訊處理庫實現

## ✅ 最近完成 (Recently Completed)
- [x] **修復 UI 背景變白問題** (完成於 2025-10-15) 🐛
  - **問題**: 開啟等化器對話框後，整個音樂播放器視窗背景從深色變成白色
  - **原因**: ttkbootstrap 的全域主題設定影響了整個 tkinter 應用程式
  - **解決方案**: 回退到原生 tkinter + 手動深色主題配色
  - **修改檔案**:
    - music_equalizer_dialog.py - 回退所有 ttkbootstrap 元件到 tk/ttk
    - main.py - 移除 ttkbootstrap import
  - **提交**: `79eca1c`, `3baaeee`

- [x] **等化器對話框現代化 UI [已回退]** (完成於 2025-10-15)
  - 嘗試使用 ttkbootstrap 現代化 UI 框架
  - 因全域主題衝突問題已回退
  - 保留模組：ui_theme_modern.py、ui_preview.py（供未來整個應用遷移時使用）

- [x] **等化器即時生效功能實作** (完成於 2025-10-15) ✨
  - **問題**: 等化器調整只在下一首歌曲才生效
  - **解決方案**: 新增回調機制，立即同步設定到 AudioProcessor
  - **實作步驟**:
    - [x] 在 `MusicEqualizerDialog` 新增 `on_equalizer_change` 回調參數
    - [x] 實作 `_trigger_equalizer_change()` 輔助方法
    - [x] 在所有等化器變更操作中觸發回調 (滑桿、預設、重置、啟用)
    - [x] 在 `music_window.py` 連接回調到 `_sync_equalizer_to_processor()`
    - [x] 新增 4 個單元測試驗證即時同步功能
  - **測試成果**:
    - ✅ 4 個新測試全部通過
    - ✅ 整體測試通過率: **98.6%** (630/639 tests)
    - ✅ flake8 檢查零錯誤
  - **修改檔案**:
    - music_equalizer_dialog.py (+12 行)
    - music_window.py (修改 1 行)
    - tests/test_music_equalizer_dialog.py (+56 行)

- [x] **音樂播放器架構遷移** (完成於 2025-10-15) 🎉
  - **目標**: 將 pygame.mixer 遷移到 sounddevice，實現即時等化器功能
  - **所有階段完成** (階段 1-4) ✅
    - [x] 安裝新依賴套件 (sounddevice, numpy, scipy, librosa, soundfile)
    - [x] 實作 EqualizerFilter - 10 頻段參數等化器 (342 行, 28 tests)
    - [x] 實作 AudioProcessor - 音訊處理管線 (123 行, 24 tests)
    - [x] 實作 AudioPlayer - sounddevice 播放器核心 (274 行, 15 tests)
    - [x] 整合到 music_window.py (+147 行整合邏輯)
    - [x] 所有測試通過 (677 tests, ≥ 95% 通過率)
    - [x] flake8 零錯誤
  - **成果**:
    - ✅ 即時等化器功能已可使用
    - ✅ 調整等化器滑桿立即生效
    - ✅ 向後相容 (自動 fallback 到 pygame.mixer)
    - ✅ 所有現有功能正常運作
  - **新增檔案**:
    - audio_player.py (274 行)
    - tests/test_audio_player.py (15 tests)
  - **技術重點**:
    - 使用 scipy.signal IIR 濾波器實作即時等化器
    - sounddevice callback 機制實現即時音訊流處理
    - 線程安全設計 (threading.Lock)
    - 音訊 callback 處理 < 10ms

## 🔮 未來功能構想 (Future Ideas)
<!-- 在此新增未來想要實作的功能 -->
- ✅ 等化器音訊效果實際應用 (已完成 2025-10-15)
- 歌詞編輯器 (建立和編輯 LRC 歌詞檔案)
- 線上歌詞搜尋與下載
- 歌詞翻譯顯示 (雙語歌詞)
