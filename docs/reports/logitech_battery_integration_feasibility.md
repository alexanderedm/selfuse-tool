# 羅技裝置電池監控整合可行性分析報告

**日期**: 2025-10-22
**分析師**: Claude Code
**專案**: selftool 音訊切換工具

---

## 執行摘要

✅ **結論: 技術上可行，但需要投入大量開發時間**

我們成功驗證了使用 Python 的 `hidapi` 庫可以與羅技裝置通訊，並收到了 HID++ 協議的回應。然而，要實現完整的電池監控功能需要深入了解 HID++ 協議規範。

---

## 1. 硬體環境掃描結果

### 1.1 發現的羅技裝置

在系統中共發現 **12 個羅技 HID 裝置**：

| 裝置編號 | 產品名稱 | Product ID | 介面類型 | Usage Page/Usage |
|---------|---------|-----------|---------|-----------------|
| 1, 3 | G535 Wireless Gaming Headset | 0x0ac4 | Interface 3 | 0x000c/0x0001, 0xff43/0x0202 |
| 2, 4-10 | USB Receiver (Unifying) | 0xc539 | Interface 0-2 | 多種 |
| 11 | (未知羅技裝置) | 0xc232 | 鍵盤介面 | 0x0001/0x0006 |
| 12 | HID VHF Driver | 0x4087 | - | 0x0059/0x0001 |

### 1.2 關鍵發現

- **Unifying 接收器 (0xc539)**: 這是羅技的統一接收器，可同時連接多個無線裝置
- **G535 無線耳機 (0x0ac4)**: 支援 HID++ 協議
- **多個介面**: 每個裝置暴露多個 HID 介面，用於不同功能

---

## 2. HID++ 協議通訊測試

### 2.1 成功通訊的裝置

✅ **裝置 #3 (G535 耳機):**
```
發送: 11 ff 00 10 00 00 00  (HID++ 2.0 長訊息)
回應: 11 ff 00 10 04 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```
- 成功收到 20 bytes 回應
- 格式符合 HID++ 2.0 規範

✅ **裝置 #8 (USB Receiver, Interface 2):**
```
發送: 10 ff 00 10 00 00 00
回應: 10 ff 8f 00 10 01 00  (錯誤代碼)

發送: 10 ff 81 00 00 00 00
回應: 10 ff 81 00 00 01 00  (狀態回應)
```
- 成功收到 7 bytes 回應
- 格式符合 HID++ 1.0 規範

### 2.2 協議分析

**HID++ 訊息格式:**
- Byte 0: Report ID (0x10=短訊息 7bytes, 0x11=長訊息 20bytes)
- Byte 1: Device Index (0xFF=接收器, 0x00-0x05=連接的裝置)
- Byte 2: Sub ID / Feature Index
- Byte 3+: 參數

**錯誤代碼:**
- `0x8f`: 錯誤回應 (可能是功能不支援或參數錯誤)

---

## 3. 技術可行性評估

### 3.1 ✅ 已驗證可行項目

1. **裝置枚舉**: 可成功列出所有羅技 HID 裝置
2. **裝置開啟**: 可成功開啟並連接到裝置
3. **雙向通訊**: 可成功發送指令並接收回應
4. **HID++ 協議**: 裝置支援 HID++ 協議
5. **Python 整合**: `hidapi` 可無縫整合到現有專案

### 3.2 ❓ 待解決挑戰

1. **協議規範**: 需要 HID++ 完整規範文檔
   - 電池狀態的正確 Feature Index
   - 不同裝置類型的指令差異
   - 回應資料的正確解析方式

2. **裝置識別**: 需要識別哪個介面用於電池查詢
   - Unifying 接收器有多個介面 (Interface 0-2)
   - 不同介面支援不同功能

3. **多裝置管理**: Unifying 接收器可連接多個裝置
   - 需要枚舉所有連接的裝置
   - 分別查詢每個裝置的電池狀態

4. **權限問題**: 某些裝置讀取時出現 "read error"
   - 可能需要管理員權限
   - 可能是裝置驅動程式獨占

---

## 4. 整合方案比較

### 方案 A: 完全自行實作 HID++ 協議 ⚠️

**優點:**
- 完全控制，無需依賴外部程式
- 可支援所有羅技裝置
- 整合到現有專案

**缺點:**
- 🔴 **開發成本極高** (估計 40-80 小時)
- 需要深入研究 HID++ 協議
- 需要處理各種裝置的特殊情況
- 需要持續維護（羅技可能更新協議）

**預估開發時間**: 2-4 週

---

### 方案 B: 使用 LGSTrayBattery 的 HTTP API ✅ **推薦**

**優點:**
- 🟢 **開發成本低** (估計 2-4 小時)
- 已有完整實作，經過測試
- 支援多種羅技裝置
- 有視覺化界面可獨立使用

**缺點:**
- 需要同時運行兩個程式
- 依賴外部程式
- LGSTrayBattery 是 C#/.NET，需要 .NET Runtime

**實作方式:**
```python
import requests

def get_logitech_battery_info():
    try:
        response = requests.get('http://localhost:12321/api/devices')
        if response.status_code == 200:
            devices = response.json()
            for device in devices:
                print(f"{device['name']}: {device['battery_percentage']}%")
            return devices
    except:
        return None  # LGSTrayBattery 未運行
```

**預估開發時間**: 4-8 小時

---

### 方案 C: 使用現有 Python 函式庫 🔍

**研究現有函式庫:**
- `solaar`: 羅技 Unifying 接收器管理工具 (Linux 為主)
- `logiops`: 羅技裝置設定工具

**優點:**
- 可能有現成的 Python 實作
- 社群支援

**缺點:**
- 需要研究相容性
- 可能不支援所有裝置

**預估研究時間**: 4-8 小時

---

### 方案 D: 通用電池監控 (非羅技特定) ⭐ **最實用**

使用 `psutil` 監控系統電池和藍牙裝置:

```python
import psutil

def get_system_battery():
    battery = psutil.sensors_battery()
    if battery:
        return {
            'percent': battery.percent,
            'power_plugged': battery.power_plugged,
            'time_left': battery.secsleft
        }
```

**優點:**
- 🟢 **開發成本極低** (估計 1-2 小時)
- 支援筆電電池
- 支援所有品牌的藍牙裝置 (透過系統 API)
- 跨平台

**缺點:**
- 無法讀取羅技 Unifying 裝置的電池 (不經過藍牙)
- 功能較有限

**預估開發時間**: 2-4 小時

---

## 5. 建議方案

### 短期方案 (1-2 天)

**實作方案 D: 通用電池監控**
- 加入系統/筆電電池監控
- 在系統托盤顯示電池狀態圖示
- 低電量時發出通知

### 中期方案 (如需羅技裝置支援)

**實作方案 B: 整合 LGSTrayBattery API**
- 偵測 LGSTrayBattery 是否運行
- 如果運行，則顯示羅技裝置電池資訊
- 提供下載/安裝 LGSTrayBattery 的提示

### 長期方案 (如有充足時間和需求)

**研究方案 C: 現有 Python 函式庫**
- 深入研究 `solaar` 等專案
- 評估移植可行性
- 考慮貢獻回社群

---

## 6. 技術細節參考

### 6.1 已測試的 HID++ 指令

```python
# HID++ 2.0: 查詢功能
[0x11, 0xFF, 0x00, 0x10, 0x00, 0x00, 0x00]  # ✅ G535 耳機有回應

# HID++ 1.0: 查詢電池狀態
[0x10, 0xFF, 0x81, 0x00, 0x00, 0x00, 0x00]  # ✅ USB Receiver 有回應
```

### 6.2 可能有用的資源

- [HID++ 1.0 規範](https://github.com/Logitech/hidpp)
- [Solaar 專案](https://github.com/pwr-Solaar/Solaar) - 開源羅技裝置管理工具
- [LGSTrayBattery 原始碼](https://github.com/andyvorld/LGSTrayBattery)

---

## 7. 結論與建議

### 7.1 可行性總結

| 方案 | 可行性 | 開發時間 | 維護成本 | 功能完整度 | 推薦度 |
|-----|--------|---------|---------|----------|--------|
| A: 自行實作 HID++ | ✅ 可行 | 40-80h | 高 | ★★★★★ | ⭐⭐ |
| B: LGSTrayBattery API | ✅ 可行 | 2-4h | 低 | ★★★★ | ⭐⭐⭐⭐ |
| C: Python 函式庫 | 🔍 待研究 | 4-8h | 中 | ★★★★ | ⭐⭐⭐ |
| D: 通用電池監控 | ✅ 可行 | 1-2h | 極低 | ★★★ | ⭐⭐⭐⭐⭐ |

### 7.2 最終建議

**階段一 (立即實作):**
1. 實作**方案 D: 通用電池監控**
   - 提供即時價值
   - 開發成本低
   - 適用於大多數使用場景

**階段二 (可選,如有特殊需求):**
2. 研究**方案 C: Solaar 等現有專案**
   - 評估是否能滿足需求
   - 考慮整合或參考其實作

3. 若仍不滿足，再考慮**方案 B: LGSTrayBattery API**
   - 作為暫時解決方案
   - 同時進行方案 A 的長期研究

### 7.3 下一步行動

如果決定繼續整合羅技電池監控，建議:

1. ✅ **研究 Solaar 專案** (4-8 小時)
   - 分析其 HID++ 協議實作
   - 評估程式碼重用可能性

2. ✅ **實作基礎架構** (4 小時)
   - 建立 HID 裝置管理模組
   - 實作基礎 HID++ 通訊層

3. ✅ **逐步加入功能** (每個 4-8 小時)
   - 裝置枚舉
   - 電池狀態查詢
   - 定時更新
   - 系統托盤整合

---

## 8. 附錄: 技術實作範例

### 8.1 建議的模組結構

```
src/
├── battery/
│   ├── __init__.py
│   ├── battery_monitor.py       # 統一介面
│   ├── system_battery.py        # 方案 D: psutil
│   ├── logitech_api.py          # 方案 B: HTTP API
│   └── logitech_hid.py          # 方案 A/C: HID++ (未來)
└── main.py
```

### 8.2 統一介面設計

```python
class BatteryMonitor:
    def get_all_batteries(self):
        """取得所有電池資訊"""
        batteries = []

        # 系統電池
        system_battery = self.get_system_battery()
        if system_battery:
            batteries.append(system_battery)

        # 羅技裝置 (如果可用)
        logitech_batteries = self.get_logitech_batteries()
        batteries.extend(logitech_batteries)

        return batteries

    def get_system_battery(self):
        """使用 psutil 取得系統電池"""
        # 實作方案 D
        pass

    def get_logitech_batteries(self):
        """取得羅技裝置電池"""
        # 優先嘗試 HTTP API (方案 B)
        # 失敗則嘗試 HID++ (方案 A/C)
        pass
```

---

**報告結束**

*此報告基於 2025-10-22 的技術調查，實際開發時間可能因經驗和需求而有所不同。*
