# Selftool - 音訊設備切換工具

<div align="center">

**一個功能豐富的 Windows 系統托盤工具**

輕鬆切換音訊設備 • 本地音樂播放器 • RSS 閱讀器 • AI 瀏覽器助手

[快速開始](getting-started/installation.md){ .md-button .md-button--primary }
[GitHub](https://github.com/your-username/selfuse-tool){ .md-button }

</div>

---

## ✨ 功能特色

### 🎧 音訊切換
一鍵在兩個預設音訊裝置之間快速切換，支援系統托盤整合與視覺回饋。

### 🎵 音樂播放器
完整功能的本地音樂播放器，支援 MP3、FLAC、WAV 格式，內建歌詞同步顯示、元數據自動補全、YouTube 下載等功能。

### 📰 RSS 閱讀器
訂閱管理 RSS 來源，支援文章過濾、搜尋與離線閱讀。

### 🤖 AI 瀏覽器助手
基於 Chrome DevTools MCP 的 AI 瀏覽器自動化助手，支援智慧網頁操作。

### 🔋 設備監控
顯示羅技/藍牙耳機電量，即時監控設備狀態。

### 📊 使用統計
追蹤音訊設備使用時間與切換次數，提供詳細的使用分析。

---

## 🚀 快速開始

### 系統需求

- Windows 10/11（或 Windows 7/8，部分功能可能不穩定）
- Python 3.8 或更高版本（開發模式）

### 安裝方式

=== "下載可執行檔（推薦）"

    1. 前往 [Releases 頁面](https://github.com/your-username/selfuse-tool/releases)
    2. 下載最新版本的 `selftool-vX.X.X-windows-x64.zip`
    3. 解壓縮並執行 `selftool.exe`

=== "從原始碼執行"

    ```bash
    # 克隆專案
    git clone https://github.com/your-username/selfuse-tool.git
    cd selfuse-tool

    # 安裝依賴
    pip install -r requirements.txt

    # 執行程式
    python src/main.py
    ```

---

## 📖 使用指南

### 首次設定

1. 執行程式後，系統托盤會出現圖示
2. 右鍵點擊圖示，選擇「設定」
3. 選擇兩個要切換的音訊裝置（裝置 A 和裝置 B）
4. 設定會自動儲存

### 日常操作

| 功能 | 操作 |
|------|------|
| 切換裝置 | 右鍵 → 「切換輸出裝置」 |
| 查看電量 | 右鍵 → 選單自動顯示 |
| 開啟音樂播放器 | 右鍵 → 「🎵 本地音樂播放器」 |
| 開啟 RSS 閱讀器 | 右鍵 → 「📰 RSS 閱讀器」 |
| AI 瀏覽器助手 | 右鍵 → 「🤖 AI 瀏覽器助手」 |
| 查看統計 | 右鍵 → 「📊 使用統計」 |
| 修改設定 | 右鍵 → 「⚙️ 設定」 |

### 托盤圖示顏色

- 🔵 **藍色**：目前使用裝置 A
- 🟢 **綠色**：目前使用裝置 B
- ⚫ **灰色**：使用其他裝置或未設定

---

## 🎯 核心特點

### 高品質程式碼

- ✅ 平均複雜度：CC=2.72（A 級）
- ✅ 測試覆蓋率：92%（569 個測試）
- ✅ flake8 零錯誤
- ✅ 可維護性指數：MI > 20（所有文件）

### 模組化架構

專案採用清晰的模組化設計，將音訊、音樂、RSS、UI 等功能完全分離，便於維護與擴展。

### 持續改進

遵循語意化版本控制（SemVer），定期發布更新，修復問題並新增功能。

---

## 📚 文檔導航

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __快速開始__

    ---

    學習如何安裝與設定 Selftool

    [:octicons-arrow-right-24: 安裝指南](getting-started/installation.md)

-   :material-star-circle:{ .lg .middle } __功能介紹__

    ---

    探索所有強大功能

    [:octicons-arrow-right-24: 功能列表](features/audio-switching.md)

-   :material-code-braces:{ .lg .middle } __開發文檔__

    ---

    了解專案結構與貢獻方式

    [:octicons-arrow-right-24: 開發指南](development/structure.md)

-   :material-history:{ .lg .middle } __更新日誌__

    ---

    查看版本更新與變更記錄

    [:octicons-arrow-right-24: CHANGELOG](changelog.md)

</div>

---

## 💡 支援與反饋

遇到問題或有建議？歡迎在 [GitHub Issues](https://github.com/your-username/selfuse-tool/issues) 提出！

---

<div align="center">

**用 ❤️ 打造 | MIT License**

[GitHub](https://github.com/your-username/selfuse-tool) •
[文檔](https://your-username.github.io/selfuse-tool) •
[發布](https://github.com/your-username/selfuse-tool/releases)

</div>
