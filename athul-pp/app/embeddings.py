import os
from typing import Any


def get_embedding_backend_name() -> str:
    backend = os.getenv("EMBEDDING_BACKEND", "onnx").strip().lower()
    if backend == "sentence-transformers":
        return "sentence-transformers"
    return "onnx"


def get_embedding_function() -> Any:
    """
    Returns the configured ChromaDB embedding function.
    Reads EMBEDDING_BACKEND environment variable:
      - 'sentence-transformers': uses SentenceTransformerEmbeddingFunction (for local use).
      - Otherwise (default 'onnx'): uses DefaultEmbeddingFunction (ONNX Runtime without PyTorch).
    Never imports torch or sentence_transformers at module level.
    """
    backend = get_embedding_backend_name()
    if backend == "sentence-transformers":
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        return SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    return DefaultEmbeddingFunction()
