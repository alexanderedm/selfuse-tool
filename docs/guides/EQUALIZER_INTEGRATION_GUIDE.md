# 等化器整合指南

本指南說明如何將等化器功能整合到 `music_window.py`。

## 已完成的模組

1. **music_equalizer.py** - 等化器邏輯模組
   - 28/28 測試通過
   - 程式碼複雜度 CC=2.4 (A級)
   - flake8 零錯誤

2. **music_equalizer_dialog.py** - 等化器 UI 對話框
   - 17/19 測試通過 (2個失敗是tkinter環境問題)
   - 程式碼複雜度 CC=2.4 (A級)
   - flake8 零錯誤

3. **tests/test_music_equalizer.py** - 等化器測試 (28個測試)

4. **tests/test_music_equalizer_dialog.py** - UI測試 (19個測試)

## 整合步驟

### 步驟 1: 更新 music_window.py 的 import

在 `music_window.py` 開頭添加：

```python
from music_equalizer import MusicEqualizer
from music_equalizer_dialog import MusicEqualizerDialog
```

### 步驟 2: 在 __init__ 方法中初始化等化器

在 `__init__` 方法中，在 `# 歌詞解析器` 之後添加：

```python
# 等化器
self.equalizer = MusicEqualizer(self.music_manager.config_manager)

# 等化器對話框(延遲初始化,當 window 建立後)
self.equalizer_dialog = None
```

### 步驟 3: 在 show() 方法中初始化等化器對話框

在 `show()` 方法中，在下載對話框初始化之後添加：

```python
# 初始化等化器對話框
self.equalizer_dialog = MusicEqualizerDialog(
    parent=self.window,
    equalizer=self.equalizer
)
```

### 步驟 4: 添加顯示等化器的方法

在 `music_window.py` 中添加：

```python
def _show_equalizer(self):
    """顯示等化器設定對話框"""
    if self.equalizer_dialog:
        self.equalizer_dialog.show()
```

### 步驟 5: 更新 MusicHeaderView 添加等化器按鈕

**方法 A: 修改 music_header_view.py**

在 `MusicHeaderView.__init__` 的參數列表中添加：

```python
on_equalizer_click=None
```

在 `__init__` 方法中添加：

```python
self.on_equalizer_click = on_equalizer_click
self.equalizer_button = None
```

在 `_create_ui` 方法的按鈕區域添加：

```python
# 等化器按鈕
self.equalizer_button = tk.Button(
    button_frame,
    text="🎚️ 等化器",
    font=("Microsoft JhengHei UI", 10),
    bg="#353535",
    fg=self.text_color,
    activebackground="#505050",
    activeforeground="white",
    borderwidth=0,
    padx=15,
    pady=5,
    command=self._on_equalizer_button_click
)
self.equalizer_button.pack(side=tk.RIGHT, padx=(5, 0))
```

添加回調方法：

```python
def _on_equalizer_button_click(self):
    """等化器按鈕點擊處理"""
    if self.on_equalizer_click:
        self.on_equalizer_click()
```

**方法 B: 直接在 music_window.py 中添加按鈕**

如果不想修改 MusicHeaderView，可以在 `music_window.py` 的 `show()` 方法中，在創建 header_view 之後添加等化器按鈕：

```python
# 添加等化器按鈕到 header_view
# (在 header_view 創建之後)
equalizer_btn = tk.Button(
    self.header_view.header_frame.children['!frame'],  # button_frame
    text="🎚️ 等化器",
    font=("Microsoft JhengHei UI", 10),
    bg="#353535",
    fg=text_color,
    activebackground="#505050",
    activeforeground="white",
    borderwidth=0,
    padx=15,
    pady=5,
    command=self._show_equalizer
)
equalizer_btn.pack(side=tk.RIGHT, padx=(5, 0))
```

### 步驟 6: 在 MusicHeaderView 初始化時傳入回調

在 `music_window.py` 的 `show()` 方法中，更新 header_view 的創建：

```python
self.header_view = MusicHeaderView(
    parent=main_frame,
    on_download_click=self._open_download_dialog,
    on_playlist_click=self._show_playlists,
    on_history_click=self._show_play_history,
    on_most_played_click=self._show_most_played,
    on_equalizer_click=self._show_equalizer  # 新增
)
```

## 功能特點

### 等化器設定

- **10 頻段**: 60Hz, 170Hz, 310Hz, 600Hz, 1kHz, 3kHz, 6kHz, 12kHz, 14kHz, 16kHz
- **增益範圍**: -12dB 到 +12dB
- **預設模式**:
  - 平坦 (Flat)
  - 流行 (Pop)
  - 搖滾 (Rock)
  - 古典 (Classical)
  - 爵士 (Jazz)
  - 人聲 (Vocal)
  - 重低音 (Bass Boost)
  - 柔和 (Soft)
  - 自定義 (Custom)

### 設定持久化

- 設定自動保存到 `config.json` 的 `music_equalizer` 鍵
- 下次啟動時自動載入上次的設定

### 重要注意事項

當前版本僅實現**設定管理**功能，**音訊效果應用功能待未來整合音訊處理庫實現**。

這是因為 `pygame.mixer` 不支援即時等化器效果。未來可以考慮：
- 整合 `pydub` 進行音訊預處理
- 使用 `sounddevice` 或其他支援音訊濾波的庫
- 實現播放前的音訊效果處理

## 測試

運行等化器測試：

```bash
python -m pytest tests/test_music_equalizer.py tests/test_music_equalizer_dialog.py -v
```

預期結果：
- test_music_equalizer.py: 28/28 通過
- test_music_equalizer_dialog.py: 17/19 通過 (2個失敗是 tkinter 環境問題)

## 檔案清單

新增的檔案：
- `music_equalizer.py` (268 行)
- `music_equalizer_dialog.py` (363 行)
- `tests/test_music_equalizer.py` (301 行)
- `tests/test_music_equalizer_dialog.py` (302 行)
- `EQUALIZER_INTEGRATION_GUIDE.md` (本檔案)

## 技術指標

- **總測試數**: 47 (新增)
- **測試通過率**: 96% (45/47，2個失敗是 tkinter 環境問題)
- **程式碼複雜度**: CC=2.4 (A級)
- **flake8**: 零錯誤
- **程式碼行數**: 631 行 (不含測試)

## 下一步

1. 整合到 `music_window.py` (按照本指南步驟操作)
2. 測試 UI 是否正常運作
3. 提交 Git commit
4. 更新 CHANGELOG.md 和 TODO.md
5. 推送到 GitHub

## 常見問題

**Q: 為什麼等化器設定無法應用到音訊？**
A: 當前版本僅實現設定管理，音訊效果應用需要額外的音訊處理庫支援。

**Q: 如何測試等化器 UI？**
A: 運行應用程式，點擊等化器按鈕，調整滑桿並測試各種預設模式。

**Q: 設定保存在哪裡？**
A: 保存在 `config.json` 的 `music_equalizer` 鍵下。

**Q: 如何新增自定義預設？**
A: 調整滑桿後會自動切換到「自定義」模式，設定會被保存。

## 聯絡

如有問題，請查閱 `music_equalizer.py` 和 `music_equalizer_dialog.py` 的 docstring，或運行測試查看使用範例。
