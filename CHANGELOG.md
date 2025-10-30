# Changelog

本文件記錄專案的所有重要變更。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [Unreleased]

### Added
- 🌐 AI 瀏覽器助手網頁版 UI（FastAPI + HTML/JS）
  - 現代化深色主題介面
  - WebSocket 即時日誌推送
  - 敏感操作確認對話框
  - 自動啟動伺服器並開啟瀏覽器
- 建立自動發布系統（GitHub Actions）
- 建立 MkDocs 文檔系統
- RSS 多執行緒優化
- 安全的 API Key 配置系統

### Changed
- 🔄 AI 瀏覽器助手從 CustomTkinter 改為網頁 UI
  - 解決啟動問題（參數傳遞、進程管理、視窗顯示）
  - 更好的跨平台相容性
  - 更容易開發和調試
  - 無需獨立 tkinter 進程

### Fixed
- 🔧 **重大修復**：AI 瀏覽器助手 OpenAI API 呼叫問題
  - 修復 `json_schema` 工具類型錯誤（應使用 `function`）
  - 這是導致「Please provide an OpenAI API key」誤導性錯誤的根本原因
  - 修正所有 JSON Schema 格式（orchestrator, web_orchestrator）
  - 修復 MCP client 在 Windows 上的 SIGINT 信號問題（改用 `terminate()`）
- 修復 AI 瀏覽器助手在 Windows 控制台的 Unicode 編碼問題
- 修復 MCP 客戶端啟動失敗時的錯誤處理

## [1.0.0] - 2025-10-28

### Added
- 🎧 音訊輸出裝置快速切換功能
- 🎵 本地音樂播放器（支援 MP3、FLAC、WAV）
- 📰 RSS 訂閱閱讀器
- 🤖 AI 瀏覽器助手（基於 Chrome DevTools MCP）
- 🔋 羅技/藍牙耳機電量顯示
- 📊 裝置使用統計功能
- 🎨 深色主題 UI 設計
- 📝 更新日誌視窗
- 🎼 音樂歌詞同步顯示（LRC 格式）
- 🎨 Discord Rich Presence 整合
- 🔍 智慧音樂搜尋與過濾
- 📥 YouTube 音樂下載功能
- 🎯 音樂元數據自動補全（YouTube Music + iTunes）
- 📱 系統托盤整合

### Fixed
- 修復開機自啟動導致程式崩潰的問題（已移除此功能）
- 修復 AI 瀏覽器助手啟動失敗問題
- 修復 RSS 文章無法顯示的問題
- 修復音樂元數據更新 JSON 檔案的 Bug
- 修復歌詞顯示同步問題

### Changed
- 移除開機自啟動功能（Windows 兼容性問題）
- 優化設定視窗為即時儲存模式
- 所有視窗點擊 X 按鈕時隱藏而非關閉
- 改進 UI 滾動功能（設定、統計視窗）

### Technical
- 專案結構模組化重構
- 程式碼品質：平均複雜度 CC=2.72（A 級）
- 測試覆蓋率：92%（569 個測試）
- flake8 零錯誤
- 可維護性指數 MI > 20（所有文件）

## [0.1.0] - 2024-01-16

### Added
- 初始版本發布
- 基本音訊切換功能
- 系統托盤圖示

---

[Unreleased]: https://github.com/your-username/selfuse-tool/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-username/selfuse-tool/releases/tag/v1.0.0
[0.1.0]: https://github.com/your-username/selfuse-tool/releases/tag/v0.1.0
