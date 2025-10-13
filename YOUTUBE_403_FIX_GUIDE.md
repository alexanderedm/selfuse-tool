# 🎵 YouTube 403 錯誤規避指南

**適用於:** yt-dlp 音樂播放機器人
**最後更新:** 2025-10-12

---

## 📋 快速摘要

本專案透過以下 **6 個關鍵設定** 成功規避 YouTube 的 403 錯誤:

1. ✅ **多客戶端策略** - 使用 Android + Web 雙客戶端
2. ✅ **靈活格式選擇** - 自動選擇最佳可用格式
3. ✅ **網路設定優化** - 調整來源地址與憑證檢查
4. ✅ **充足超時時間** - 45 秒讓 yt-dlp 嘗試多種策略
5. ✅ **完善錯誤處理** - 優雅處理失敗情況
6. ✅ **Cookie 支援預留** - 可升級使用瀏覽器 Cookie

---

## 🔧 實作方法

### 完整配置 (直接使用)

在你的 `yt-dlp` 配置中加入以下設定:

```python
import yt_dlp

YTDL_OPTIONS = {
    # 基本設定
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'noplaylist': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',

    # 🔑 關鍵設定 1: 多客戶端策略
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],  # Android 客戶端較不易被封鎖
            'skip': ['hls', 'dash']                # 跳過串流格式
        }
    },

    # 🔑 關鍵設定 2: 網路優化
    'source_address': '0.0.0.0',      # 綁定預設網路介面
    'nocheckcertificate': True,       # 避免憑證問題

    # 🔑 關鍵設定 3: Cookie 支援 (選用)
    'cookiesfrombrowser': None,       # 可設為 ('chrome', None) 使用 Chrome Cookie
}

# 創建 YoutubeDL 實例
ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)
```

### 搭配超時處理 (推薦)

```python
import asyncio

async def search_song(query: str, timeout: float = 45.0):
    """搜尋歌曲並處理超時"""
    loop = asyncio.get_event_loop()

    try:
        # 🔑 關鍵設定 4: 45 秒超時
        data = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: ytdl.extract_info(query, download=False)
            ),
            timeout=timeout
        )
        return data

    except asyncio.TimeoutError:
        print(f"⏱️ 搜尋超時: {query}")
        return None

    except Exception as e:
        print(f"❌ 搜尋錯誤: {e}")
        return None
```

---

## 📖 設定說明

### 1. Player Client 切換

```python
'player_client': ['android', 'web']
```

**作用:**
- YouTube 對不同客戶端的限制程度不同
- `android` 客戶端通常較不易被封鎖
- `web` 客戶端作為備用
- yt-dlp 會自動嘗試兩者

**為什麼有效:**
- Android 客戶端的請求特徵與行動裝置相似
- YouTube 對行動裝置的限制較寬鬆

---

### 2. 跳過串流格式

```python
'skip': ['hls', 'dash']
```

**作用:**
- 跳過 HLS (HTTP Live Streaming) 和 DASH 格式
- 直接使用傳統格式,更穩定可靠

**為什麼有效:**
- 串流格式需要額外的請求,增加被封鎖機率
- 傳統格式請求次數較少

---

### 3. 來源地址設定

```python
'source_address': '0.0.0.0'
```

**作用:**
- 綁定到系統的預設網路介面
- 避免特定 IP 被限速或封鎖

**為什麼有效:**
- 確保請求從正確的網路介面發出
- 有助於多網卡環境的穩定性

---

### 4. SSL 憑證檢查

```python
'nocheckcertificate': True
```

**作用:**
- 不檢查 SSL 憑證有效性
- 避免憑證問題導致連線失敗

**注意:**
- 這會降低安全性
- 僅在必要時使用
- 本專案用於內部 Discord 機器人,風險可控

---

### 5. 音頻格式選擇

```python
'format': 'bestaudio/best'
```

**作用:**
- 優先選擇最佳音頻格式
- 若無獨立音頻,則選擇最佳混合格式

**為什麼有效:**
- 不強制要求特定格式
- 讓 yt-dlp 智能選擇可用的最佳選項

---

### 6. Cookie 支援 (進階)

```python
'cookiesfrombrowser': None  # 或 ('chrome', None)
```

**未來升級選項:**

如果遇到更嚴格的限制,可以啟用 Cookie 支援:

```python
# 使用 Chrome 的 Cookie
'cookiesfrombrowser': ('chrome', None)

# 或使用 Firefox
'cookiesfrombrowser': ('firefox', None)
```

**作用:**
- 從瀏覽器讀取已登入的 Cookie
- 讓請求看起來像正常使用者

**注意:**
- 需要在該瀏覽器登入 YouTube
- 可能需要定期更新 Cookie

---

## 🎯 使用範例

### 基礎使用

```python
import yt_dlp

# 使用上述配置
ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

# 提取影片資訊
info = ytdl.extract_info('https://www.youtube.com/watch?v=dQw4w9WgXcQ', download=False)

# 獲取音頻 URL
audio_url = info['url']
title = info['title']
duration = info['duration']

print(f"標題: {title}")
print(f"時長: {duration} 秒")
print(f"音頻 URL: {audio_url}")
```

### 搜尋並播放

```python
# 搜尋功能
search_query = 'ytsearch5:imagine dragons'
results = ytdl.extract_info(search_query, download=False)

for entry in results['entries']:
    print(f"- {entry['title']} ({entry['duration']}s)")
```

### Discord 機器人整合

```python
import discord
from discord.ext import commands

async def play_song(ctx, query: str):
    """Discord 音樂播放範例"""

    # 搜尋歌曲
    data = await search_song(query)

    if not data:
        await ctx.send("❌ 找不到歌曲或搜尋失敗")
        return

    # 獲取音頻 URL
    if 'entries' in data:
        # 搜尋結果
        info = data['entries'][0]
    else:
        # 直接 URL
        info = data

    # 播放音頻
    audio_source = discord.FFmpegPCMAudio(info['url'])
    ctx.voice_client.play(audio_source)

    await ctx.send(f"🎵 正在播放: {info['title']}")
```

---

## 🐛 常見問題

### Q1: 還是遇到 403 錯誤怎麼辦?

**解決方案:**

1. **確認 yt-dlp 是最新版本**
   ```bash
   pip install --upgrade yt-dlp
   ```

2. **啟用 Cookie 支援**
   ```python
   'cookiesfrombrowser': ('chrome', None)
   ```

3. **檢查網路環境**
   - 確認沒有使用 VPN 或代理
   - 某些網路環境可能被 YouTube 限制

4. **增加重試機制**
   ```python
   for attempt in range(3):
       try:
           data = ytdl.extract_info(url, download=False)
           break
       except Exception as e:
           if attempt == 2:
               raise e
           await asyncio.sleep(2)
   ```

---

### Q2: 超時時間應該設多少?

**建議:**
- **一般情況:** 30-45 秒
- **搜尋查詢:** 45 秒
- **直接 URL:** 30 秒
- **播放清單:** 60 秒

```python
timeout = 45.0  # 推薦值
```

---

### Q3: 如何知道是否成功規避 403?

**檢查方式:**

1. **查看日誌輸出**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **測試不同影片**
   - 公開影片
   - 年齡限制影片
   - 音樂影片

3. **監控錯誤率**
   ```python
   success_count = 0
   error_count = 0

   # 記錄統計
   if data:
       success_count += 1
   else:
       error_count += 1
   ```

---

## 📊 效能影響

| 設定項目 | 效能影響 | 成功率提升 |
|---------|---------|-----------|
| Player Client 切換 | ⚡ 幾乎無 | ⭐⭐⭐⭐⭐ 極高 |
| 跳過串流格式 | ⚡ 略快 | ⭐⭐⭐⭐ 高 |
| 來源地址設定 | ⚡ 無 | ⭐⭐⭐ 中 |
| 停用憑證檢查 | ⚡ 略快 | ⭐⭐ 低 |
| Cookie 支援 | 🐌 略慢 | ⭐⭐⭐⭐⭐ 極高 |

---

## 🔗 相關資源

- **yt-dlp GitHub:** https://github.com/yt-dlp/yt-dlp
- **yt-dlp 文檔:** https://github.com/yt-dlp/yt-dlp#usage-and-options
- **本專案音樂模組:** [cogs/music.py](cogs/music.py#L14-L38)

---

## 📝 版本紀錄

### 2025-10-12
- ✅ 初版發布
- ✅ 包含 6 個核心設定
- ✅ 提供完整使用範例

---

## 💡 小技巧

1. **定期更新 yt-dlp**
   ```bash
   pip install --upgrade yt-dlp
   ```

2. **使用異步處理避免阻塞**
   ```python
   await asyncio.wait_for(extract_info(), timeout=45)
   ```

3. **記錄詳細日誌方便除錯**
   ```python
   logger.error(f"搜尋失敗: {e}", exc_info=True)
   ```

4. **實作降級策略**
   ```python
   # 先嘗試 Android 客戶端
   # 失敗後嘗試 Web 客戶端
   # 最後嘗試使用 Cookie
   ```

---

**祝你使用愉快! 🎉**

如有問題,請查看 [PROJECT_STATUS.md](PROJECT_STATUS.md) 或提交 Issue。
