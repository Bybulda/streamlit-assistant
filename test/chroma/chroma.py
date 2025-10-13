# db/chroma.py
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import chromadb

CHROMA_HOST = "localhost"   # если докер локально
CHROMA_PORT = 8000

client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    settings=Settings(allow_reset=True)  # удобно в dev, можно убрать на проде
)


client.delete_collection("test_docs")
embedding_fn = SentenceTransformerEmbeddingFunction(model_name="sentence-transformers/all-MiniLM-L6-v2")

collection = client.get_or_create_collection(
    name="test_docs",
    embedding_function=embedding_fn
)

collection.add(
    ids=["1"],
    documents=["Привет, это тестовый документ для ChromaDB"]
)

def get_or_create_collection(name: str = "documents"):
    try:
        return client.get_collection(name)
    except Exception:
        return client.create_collection(name)
