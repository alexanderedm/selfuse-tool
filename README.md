# 音訊輸出裝置快速切換工具

一個輕量級的 Windows 系統托盤工具，讓你能快速在兩個預設的音訊輸出裝置之間切換。

## 功能特色

- 🎧 **一鍵切換**: 在兩個預設音訊裝置間快速切換
- 🖼️ **系統托盤整合**: 常駐系統托盤，不占用桌面空間
- 🎨 **視覺回饋**:
  - 切換時顯示通知訊息
  - 托盤圖示顏色隨當前裝置改變
- ⚙️ **簡單設定**: 圖形化設定介面，輕鬆選擇要切換的裝置
- 🚀 **開機自啟動**: 可選擇隨 Windows 開機啟動
- 💾 **記憶設定**: 所有設定持久化儲存，重開機後保留

## 系統需求

- Windows 10/11 (或 Windows 7/8，但部分功能可能不穩定)
- Python 3.8 或更高版本

## 安裝步驟

### 方法 1: 使用原始碼

1. 克隆或下載此專案
2. 安裝依賴套件:
```bash
pip install -r requirements.txt
```

3. 執行程式:
```bash
python main.py
```

### 方法 2: 使用打包的執行檔 (待發布)

直接下載 `AudioSwitcher.exe` 並執行即可。

## 使用說明

### 首次使用

1. 執行程式後，系統托盤會出現一個圖示
2. 右鍵點擊圖示，選擇「設定」
3. 在設定視窗中選擇兩個要切換的音訊裝置 (裝置 A 和 裝置 B)
4. 點擊「儲存」

### 日常使用

- **切換裝置**: 右鍵點擊托盤圖示 → 選擇「切換輸出裝置」
- **修改設定**: 右鍵點擊托盤圖示 → 選擇「設定」
- **開機自啟動**: 右鍵點擊托盤圖示 → 勾選「開機自動啟動」
- **結束程式**: 右鍵點擊托盤圖示 → 選擇「結束」

### 托盤圖示顏色說明

- 🔵 **藍色**: 目前使用裝置 A
- 🟢 **綠色**: 目前使用裝置 B
- ⚫ **灰色**: 使用其他裝置或未設定

## 專案結構

```
selftool/
├── main.py                    # 主程式進入點
├── audio_manager.py           # 音訊裝置管理模組
├── config_manager.py          # 設定檔管理模組
├── settings_window.py         # 設定視窗模組
├── stats_window.py            # 統計視窗模組
├── rss_manager.py             # RSS 管理模組
├── rss_window.py              # RSS 視窗模組
├── music_manager.py           # 音樂管理模組
├── music_window.py            # 音樂播放器視窗
├── youtube_downloader.py      # YouTube 下載器
├── clipboard_monitor.py       # 剪貼簿監控模組
├── logger.py                  # 日誌系統
├── config.json                # 設定檔 (自動生成)
├── requirements.txt           # Python 依賴套件
├── README.md                  # 本文件
├── CHANGELOG.md               # 更新日誌
└── PRD.md                     # 產品需求文件
```

## 技術細節

### 使用的技術棧

- **pystray**: 系統托盤功能
- **pycaw**: Windows 音訊控制
- **tkinter**: 設定介面 (Python 內建)
- **comtypes**: COM 介面操作
- **pywin32**: Windows API
- **feedparser**: RSS 訂閱解析
- **pygame**: 音樂播放

### 運作原理

本工具使用 Windows 的 PolicyConfig COM 介面來切換預設音訊裝置，相容 Windows 7/8/10/11。

## 打包成執行檔 (可選)

如果想要打包成單一執行檔:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name=AudioSwitcher main.py
```

生成的 `AudioSwitcher.exe` 會在 `dist` 資料夾中。

## 📊 專案健康度

根據最新的程式碼健康度分析 (2025-10-13):

- **總體健康度**: 🟢 **90/100** (卓越 - 重構完成!)
- **檔案總數**: 40 個 Python 檔案 (23 原始碼 + 17 測試)
- **測試覆蓋率**: ✅ **68%** (339 個單元測試, 99.4% 通過)
- **程式碼品質**: ✅ 零 flake8 錯誤

**🎉 music_window.py 重構完成 (2025-10-13) ✅**:
  - ✅ **達成 < 800 行目標**: 1,548 → **774 行** (-50.0%)
  - ✅ **從最初瘦身 73%**: 2,865 → 774 行
  - ✅ **模組化重構完成**: 新增 11 個專門模組
    1. MusicFileManager (檔案操作, 120 行)
    2. MusicHistoryDialog (播放歷史, 115 行)
    3. MusicPlaylistDialog (播放列表, 313 行)
    4. MusicDownloadDialog (YouTube 下載, 173 行)
    5. MusicMetadataFetcher (自動補全音樂資訊, 155 行)
    6. MusicLibraryView (資料夾樹與歌曲列表, 302 行)
    7. MusicSearchView (搜尋框與搜尋邏輯, 142 行)
    8. MusicHeaderView (頂部標題和按鈕, 160 行)
    9. MusicPlaybackView (播放控制 UI, 342 行)
    10. MusicSongActions (歌曲操作, 248 行)
    11. MusicFolderActions (資料夾操作, 193 行)
  - ✅ **測試大幅擴充**: 155 → 339 個測試 (+119%)
  - ✅ **測試覆蓋率達標**: 68% (超過 60% 目標)
  - ✅ **測試通過率**: 99.4% (337/339)
  - ✅ **技術債務消除**: music_window.py 不再是技術債務
  - ✅ **程式碼品質**: Flake8 零錯誤 + Git hooks
  - ✅ **TDD 實踐**: Overnight Development + 完整測試套件

**🆕 新功能 (2025-10-13)**:
  - 🎵 **自動補全音樂資訊**
    - 播放時自動檢測缺失的封面/藝術家/專輯
    - 從 iTunes API 自動抓取高解析度封面 (600x600)
    - 背景執行不阻塞 UI
    - 可在設定頁面啟用/停用

  - 🎤 **同步歌詞顯示** (2025-10-14)
    - 支援 LRC 格式歌詞檔案 (`.lrc`)
    - 自動同步播放位置高亮顯示
    - 點擊歌詞行可跳轉到對應時間點
    - **使用方式**: 將 `.lrc` 歌詞檔案放在音樂檔案相同目錄，且檔名與音樂檔案相同
      - 例如: `Song.mp3` 對應 `Song.lrc`
    - **注意**: 目前不支援自動下載歌詞，需要手動取得 LRC 檔案

  - 🎚️ **10 頻段等化器** (2025-10-14)
    - 10 個可調整頻段 (60Hz - 16kHz)
    - 增益範圍: -12dB 到 +12dB
    - 8 種預設模式: 平坦、流行、搖滾、古典、爵士、人聲、重低音、柔和
    - 設定自動儲存到 config.json
    - **注意**: 當前版本僅實現設定管理，音訊效果應用需要未來整合音訊處理庫

詳細更新日誌請參考 `CHANGELOG.md`。

## 常見問題

**Q: 為什麼切換後沒有反應?**
A: 請確認：
1. 已在設定中選擇兩個不同的裝置
2. 選擇的裝置目前是啟用狀態
3. 以管理員權限執行程式

**Q: 能否支援超過兩個裝置?**
A: 目前版本僅支援兩個裝置間切換,這是為了保持簡單易用。未來版本可能會加入更多裝置支援。

**Q: 開機自啟動沒有作用?**
A: 請檢查 Windows 工作管理員 → 啟動項目,確認 AudioSwitcher 是否已加入。

**Q: 如何使用歌詞功能?**
A: 歌詞功能需要手動準備 LRC 格式的歌詞檔案:
1. 取得音樂對應的 LRC 歌詞檔案 (可從網路下載或自行製作)
2. 將 `.lrc` 檔案放在音樂檔案相同目錄
3. 確保歌詞檔名與音樂檔名相同 (副檔名除外)
   - 例如: `//ShuviNAS/Shuvi/J-Pop/Song.mp3` 對應 `//ShuviNAS/Shuvi/J-Pop/Song.lrc`
4. 播放音樂時會自動載入並同步顯示歌詞

**注意**: 目前不支援從 YouTube 下載時自動下載歌詞，未來可能會加入此功能。

**Q: 等化器設定後為什麼沒有效果?**
A: 當前版本的等化器僅實現設定管理功能，實際的音訊效果應用需要整合額外的音訊處理庫。目前可以：
- 調整各頻段增益並儲存
- 選擇不同的預設模式
- 設定會自動保存到 config.json

未來版本計畫整合 pydub 或 sounddevice 來實現真正的音訊效果應用。

**Q: YouTube 下載遇到 403 錯誤怎麼辦?**
A: 這是 YouTube 的反爬蟲機制。專案已實作以下規避策略:

**核心設定 (已內建於程式):**
1. ✅ **yt-dlp 版本**: 使用 2025.09.26 最新版本
2. ✅ **mweb 客戶端**: 使用 `player_client=mweb,android` (2025 年最新建議)
3. ✅ **跳過串流格式**: `skip=hls,dash` 減少請求次數
4. ✅ **網路優化**: `source_address=0.0.0.0` 綁定網路介面
5. ✅ **重試機制**: 自動重試 3 次
6. ✅ **Cookie 支援**: 自動嘗試使用 Chrome/Edge/Firefox cookies

**如果仍失敗:**
1. **更新 yt-dlp** (最重要!): `pip install --upgrade yt-dlp`
2. **登入 YouTube**: 在 Chrome 瀏覽器登入 YouTube 帳號
3. **定期更新**: YouTube 會不定期更新防護,建議每月更新一次 yt-dlp

詳細技術說明請參考 `YOUTUBE_403_FIX_GUIDE.md`

## 授權

MIT License

## 貢獻

歡迎提交 Issue 或 Pull Request！

## 更新日誌

### v1.0.0 (2025-10-04)
- 初始版本發布
- 支援雙裝置快速切換
- 系統托盤整合
- 圖形化設定介面
- 開機自啟動功能
