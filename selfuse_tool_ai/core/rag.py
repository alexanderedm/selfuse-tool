import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

class Rag:
    """Simple RAG implementation using Chroma for embeddings and search."""

    def __init__(self, index_path: str = "./data/chroma"):
        """Initialize the RAG system with delayed initialization."""
        # 確保索引目錄存在
        from pathlib import Path
        Path(index_path).mkdir(parents=True, exist_ok=True)

        self.index_path = index_path
        self._emb_fn = None
        self._client = None
        self._collection = None

    def _initialize(self):
        """Lazy initialization of Chroma components."""
        if self._collection is None:
            # 從環境變數獲取 API key
            import os
            api_key = os.environ.get("OPENAI_API_KEY")

            # 如果環境變數中沒有，嘗試從 secure_config 載入
            if not api_key:
                try:
                    from src.core.secure_config import get_openai_api_key
                    api_key = get_openai_api_key()
                    if api_key:
                        os.environ["OPENAI_API_KEY"] = api_key
                except Exception:
                    pass

            # 明確傳遞 API key 給 OpenAIEmbeddingFunction
            self._emb_fn = OpenAIEmbeddingFunction(
                api_key=api_key,
                model_name="text-embedding-3-large"
            )
            self._client = chromadb.PersistentClient(path=self.index_path)
            self._collection = self._client.get_or_create_collection(
                "knowledge_base",
                embedding_function=self._emb_fn,
            )

    def upsert(self, doc_id: str, text: str, meta: dict | None = None) -> None:
        """Insert or update a document in the vector store."""
        self._initialize()
        self._collection.upsert(ids=[doc_id], documents=[text], metadatas=[meta or {}])

    def search(self, query: str, k: int = 5) -> list[str]:
        """Search the vector store and return top k documents."""
        self._initialize()
        results = self._collection.query(query_texts=[query], n_results=k)
        return results.get("documents", [[]])[0]
