import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# Initialize embedding function and persistent Chroma client
_emb_fn = OpenAIEmbeddingFunction(model_name="text-embedding-3-large")
_client = chromadb.PersistentClient(path="./data/chroma")
_collection = _client.get_or_create_collection(
    "kb",
    embedding_function=_emb_fn,
)

def upsert(doc_id: str, text: str, meta: dict | None = None) -> None:
    """Insert or update a document in the vector store."""
    _collection.upsert(ids=[doc_id], documents=[text], metadatas=[meta or {}])

def search(query: str, k: int = 5) -> list[str]:
    """Search the vector store and return top k documents."""
    results = _collection.query(query_texts=[query], n_results=k)
    return results.get("documents", [[]])[0]
