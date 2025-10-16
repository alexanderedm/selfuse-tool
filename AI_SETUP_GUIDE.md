# AI 助理設定指南

## 1. 安裝本地 LLM（Ollama）

### Windows 安裝

1. **下載 Ollama**
   - 前往：https://ollama.com/download
   - 下載 Windows 版本
   - 執行安裝程式

2. **下載模型**
   ```bash
   # 開啟命令提示字元或 PowerShell
   ollama pull llama3:8b
   ```

   **其他推薦模型**：
   - `llama3:8b` - 預設，8B 參數（約 4.7GB）
   - `llama3:70b` - 大模型，70B 參數（約 40GB，需要更好的硬體）
   - `mistral` - 另一個優秀模型（約 4.1GB）
   - `qwen2.5:7b` - 中文效果較好（約 4.7GB）

3. **啟動 Ollama 服務**
   ```bash
   # Ollama 安裝後會自動在背景運行
   # 如果沒有，手動啟動：
   ollama serve
   ```

4. **測試連接**
   ```bash
   # 測試模型是否正常運行
   ollama run llama3:8b
   ```
   輸入一個問題測試，成功回應後輸入 `/bye` 退出

## 2. 修改 AI 助理配置（可選）

如果你想使用不同的模型或 LLM 服務，可以修改：

**方法 1：修改代碼** (`ai_assistant.py`)
```python
# 在 AIAssistant.__init__ 中修改預設值
def __init__(
    self,
    rag_system: RAGSystem,
    base_url: str = "http://localhost:11434/v1",  # Ollama 預設端點
    model: str = "llama3:8b",  # 修改成你下載的模型
    max_rounds: int = 3
):
```

**方法 2：使用其他 LLM 服務**

如果你想使用 LM Studio、OpenAI API 或其他服務：

```python
# LM Studio (預設端口 1234)
base_url = "http://localhost:1234/v1"
model = "你在 LM Studio 載入的模型名稱"

# OpenAI API
base_url = "https://api.openai.com/v1"
model = "gpt-4"  # 或 gpt-3.5-turbo
api_key = "你的 OpenAI API 金鑰"
```

## 3. RAG 資料管理

### 自動填充範例資料
首次使用時，系統會自動填充範例資料（5 筆關於飲食偏好的資料）

### 手動新增資料

**方法 1：使用 Python 腳本**
```python
from rag_system import RAGSystem

# 初始化 RAG 系統
rag = RAGSystem()

# 新增單筆資料
rag.add_document(
    text="使用者喜歡聽電子音樂和 J-Pop",
    metadata={"category": "音樂偏好"},
    doc_id="music_pref_1"
)

# 新增多筆資料
user_data = [
    {
        "text": "使用者住在台北市信義區",
        "metadata": {"category": "地理位置"},
        "id": "location_1"
    },
    {
        "text": "使用者的工作是軟體工程師",
        "metadata": {"category": "職業"},
        "id": "job_1"
    }
]

for data in user_data:
    rag.add_document(
        text=data["text"],
        metadata=data["metadata"],
        doc_id=data["id"]
    )

print(f"目前 RAG 系統有 {rag.get_collection_count()} 筆資料")
```

**方法 2：使用 RAG 管理 UI**（即將新增）
- 在 AI 助理視窗中直接新增、編輯、刪除個人化資料

### 資料類別建議

建議將個人化資料分類儲存：

| 類別 | 範例 |
|------|------|
| 飲食偏好 | 喜歡的菜系、討厭的食物 |
| 健康資訊 | 過敏原、飲食限制 |
| 地理位置 | 住家、常去地點 |
| 預算 | 各種消費預算 |
| 興趣嗜好 | 音樂、電影、運動 |
| 工作學習 | 職業、技能、學習目標 |
| 人際關係 | 家人、朋友偏好 |
| 時間習慣 | 作息時間、習慣 |

### 清空所有資料

```python
from rag_system import RAGSystem

rag = RAGSystem()
rag.clear_all_data()  # ⚠️ 小心！這會刪除所有資料
```

## 4. 使用 AI 助理

1. **啟動應用程式**
2. **點擊系統托盤圖示**
3. **選擇「🤖 AI 助理」**
4. **輸入你的問題**
5. **點擊「🚀 開始討論」**

系統會：
1. 從 RAG 系統檢索相關個人化資料
2. 5 個 AI 代理進行討論（2-3 輪）
3. 共識投票決定是否結束
4. 選出負責人撰寫最終提案
5. 顯示完整會議記錄

## 5. 故障排除

### 問題：連線錯誤 (Connection error)
- **原因**：Ollama 沒有運行
- **解決**：
  ```bash
  ollama serve
  ```
  或重新啟動 Ollama 應用程式

### 問題：模型回應很慢
- **原因**：模型太大或電腦配置不足
- **解決**：
  - 使用較小的模型（如 `llama3:8b` 而非 `llama3:70b`）
  - 減少討論輪數（修改 `max_rounds`）
  - 減少 AI 代理數量

### 問題：RAG 檢索不到相關資料
- **原因**：資料庫中沒有相關資料
- **解決**：手動新增更多個人化資料

### 問題：ChromaDB 錯誤
- **解決**：刪除 `./chroma_db` 資料夾，重新啟動應用程式

## 6. 進階配置

### 修改討論輪數
```python
# 在 ai_assistant_window.py 中修改
max_rounds = 3  # 增加到 5 輪討論
```

### 修改 AI 代理數量
可以在 `ai_assistant.py` 中增加或減少代理

### 自定義 AI 角色
在 `ai_agent.py` 的 `ROLES` 字典中新增角色：
```python
ROLES = {
    # ... 現有角色 ...
    "comedian": {
        "name": "幽默大師",
        "prompt": "你是一位幽默風趣的思考者，專注於用輕鬆的方式看待問題。"
    }
}
```

## 7. 效能建議

| 硬體 | 推薦模型 | 預期回應時間 |
|------|---------|-------------|
| 8GB RAM | llama3:8b | 5-15 秒/輪 |
| 16GB RAM | llama3:8b, mistral | 3-10 秒/輪 |
| 32GB+ RAM | llama3:70b | 10-30 秒/輪 |

**注意**：5 個 AI 代理 × 3 輪討論 = 至少 15 次 LLM 呼叫，總計可能需要 2-5 分鐘

## 8. 隱私說明

- ✅ **完全本地運行**：所有資料和 AI 運算都在你的電腦上
- ✅ **無網路傳輸**：不會傳送任何資料到外部伺服器
- ✅ **資料所有權**：RAG 資料庫檔案在 `./chroma_db` 資料夾，你完全掌控

---

**有任何問題或建議，歡迎在 GitHub 提出 Issue！**
