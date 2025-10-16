"""RAG 資料管理工具 - 簡單的命令列工具"""
from rag_system import RAGSystem
from logger import logger


def show_menu():
    """顯示主選單"""
    print("\n" + "="*50)
    print("🗂️  RAG 個人化資料管理工具")
    print("="*50)
    print("1. 查看所有資料")
    print("2. 新增資料")
    print("3. 搜尋資料")
    print("4. 清空所有資料")
    print("5. 填充範例資料")
    print("6. 批次匯入資料")
    print("0. 離開")
    print("="*50)


def view_all_data(rag: RAGSystem):
    """查看所有資料"""
    count = rag.get_collection_count()
    print(f"\n📊 目前共有 {count} 筆資料\n")

    if count == 0:
        print("⚠️  資料庫為空，請先新增資料或填充範例資料")
        return

    # 使用空查詢來取得所有資料
    results = rag.query("", n_results=count)

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['text']}")
        if result.get('metadata'):
            print(f"   類別: {result['metadata'].get('category', '未分類')}")
        print()


def add_single_data(rag: RAGSystem):
    """新增單筆資料"""
    print("\n📝 新增資料")
    print("-" * 50)

    text = input("請輸入資料內容：").strip()
    if not text:
        print("❌ 資料內容不能為空")
        return

    category = input("請輸入類別（可選，按 Enter 跳過）：").strip()

    metadata = {}
    if category:
        metadata["category"] = category

    # 生成 ID
    import hashlib
    doc_id = hashlib.md5(text.encode()).hexdigest()[:12]

    rag.add_document(text=text, metadata=metadata, doc_id=doc_id)
    print(f"✅ 資料已新增！ID: {doc_id}")


def search_data(rag: RAGSystem):
    """搜尋資料"""
    print("\n🔍 搜尋資料")
    print("-" * 50)

    query = input("請輸入搜尋關鍵字：").strip()
    if not query:
        print("❌ 搜尋關鍵字不能為空")
        return

    n_results = input("顯示幾筆結果？（預設 3）：").strip()
    try:
        n_results = int(n_results) if n_results else 3
    except ValueError:
        n_results = 3

    results = rag.query(query, n_results=n_results)

    if not results:
        print(f"❌ 找不到與「{query}」相關的資料")
        return

    print(f"\n✅ 找到 {len(results)} 筆相關資料：\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['text']}")
        if result.get('metadata'):
            print(f"   類別: {result['metadata'].get('category', '未分類')}")
        print(f"   相似度: {1 - result.get('distance', 0):.2%}")
        print()


def clear_all_data(rag: RAGSystem):
    """清空所有資料"""
    print("\n⚠️  清空所有資料")
    print("-" * 50)

    confirm = input("確定要刪除所有資料嗎？此操作無法復原！(yes/no)：").strip().lower()

    if confirm == 'yes':
        rag.clear_all_data()
        print("✅ 所有資料已清空")
    else:
        print("❌ 操作已取消")


def populate_sample_data(rag: RAGSystem):
    """填充範例資料"""
    print("\n📦 填充範例資料")
    print("-" * 50)

    confirm = input("確定要填充範例資料嗎？(yes/no)：").strip().lower()

    if confirm == 'yes':
        rag.populate_sample_data()
        print("✅ 範例資料已填充")
    else:
        print("❌ 操作已取消")


def batch_import_data(rag: RAGSystem):
    """批次匯入資料"""
    print("\n📥 批次匯入資料")
    print("-" * 50)
    print("請輸入多筆資料，每筆一行，格式：資料內容 | 類別")
    print("例如：我喜歡吃日本料理 | 飲食偏好")
    print("輸入空行結束")
    print()

    data_list = []
    while True:
        line = input(f"第 {len(data_list) + 1} 筆：").strip()
        if not line:
            break

        parts = line.split('|')
        text = parts[0].strip()
        category = parts[1].strip() if len(parts) > 1 else "未分類"

        data_list.append({
            "text": text,
            "category": category
        })

    if not data_list:
        print("❌ 沒有輸入任何資料")
        return

    print(f"\n即將匯入 {len(data_list)} 筆資料：")
    for i, data in enumerate(data_list, 1):
        print(f"{i}. {data['text']} [{data['category']}]")

    confirm = input("\n確定匯入？(yes/no)：").strip().lower()

    if confirm == 'yes':
        for data in data_list:
            rag.add_document(
                text=data["text"],
                metadata={"category": data["category"]}
            )
        print(f"✅ 成功匯入 {len(data_list)} 筆資料")
    else:
        print("❌ 操作已取消")


def main():
    """主程式"""
    print("\n正在初始化 RAG 系統...")
    rag = RAGSystem()
    print("✅ RAG 系統已初始化（資料庫路徑: ./chroma_db）")

    while True:
        show_menu()
        choice = input("\n請選擇功能（輸入數字）：").strip()

        if choice == '1':
            view_all_data(rag)
        elif choice == '2':
            add_single_data(rag)
        elif choice == '3':
            search_data(rag)
        elif choice == '4':
            clear_all_data(rag)
        elif choice == '5':
            populate_sample_data(rag)
        elif choice == '6':
            batch_import_data(rag)
        elif choice == '0':
            print("\n👋 再見！")
            break
        else:
            print("❌ 無效的選項，請重新選擇")

        input("\n按 Enter 繼續...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程式已中斷")
    except Exception as e:
        logger.error(f"執行時發生錯誤: {e}")
        print(f"\n❌ 發生錯誤: {e}")
