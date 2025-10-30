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
            self._emb_fn = OpenAIEmbeddingFunction(model_name="text-embedding-3-large")
            self._client = chromadb.PersistentClient(path=self.index_path)
            self._collection = self._client.get_or_create_collection(
                "kb",
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
