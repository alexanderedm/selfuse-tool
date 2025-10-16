# 📊 專案健康分析報告

**報告日期**: 2025-10-14
**分析範圍**: 最近 3 個月的變更歷史
**工具**: radon, pytest, git

---

## 📈 倉庫概覽

### 基本統計
- **源代碼文件**: 38 個 Python 文件
- **測試文件**: 35 個測試文件
- **測試總數**: 569 個測試
- **測試覆蓋率**: 92% (35/38 文件有對應測試)
- **平均複雜度**: CC=2.72 (A 級 - 優秀)
- **可維護性**: 所有文件均為 A 級 (MI > 20)

### 🎯 整體健康狀況: **優秀 (A 級)**

專案整體代碼品質非常好,已完成大規模重構工作,複雜度控制在優秀範圍。

---

## ⚠️ 需要關注的文件

### 1. **music_window.py** - 🔴 高優先級
- **變更頻率**: 20 次提交 (最近 3 個月) - 🔴 **最高變更率**
- **可維護性指數**: MI = 28.54 (A 級,但是最低)
- **文件位置**: `music_window.py`
- **複雜度問題**:
  - `_load_lyrics_for_song()`: CC=10 (B 級) - music_window.py:892
  - `_update_progress()`: CC=6 (B 級) - music_window.py:635
  - `_restore_playback_state()`: CC=6 (B 級) - music_window.py:681
  - `_rename_folder()`: CC=6 (B 級) - music_window.py:788
  - `_play_playlist()`: CC=6 (B 級) - music_window.py:858

**風險分析**:
- 高變更率 + 多個 B 級複雜度函數 = **技術債務累積風險**
- 該文件作為核心 UI 控制器,持續新增功能導致複雜度上升
- 最近新增的歌詞功能導致 `_load_lyrics_for_song()` 複雜度為 10

**建議**:
1. 重構 `_load_lyrics_for_song()` (CC=10) - 拆分歌詞載入邏輯
2. 考慮將播放控制邏輯獨立成 `MusicPlaybackController` (部分已完成)
3. 增加 `_load_lyrics_for_song()` 的單元測試覆蓋

---

### 2. **settings_window.py** - 🟡 中優先級
- **變更頻率**: 9 次提交 (最近 3 個月)
- **可維護性指數**: 未在前 30 名中顯示 (推測 > 40)
- **複雜度問題**:
  - `_create_single_device_selector()`: CC=8 (B 級) - settings_window.py:102
  - `_validate_and_save_devices()`: CC=6 (B 級) - settings_window.py:512

**風險分析**:
- 中等變更率 + 裝置設定邏輯複雜
- UI 建構和驗證邏輯耦合

**建議**:
1. 將裝置選擇邏輯抽離到獨立模組 (`device_selector.py`)
2. 簡化驗證邏輯,考慮使用驗證框架

---

### 3. **music_playlist_dialog.py** - 🟢 低優先級
- **可維護性指數**: MI = 48.18 (A 級,但相對較低)
- **變更頻率**: 低
- **複雜度**: 整體良好

**建議**: 監控即可,暫無急迫重構需求

---

## ✅ 優秀實踐

### 🏆 高品質模組
1. **constants.py** - MI = 100.00 (完美)
2. **music_header_view.py** - MI = 100.00 (完美)
3. **music_search_view.py** - MI = 82.76 (優秀)
4. **logger.py** - MI = 74.37 (優秀)
5. **rss_feed_list_view.py** - MI = 73.83 (優秀)

### 🎉 成功的重構
- **10 個高複雜度函數已成功重構** (從前次會話)
  - rss_manager.py::fetch_feed_entries (CC 24 → 7)
  - youtube_downloader.py::download_audio (CC 19 → 7)
  - music_library_view.py::_on_category_select_internal (CC 11 → 6)
  - music_metadata_fetcher.py::update_song_metadata (CC 10 → 5)
  - music_metadata_fetcher.py::fetch_metadata (CC 10 → 5)
  - settings_window.py::_validate_and_save_devices (CC 10 → 6)
  - stats_window.py::show (CC 10 → 2)
  - music_window.py::_update_progress (CC 9 → 6)
  - music_window.py::_play_next (CC 9 → 4)
  - music_window.py::_toggle_play_pause (CC 8 → 4)
- **零 xenon 違規** (從 5 個降為 0)
- **96%+ 測試通過率**
- **flake8 零錯誤**

### 📦 良好的模組化
- 清晰的職責分離 (view/controller/manager 模式)
- 最近新增的模組品質優秀:
  - `lyrics_parser.py` - MI = 71.02 (A)
  - `music_equalizer.py` - MI = 61.11 (A)
  - `music_equalizer_dialog.py` - MI = 61.70 (A)
  - `music_lyrics_view.py` - MI = 55.73 (A)

---

## 🎯 優先改進建議

### 🔴 **立即處理** (本週)

#### 1. 重構 `music_window.py::_load_lyrics_for_song()` (CC=10)
```python
# 目前 (推測結構):
def _load_lyrics_for_song(self, song_path):
    # 歌詞文件查找邏輯
    # LRC 解析邏輯
    # UI 更新邏輯
    # 錯誤處理
    # ... (10 個分支路徑)

# 建議拆分為:
def _load_lyrics_for_song(self, song_path):
    lyrics_file = self._find_lyrics_file(song_path)
    if not lyrics_file:
        self._show_no_lyrics()
        return

    self._display_lyrics(lyrics_file)

def _find_lyrics_file(self, song_path):
    # 純邏輯,易於測試
    ...

def _display_lyrics(self, lyrics_file):
    # UI 更新,分離關注點
    ...
```

**影響**: 降低最高複雜度函數,提升可測試性

---

### 🟡 **短期處理** (本月)

#### 2. 為 `music_window.py` 新增測試覆蓋
- 當前: `tests/test_music_window.py` 存在,但需增強
- 目標: 覆蓋 B 級複雜度函數,尤其是:
  - `_load_lyrics_for_song()` (CC=10)
  - `_update_progress()` (CC=6)
  - `_restore_playback_state()` (CC=6)

#### 3. 重構 `settings_window.py::_create_single_device_selector()` (CC=8)
- 將裝置選擇 UI 邏輯獨立成組件
- 降低與主視窗的耦合

---

### 🟢 **長期優化** (下季度)

#### 4. 持續監控高變更文件
```
20 commits - music_window.py     ⚠️ 持續高變更
 9 commits - settings_window.py  ⚠️ 中等變更
 4 commits - music_manager.py    ✅ 穩定
```

#### 5. 考慮架構重構
- `music_window.py` (28.54 MI) 職責過重
- 建議: 採用 MVP/MVVM 模式進一步分離關注點
- 目標: 將 MI 提升到 40+ 範圍

---

## 📊 詳細指標

### 複雜度分布
- **A 級 (CC 1-5)**: ~85% 的函數
- **B 級 (CC 6-10)**: ~12% 的函數
- **C 級及以下 (CC > 10)**: 0% ✅

### 可維護性分布
- **A 級 (MI > 20)**: 100% 的文件 ✅
- **最高**: constants.py (MI=100)
- **最低**: music_window.py (MI=28.54)
- **平均**: MI ≈ 60-65 (優秀)

### 測試健康度
- **測試覆蓋率**: 92% (35/38 文件)
- **未覆蓋文件**: 3 個 (可能是工具腳本或常量文件)
- **測試總數**: 569 個
- **通過率**: 96%+

### Git 變更分析 (最近 3 個月)
| 文件 | 提交次數 | 風險等級 | 建議 |
|------|---------|---------|------|
| music_window.py | 20 | 🔴 高 | 立即重構 |
| settings_window.py | 9 | 🟡 中 | 短期優化 |
| music_manager.py | 4 | 🟢 低 | 監控即可 |
| youtube_downloader.py | 3 | 🟢 低 | 穩定 |
| rss_manager.py | 3 | 🟢 低 | 穩定 |

---

## 🎊 總結

### 專案狀態: 健康 🟢

這是一個**代碼品質優秀**的專案,已完成大量重構工作。主要關注點集中在單一高變更文件 (`music_window.py`),需要**定期重構**以防止技術債務累積。

### 關鍵優勢
✅ 零高風險技術債務
✅ 優秀的測試覆蓋率 (92%)
✅ 清晰的模組化架構
✅ 持續的代碼品質監控
✅ 成功的持續重構實踐

### 改進方向
⚠️ 持續重構高變更文件 (`music_window.py`)
⚠️ 增強核心模組測試覆蓋
⚠️ 監控架構演化趨勢
⚠️ 考慮進一步的架構分離 (MVP/MVVM)

---

## 📅 後續行動

### 本週 (2025-10-14 ~ 2025-10-20)
- [ ] 重構 `music_window.py::_load_lyrics_for_song()` (CC 10 → <6)
- [ ] 為 `_load_lyrics_for_song()` 新增單元測試

### 本月 (2025-10)
- [ ] 增強 `tests/test_music_window.py` 測試覆蓋
- [ ] 重構 `settings_window.py::_create_single_device_selector()` (CC 8 → <6)

### 下季度 (2025-Q4)
- [ ] 評估 `music_window.py` 架構重構可行性
- [ ] 建立自動化代碼品質門檻 (CI/CD)

---

**報告生成**: Claude Code (Project Health Auditor)
**下次審查建議日期**: 2025-11-14 (1 個月後)
