# 安裝指南

本頁面將引導你完成 Selftool 的安裝過程。

---

## 📦 方法一：下載可執行檔（推薦）

這是最簡單的安裝方式，無需安裝 Python 環境。

### 步驟

1. **前往 Releases 頁面**

    訪問 [GitHub Releases](https://github.com/your-username/selfuse-tool/releases)，找到最新版本。

2. **下載壓縮檔**

    下載 `selftool-vX.X.X-windows-x64.zip`（例如 `selftool-v1.0.0-windows-x64.zip`）

3. **解壓縮**

    將壓縮檔解壓到你想要的位置，例如：
    ```
    C:\Program Files\Selftool\
    ```

4. **執行程式**

    雙擊 `selftool.exe` 啟動程式。

5. **建立捷徑（可選）**

    右鍵點擊 `selftool.exe` → 傳送到 → 桌面（建立捷徑）

!!! tip "提示"
    首次執行時，Windows 可能會顯示 SmartScreen 警告。點擊「其他資訊」→「仍要執行」即可。

---

## 🐍 方法二：從原始碼執行

適合開發者或需要自訂功能的進階使用者。

### 系統需求

- Python 3.8 或更高版本
- pip（Python 套件管理器）
- Git（用於克隆專案）

### 步驟

1. **安裝 Python**

    前往 [Python 官網](https://www.python.org/downloads/) 下載並安裝 Python 3.8+

    !!! warning "注意"
        安裝時記得勾選「Add Python to PATH」

2. **克隆專案**

    ```bash
    git clone https://github.com/your-username/selfuse-tool.git
    cd selfuse-tool
    ```

3. **建立虛擬環境（推薦）**

    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    ```

4. **安裝依賴套件**

    ```bash
    pip install -r requirements.txt
    ```

5. **執行程式**

    ```bash
    python src/main.py
    ```

---

## 🔧 方法三：打包成可執行檔

如果你修改了原始碼並想要打包成 `.exe`：

### 步驟

1. **安裝 PyInstaller**

    ```bash
    pip install pyinstaller
    ```

2. **執行打包**

    ```bash
    pyinstaller selftool.spec
    ```

3. **找到執行檔**

    打包完成後，執行檔位於 `dist/selftool/selftool.exe`

---

## ✅ 驗證安裝

安裝完成後，你應該會看到：

1. **系統托盤圖示**

    Windows 工作列右下角出現 Selftool 圖示

2. **右鍵選單**

    右鍵點擊圖示，會出現功能選單

3. **設定視窗**

    選擇「設定」應該能順利開啟設定視窗

如果沒有出現圖示，請檢查：

- 是否有錯誤訊息彈出？
- 是否有防毒軟體阻擋？
- `logs/` 目錄下是否有錯誤日誌？

---

## 🚀 下一步

安裝完成後，請前往 [基本使用](basic-usage.md) 學習如何設定與使用 Selftool。

---

## ❓ 遇到問題？

如果安裝過程中遇到問題，請：

1. 查看 [常見問題](faq.md)
2. 檢查 [GitHub Issues](https://github.com/your-username/selfuse-tool/issues)
3. 提出新的 Issue 尋求協助
