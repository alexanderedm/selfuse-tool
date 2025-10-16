"""RAG 檢索系統模組 - 個人化資料檢索"""
import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict
from logger import logger


class RAGSystem:
    """RAG 檢索系統類別 - 負責個人化資料檢索"""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """初始化 RAG 系統

        Args:
            persist_directory: ChromaDB 持久化目錄
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        # 初始化 ChromaDB 客戶端
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        # 取得或建立集合
        self.collection = self.client.get_or_create_collection(
            name="user_data",
            metadata={"description": "使用者個人化資料"}
        )

        logger.info(f"RAG 系統已初始化，資料庫路徑: {persist_directory}")

    def add_document(self, text: str, metadata: Dict[str, any] = None, doc_id: str = None):
        """新增文件到向量資料庫

        Args:
            text: 文件內容
            metadata: 文件元數據（可選）
            doc_id: 文件 ID（可選，自動生成）
        """
        try:
            if not doc_id:
                import hashlib
                doc_id = hashlib.md5(text.encode()).hexdigest()

            self.collection.add(
                documents=[text],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )

            logger.info(f"文件已新增到 RAG 系統，ID: {doc_id}")

        except Exception as e:
            logger.error(f"新增文件時發生錯誤: {e}")

    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, any]]:
        """查詢相關文件

        Args:
            query_text: 查詢文字
            n_results: 回傳結果數量

        Returns:
            list: 相關文件列表，每個元素包含 {text, metadata, distance}
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )

            # 格式化結果
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })

            logger.info(f"RAG 查詢完成，找到 {len(formatted_results)} 個相關文件")

            return formatted_results

        except Exception as e:
            logger.error(f"查詢時發生錯誤: {e}")
            return []

    def get_context_for_question(self, question: str, n_results: int = 3) -> str:
        """為問題取得相關背景資料

        Args:
            question: 使用者問題
            n_results: 檢索結果數量

        Returns:
            str: 格式化的背景資料文字
        """
        results = self.query(question, n_results)

        if not results:
            return "無相關背景資料"

        # 格式化背景資料
        context_parts = ["### 相關背景資料\n"]
        for i, result in enumerate(results, 1):
            context_parts.append(f"{i}. {result['text']}")
            if result['metadata']:
                context_parts.append(f"   (來源: {result['metadata']})")

        context = "\n".join(context_parts)

        logger.debug(f"為問題產生背景資料，長度: {len(context)}")

        return context

    def populate_sample_data(self):
        """填充範例個人化資料（測試用）"""
        sample_data = [
            {
                "text": "使用者喜歡吃中式料理，特別是川菜和粵菜",
                "metadata": {"category": "飲食偏好"},
                "id": "pref_food_1"
            },
            {
                "text": "使用者對海鮮過敏，不能吃蝦、蟹",
                "metadata": {"category": "健康資訊"},
                "id": "health_allergy_1"
            },
            {
                "text": "使用者常去的餐廳：附近的川菜館（距離500公尺）",
                "metadata": {"category": "常用地點"},
                "id": "location_restaurant_1"
            },
            {
                "text": "使用者預算：晚餐通常在200-400元之間",
                "metadata": {"category": "預算"},
                "id": "budget_dinner_1"
            },
            {
                "text": "使用者最近在減肥，希望選擇較清淡的食物",
                "metadata": {"category": "當前目標"},
                "id": "goal_diet_1"
            }
        ]

        for data in sample_data:
            self.add_document(
                text=data["text"],
                metadata=data["metadata"],
                doc_id=data["id"]
            )

        logger.info("已填充 5 筆範例個人化資料")

    def clear_all_data(self):
        """清空所有資料（慎用）"""
        try:
            self.client.delete_collection(name="user_data")
            self.collection = self.client.get_or_create_collection(
                name="user_data",
                metadata={"description": "使用者個人化資料"}
            )
            logger.info("RAG 系統資料已清空")
        except Exception as e:
            logger.error(f"清空資料時發生錯誤: {e}")

    def get_collection_count(self) -> int:
        """取得集合中的文件數量

        Returns:
            int: 文件數量
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"取得文件數量時發生錯誤: {e}")
            return 0
