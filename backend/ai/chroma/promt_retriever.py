from chroma_service import get_or_create_collection, encode_texts


def retrieve_relevant_chunks(query: str, top_k: int = 5):
    collection = get_or_create_collection()
    query_embedding = encode_texts([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"]
    )
    return [
        {
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i]
        }
        for i in range(len(results["documents"][0]))
    ]


def build_prompt_with_context(user_question: str, context_chunks: list) -> str:
    context_text = "\n\n".join(
        [f"Контекст {i + 1}:\n{chunk['document']}" for i, chunk in enumerate(context_chunks)]
    )
    prompt = f"""Ты — помощник, использующий базу знаний для ответа на вопросы.

Контекст:
{context_text}

Вопрос пользователя:
{user_question}

Ответь максимально точно и опираясь на контекст.
"""
    return prompt
