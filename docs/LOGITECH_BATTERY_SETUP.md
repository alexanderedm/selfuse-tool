# 羅技裝置電池監控設定指南

本指南說明如何為羅技無線裝置（如 G535、G733 等）啟用電池監控功能。

## 背景說明

羅技 USB 無線裝置使用專有的 HID++ 協議，無法透過 Windows 標準 API 查詢電池狀態。因此需要使用第三方工具 **LGSTray** 來提供電池資訊。

## 安裝步驟

### 1. 下載 LGSTray

前往 GitHub 發布頁面下載最新版本：
👉 https://github.com/andyvorld/LGSTrayBattery/releases

下載並解壓縮 `LGSTray-win-x64.zip`（包含 LGSTray.exe 和相關檔案）

### 2. 放置檔案

將解壓縮的所有檔案放在專案根目錄：

```
E:\VScode\selftool\
├── LGSTray.exe           ← 主程式
├── LGSTrayHID.exe        ← HID 驅動
├── LGSTray.pdb          ← 除錯符號
├── LGSTrayCore.pdb
├── LGSTrayHID.pdb
├── LGSTrayPrimitives.pdb
├── src\
├── start_logitech.bat   ← 使用這個！
└── ...
```

### 3. 使用啟動腳本

使用提供的 `start_logitech.bat` 啟動程式：

1. 雙擊 `start_logitech.bat`
2. 腳本會自動：
   - 檢查 LGSTray 是否已執行
   - 如果未執行，自動啟動它
   - 等待 3 秒讓 LGSTray 初始化
   - 啟動音訊切換工具

**就這麼簡單！一個批次檔搞定所有事情。**

## ✅ 驗證設定

執行 `test_lgstray.bat` 來測試 LGSTray 是否正常運作：
- ✅ 檢查 LGSTray 執行狀態
- ✅ 測試 API 連線
- ✅ 顯示所有裝置的電池資訊

如果看到類似以下輸出，表示設定成功：
```
[OK] LGSTray is running
[OK] API connection successful!
找到 3 個裝置:
1. G535 Gaming Headset
   電池: 80.0%
   充電中: 否
```

## 功能說明

### 自動偵測

程式會自動偵測 LGSTray 是否執行：

- ✅ **LGSTray 執行中**：顯示羅技裝置電池資訊（80%）
- ⚠️ **LGSTray 未執行**：退回到標準藍牙查詢（可能無法顯示羅技裝置）

### 托盤選單顯示

右鍵點擊系統托盤圖示，會看到：

```
🔋 Logitech G535 Gaming Headset: 85%
```

電池圖示說明：
- 🔌 充電中
- 🔋 電量充足（>= 50%）
- 🪫 電量不足（< 50%）

**電量資訊會在每次打開右鍵選單時自動更新**，無需手動刷新。

## 故障排除

### Q: 顯示「耳機: 不支援或未連接」

**檢查清單：**
1. ✅ LGSTray.exe 是否正在執行？
   - 檢查系統托盤是否有 LGSTray 圖示
   - 或使用工作管理員查看
   - **執行 `test_lgstray.bat` 進行診斷**

2. ✅ 羅技裝置是否已連接並開機？
   - 確認裝置已連接到電腦
   - 確認裝置已開機

3. ✅ LGSTray API 是否可訪問？
   - 開啟瀏覽器訪問 http://localhost:12321/
   - 應該能看到裝置列表 HTML 頁面
   - 執行 `test_lgstray.bat` 會自動測試

### Q: LGSTray 無法啟動

**可能原因：**
- 需要 .NET Runtime（通常 Windows 10/11 已內建）
- 防火牆或防毒軟體阻擋
- 羅技裝置驅動未正確安裝

**解決方法：**
1. 安裝最新的 [.NET Runtime](https://dotnet.microsoft.com/download/dotnet/8.0)
2. 檢查防火牆設定，允許 LGSTray
3. 安裝或更新羅技 G HUB 驅動程式

### Q: 能否單獨使用 LGSTray 查看電量？

可以！LGSTray 本身就是一個獨立的電池監控工具，會在系統托盤顯示電池百分比。本專案只是整合了它的 HTTP API 來提供統一的介面。

## 技術細節

### HTTP API 端點

LGSTray 提供 HTTP API（XML 格式）：

**端點：** `GET http://localhost:12321/device/{device_name}`

**範例：** `GET http://localhost:12321/device/G535%20Gaming%20Headset`

**回應範例：**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<xml>
  <device_id>dev00000000</device_id>
  <device_name>G535 Gaming Headset</device_name>
  <device_type>Headset</device_type>
  <battery_percent>80.00</battery_percent>
  <battery_voltage>0.00</battery_voltage>
  <mileage>30.71</mileage>
  <charging>False</charging>
  <last_update>10/22/2025 20:51:24 -06:00</last_update>
</xml>
```

**裝置列表端點：** `GET http://localhost:12321/`（返回 HTML 格式的裝置列表）

### 程式架構

```
src/battery/
├── __init__.py
├── bluetooth_battery.py      # 標準藍牙查詢（不支援羅技 USB 無線）
└── logitech_battery.py        # LGSTrayBattery API 整合

src/main.py
└── get_headset_battery_text()
    ├── 1. 嘗試 LGSTrayBattery API（優先）
    └── 2. 退回到標準藍牙查詢
```

## 其他資源

- **LGSTrayBattery GitHub**: https://github.com/andyvorld/LGSTrayBattery
- **HID++ 協議文檔**: https://github.com/Logitech/hidpp
- **可行性研究報告**: `docs/reports/logitech_battery_integration_feasibility.md`

## 授權聲明

LGSTrayBattery 是獨立的開源專案，本專案僅使用其 HTTP API。請參閱 LGSTrayBattery 的授權條款。
