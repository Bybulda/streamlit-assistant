import os
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "documents")

client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    settings=Settings(allow_reset=True)
)

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def get_or_create_collection():
    return client.get_or_create_collection(name=CHROMA_COLLECTION)


def encode_texts(texts: List[str]) -> List[List[float]]:
    return embedder.encode(texts).tolist()


def add_document(doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
    collection = get_or_create_collection()
    embedding = encode_texts([content])
    collection.add(
        ids=[doc_id],
        documents=[content],
        embeddings=embedding,
        metadatas=[metadata or {}]
    )


def get_document_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
    collection = get_or_create_collection()
    result = collection.get(
        ids=[doc_id],
        include=["documents", "metadatas", "embeddings"]
    )

    if not result["ids"]:
        return None

    return {
        "id": result["ids"][0],
        "document": result["documents"][0],
        "metadata": result["metadatas"][0],
        "embedding": result["embeddings"][0] if "embeddings" in result else {}
    }



def document_exists(doc_id: str) -> bool:
    collection = get_or_create_collection()
    result = collection.get(ids=[doc_id])
    return len(result["ids"]) > 0


def delete_document(doc_id: str):
    collection = get_or_create_collection()
    collection.delete(ids=[doc_id])


def list_all_documents(limit: int = 100) -> List[Dict[str, Any]]:
    collection = get_or_create_collection()
    data = collection.get(limit=limit)
    docs = []
    for i, _id in enumerate(data["ids"]):
        docs.append({
            "id": _id,
            "document": data["documents"][i],
            "metadata": data["metadatas"][i]
        })
    return docs


def reset_collection():
    client.delete_collection(CHROMA_COLLECTION)
    print(f"Collection '{CHROMA_COLLECTION}' was reset.")
