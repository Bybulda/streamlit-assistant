from typing import List, Dict

import tiktoken


def get_encoder(model_name: str = "gpt-4o-mini") -> tiktoken.Encoding:
    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def chunk_text_by_tokens(
        text: str,
        chunk_size: int = 400,
        chunk_overlap: int = 50,
        model_name: str = "gpt-4o-mini"
) -> List[str]:
    encoder = get_encoder(model_name)
    tokens = encoder.encode(text)

    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoder.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += chunk_size - chunk_overlap

    return chunks


def preprocess_document_by_tokens(
        content: str,
        model_name: str = "gpt-4o-mini"
) -> List[Dict[str, str]]:
    chunks = chunk_text_by_tokens(content, model_name=model_name)
    return [{"content": chunk, "chunk_index": i} for i, chunk in enumerate(chunks)]
