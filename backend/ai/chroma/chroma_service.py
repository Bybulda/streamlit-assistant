import os
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from backend.ai.chroma.token_chunker import preprocess_document_by_tokens

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


def search_similar_chunks(query: str, top_k: int = 5, doc_id: Optional[str] = None):
    collection = get_or_create_collection()
    query_embedding = encode_texts([query])

    where_clause = {"document_id": doc_id} if doc_id else None

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=where_clause
    )

    if not results["ids"] or not results["ids"][0]:
        return []

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
        })
    return chunks


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


def add_full_document(
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        model_name: str = "gpt-4o-mini"
):
    collection = get_or_create_collection()
    processed_chunks = preprocess_document_by_tokens(content, model_name=model_name)

    ids = [f"{doc_id}_{chunk['chunk_index']}" for chunk in processed_chunks]
    documents = [chunk["content"] for chunk in processed_chunks]
    metadatas = [
        {**(metadata or {}), "chunk_index": chunk["chunk_index"]}
        for chunk in processed_chunks
    ]
    embeddings = encode_texts(documents)

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
