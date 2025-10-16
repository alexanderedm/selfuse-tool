# 更新日誌

所有重要的專案變更都會記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
版本編號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

---

## [未發布]

### 新增 (Added)
- **歌曲拖放功能** (2025-10-16)
  - 實作拖放（Drag and Drop）功能，可直接拖動歌曲到資料夾
  - 拖動過程中提供視覺回饋（滑鼠游標變化）
  - 懸停在資料夾上時顯示可放下提示
  - 放下時彈出確認對話框
  - 移動完成後自動重新載入音樂庫
  - 使用方式：
    1. 在右側歌曲列表中按住滑鼠左鍵
    2. 拖動到左側資料夾樹的目標資料夾上
    3. 放開滑鼠，確認移動即可
  - 修改檔案：`src/music/views/music_library_view.py`

### 修復 (Fixed)
- **歌曲移動和刪除功能無法使用** (2025-10-16)
  - 修正使用錯誤的欄位名稱 `filepath`，應為 `audio_path`
  - 移動功能現在會同時移動音訊檔案和 JSON 檔案
  - 刪除功能現在會同時刪除音訊檔案和 JSON 檔案
  - 增加詳細的日誌記錄和錯誤追蹤
  - 修改檔案：`src/music/views/music_library_view.py`

- **播放控制按鈕顯示被裁切** (2025-10-16)
  - 增加播放控制區域主框架寬度從 280px 到 320px
  - 縮小播放按鈕尺寸：上一首/下一首 55x55px → 50x50px，播放/暫停 75x75px → 65x65px
  - 減少按鈕間距，優化整體佈局
  - 修復上一首、播放、下一首按鈕顯示不完整問題
  - 修改檔案：`src/music/views/music_playback_view.py`

- **優化視窗體驗與修復 RSS 功能** (2025-10-16)
  - **修復 Bug**:
    - RSS 視窗：修復 `rss_preview_view.py` corner_radius 元組錯誤（TypeError: can't multiply sequence by non-int of type 'float'）
    - 音樂播放器：RSS 錯誤修復後，音樂播放器啟動不再閃退
  - **功能優化**:
    - 設定視窗即時儲存：移除儲存按鈕，改為裝置選擇和元數據開關變更時自動儲存
    - 設定視窗：增加驗證邏輯，防止選擇相同裝置或未完整選擇時儲存
    - 視窗隱藏機制：所有視窗（設定、統計、更新日誌、RSS、音樂）點擊 X 時隱藏而非銷毀
    - 視窗狀態保持：重新開啟時使用 `deiconify()` 恢復視窗狀態
    - 音樂播放器：隱藏時繼續播放音樂，使用體驗更流暢
  - **修改檔案**:
    - `src/rss/rss_preview_view.py` - 修復 corner_radius 參數錯誤
    - `src/windows/settings_window.py` - 實作即時儲存功能與隱藏機制
    - `src/windows/stats_window.py` - 實作視窗隱藏機制
    - `src/windows/changelog_window.py` - 實作視窗隱藏機制
    - `src/rss/rss_window.py` - 實作視窗隱藏機制
    - `src/music/windows/music_window.py` - 實作視窗隱藏機制（保持播放）

### 變更 (Changed)
- **專案結構重構：模組化組織** (2025-10-16)
  - 將所有 Python 檔案從根目錄遷移到 `src/` 下的分類資料夾
  - 新的目錄結構：
    - `src/core/` - 核心模組（audio_manager, config_manager, logger, constants）
    - `src/audio/` - 音訊處理模組（audio_player, audio_processor, equalizer_filter）
    - `src/music/` - 音樂播放器模組（分為 windows, views, dialogs, managers, actions, utils）
    - `src/rss/` - RSS 閱讀器模組
    - `src/windows/` - 視窗模組（settings_window, stats_window, changelog_window）
    - `src/utils/` - 工具模組（clipboard_monitor, path_utils, discord_presence, ui_theme）
  - 更新所有 import 路徑為絕對導入（`from src.core.logger import logger`）
  - 更新所有測試檔案的 import 和 @patch 語句
  - 處理的檔案數量：
    - 批次更新 98 個檔案，其中 65 個有變更
    - 更新 4 個測試檔案的 @patch 裝飾器路徑
  - 測試結果：513/708 個測試通過（72% 成功率）
  - 所有 `__init__.py` 檔案已建立，支援套件導入
  - **效益**：
    - 更清晰的程式碼組織結構
    - 更容易維護和擴展
    - 符合 Python 專案最佳實踐
    - 為未來模組化開發打下基礎

### 已移除 (Removed)
- **🤖 AI 團隊協作助理系統** (已回退於 2025-10-16)
  - 移除原因：功能實作需要較長設定時間（Ollama 安裝、RAG 資料準備等），應使用者要求暫時回退
  - 已刪除檔案：
    - `ai_agent.py` - AI 代理類別
    - `rag_system.py` - RAG 檢索系統
    - `meeting_manager.py` - 會議管理器
    - `ai_assistant.py` - AI 助理主控制器
    - `ai_assistant_window.py` - CustomTkinter UI 介面
    - `AI_SETUP_GUIDE.md` - 設定指南
    - `rag_manager_tool.py` - RAG 資料管理工具
  - 已從 main.py 移除相關整合程式碼
  - **注意**：功能保留在版本歷史中，未來可視需求重新引入

### 新增 (Added)
- **UI 滾動功能改進** (2025-10-16)
  - `settings_window.py` - 新增 CTkScrollableFrame 主框架，解決高度 850px 內容顯示不全問題
  - `stats_window.py` - 統計容器改用 CTkScrollableFrame，支援多裝置卡片滾動
  - `changelog_window.py` - 已有 CTkTextbox 內建滾動（無需修改）
  - `music_library_view.py` - 已有 ttk.Treeview 內建滾動（無需修改）

### 修復 (Fixed)
- **修復音樂播放器 AttributeError** (2025-10-16)
  - 修復 `MusicPlaybackView` 缺少 `progress_bar` 和 `volume_scale` 屬性
  - 新增向後相容別名，確保 `music_window.py` 正常運作
  - 問題：嘗試訪問不存在的屬性導致程式崩潰
  - 解決：在 `MusicPlaybackView.__init__` 和 `create_view` 中設定別名
- **程式碼品質提升** (2025-10-16)
  - flake8 檢查從 22 個錯誤降至 4 個（僅測試檔案的小縮排問題）
  - 修復 `test_music_window.py` 和 `test_music_folder_actions.py` 的多餘空行問題
  - 核心程式碼檔案達到 flake8 零錯誤
  - AI 助理系統所有模組 flake8 零錯誤
- **多來源音樂元數據補全整合** (2025-10-16)
  - 將 `music_metadata_multi_source.py` 整合到 `music_metadata_fetcher.py`
  - 優先使用 YouTube Music API，失敗時自動 fallback 到 iTunes API
  - 提高元數據補全成功率，支援更多音樂來源
  - 智慧處理不同來源返回的欄位名稱（`thumbnail` vs `artworkUrl`）
- **Phase 4: 完成所有視窗 CustomTkinter 遷移** (2025-10-16)
  - 完成剩餘 8 個模組的遷移，達成 100% CustomTkinter UI 現代化
  - 遷移模組列表：
    - `music_lyrics_view.py` - 歌詞顯示視圖（CTkTextbox + 圓角框架）
    - `settings_window.py` - 設定視窗（CTkSwitch、CTkOptionMenu、CTkEntry）
    - `stats_window.py` - 統計視窗（CTkProgressBar、圓角卡片）
    - `changelog_window.py` - 更新日誌視窗（CTkTextbox、簡化設計）
    - `rss_window.py` - RSS 主視窗（圓角框架、現代化按鈕）
    - `rss_feed_list_view.py` - RSS Feed 列表（圓角框架包裹 Treeview）
    - `rss_entry_list_view.py` - RSS 文章列表（CTkEntry + CTkRadioButton）
    - `rss_preview_view.py` - RSS 預覽視圖（CTkTextbox + 圓角設計）
  - 設計特點：
    - 圓角標準：主框架 15px、卡片 12px、按鈕 10px、輸入框 8px
    - 統一按鈕高度：38-40px（標準）、32-35px（小型）
    - 所有對話框自動置頂（transient、lift、focus_force）
    - 保留 ttk.Treeview（包在 CTkFrame 圓角框架中）
    - flake8 零錯誤
  - **遷移進度：16/16（100%）**
  - **Phase 4 完成！所有視窗已完全現代化**

- **對話框視窗 CustomTkinter 遷移** (2025-10-16 - Phase 3)
  - 遷移 `music_playlist_dialog.py` 到 CustomTkinter（播放列表管理）
    - 所有按鈕使用圓角設計（corner_radius=10）
    - 對話框和框架使用圓角（corner_radius=12-15）
    - 升級所有標籤、按鈕、輸入框到 CustomTkinter 元件
    - 保留 ttk.Treeview（包在圓角 CTkFrame 中）
  - 遷移 `music_download_dialog.py` 到 CustomTkinter（YouTube 下載）
    - 圓角輸入框（corner_radius=8，帶 placeholder）
    - 圓角下拉選單（CTkOptionMenu）
    - 現代化進度條（CTkProgressBar，indeterminate 模式）
    - 所有按鈕統一 40px 高度，圓角 10px
  - 遷移 `music_history_dialog.py` 到 CustomTkinter（播放歷史）
    - 圓角框架包裹 Treeview（corner_radius=12）
    - 統一按鈕樣式（38px 高度，圓角 10px）
    - 清除歷史按鈕使用警告色（#d43d00）
  - flake8 零錯誤
- **音樂庫視圖全面升級** (2025-10-16)
  - 遷移 `music_library_view.py` 到 CustomTkinter，獲得圓角邊框
  - 資料夾樹和歌曲列表使用圓角框架（corner_radius=15）
  - 新增排序功能：可按歌名、藝術家、時長排序，支援升序/降序
  - 新增歌曲右鍵選單：移動歌曲到不同資料夾、刪除歌曲
  - 新增資料夾右鍵選單：重新命名資料夾、刪除資料夾
  - 歌曲列表新增「藝術家」欄位顯示
  - 所有對話框自動置頂並聚焦（添加 transient、lift、focus_force）
  - 視窗最小寬度設定為 1200x700，確保所有按鈕顯示完整
  - flake8 零錯誤
  - 測試通過率 > 98%
- **CustomTkinter UI 現代化升級** (2025-10-16 - Overnight Development)
  - 遷移核心視窗到 CustomTkinter，獲得現代化圓角 UI
  - 遷移完成的模組（16/16 - 100%）：
    - Phase 1-3: 音樂播放器核心（8個模組）
      - `music_window.py` - 主視窗（ctk.CTk）
      - `music_header_view.py` - 頂部按鈕區域（圓角按鈕，更大按鈕設計）
      - `music_search_view.py` - 搜尋框（圓角輸入框 + placeholder）
      - `music_playback_view.py` - 播放控制區域（圓角框架 + 現代化控制元件）
      - `music_library_view.py` - 音樂庫視圖（圓角框架 + 排序功能）
      - `music_playlist_dialog.py` - 播放列表對話框
      - `music_download_dialog.py` - YouTube 下載對話框
      - `music_history_dialog.py` - 播放歷史對話框
    - Phase 4: 其他視窗和 RSS 模組（8個模組）
      - `music_lyrics_view.py` - 歌詞顯示視窗
      - `settings_window.py` - 設定視窗
      - `stats_window.py` - 統計視窗
      - `changelog_window.py` - 更新日誌視窗
      - `rss_window.py` - RSS 閱讀器主視窗
      - `rss_feed_list_view.py` - RSS Feed 列表
      - `rss_entry_list_view.py` - RSS 文章列表
      - `rss_preview_view.py` - RSS 預覽視圖
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
  - flake8 零錯誤
  - **所有 16 個模組遷移完成（100%）**

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
