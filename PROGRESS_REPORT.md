# Music Window 瘦身進度報告

## 目標
將 music_window.py 從 1370 行減少到 < 800 行

## 當前進度

### 已完成階段

#### 階段 1: 整合 MusicPlaybackView ✅
- **減少行數**: 275 行 (1370 → 1095)
- **完成項目**:
  - ✅ 導入 MusicPlaybackView 模組
  - ✅ 移除播放控制 UI 建立代碼 (172 行)
  - ✅ 移除重複的專輯封面方法 (103 行)
    - _load_album_cover
    - _get_default_cover_image
    - _update_album_cover
  - ✅ 更新所有 UI 操作使用 playback_view
  - ✅ 簡化 _update_progress 方法
  - ✅ 簡化 _restore_playback_state 方法
- **測試結果**: ✅ 8 passed, 1 skipped
- **Flake8**: ✅ 0 errors

### 剩餘目標
- **當前行數**: 1095
- **目標行數**: < 800
- **還需減少**: 295 行 (27%)

### 下一階段計劃

#### 階段 2: 抽離 MusicSongActions 模組 (預計減少 150-200 行)
抽離歌曲操作相關程式碼:
- _on_song_double_click
- _play_song_from_tree
- _play_song_from_playlist
- _add_song_to_playlist
- _delete_song
- _move_song_to_category (包含對話框，約 100 行)

#### 階段 3: 抽離 MusicFolderActions 模組 (預計減少 100-150 行)
抽離資料夾操作相關程式碼:
- _create_new_folder
- _rename_folder
- _delete_folder
- _on_category_right_click (右鍵選單)

#### 階段 4: 抽離或優化其他部分 (預計減少 50-100 行)
- 簡化 _on_category_select, _on_category_double_click
- 抽離或優化搜尋相關程式碼
- 其他重複程式碼優化

## 技術債務與改進
- ✅ 移除重複的圖片處理程式碼
- ✅ 統一使用 playback_view 更新 UI
- ⏳ 待處理: 歌曲和資料夾操作邏輯分離
- ⏳ 待處理: 對話框管理統一

## 品質指標
- **測試覆蓋率**: 68%
- **總測試數**: 317 個
- **Flake8 錯誤**: 0
- **程式碼品質**: ✅ 良好
