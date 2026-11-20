import io
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from pypdf import PdfReader

from app.embeddings import get_embedding_backend_name, get_embedding_function

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"
DATA_DIR = BASE_DIR / "data"

_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[Any] = None


def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _client


def get_collection() -> Any:
    global _collection
    if _collection is None:
        client = get_chroma_client()
        backend = get_embedding_backend_name()
        collection_name = f"notes_{backend}"
        embed_fn = get_embedding_function()
        _collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=embed_fn,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def reset_collection_cache() -> None:
    global _client, _collection
    _client = None
    _collection = None


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    if not text or not text.strip():
        return []
    chunks = []
    start = 0
    step = max(1, chunk_size - overlap)
    text_len = len(text)
    while start < text_len:
        end = min(text_len, start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == text_len:
            break
        start += step
    return chunks


def extract_chunks_from_file(filename: str, content_bytes: bytes) -> List[Dict[str, Any]]:
    lower_name = filename.lower()
    extracted_chunks: List[Dict[str, Any]] = []

    if lower_name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content_bytes))
        chunk_idx = 0
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            chunks = chunk_text(page_text, chunk_size=500, overlap=50)
            for c in chunks:
                extracted_chunks.append({
                    "text": c,
                    "metadata": {
                        "source": filename,
                        "page": page_num,
                        "chunk_index": chunk_idx,
                    }
                })
                chunk_idx += 1
    elif lower_name.endswith((".txt", ".md")):
        try:
            text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = content_bytes.decode("latin-1", errors="ignore")
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        for idx, c in enumerate(chunks):
            extracted_chunks.append({
                "text": c,
                "metadata": {
                    "source": filename,
                    "page": 1,
                    "chunk_index": idx,
                }
            })
    else:
        raise ValueError(f"Unsupported file format: {filename}")

    return extracted_chunks


def ingest_file(filename: str, content_bytes: bytes) -> int:
    collection = get_collection()
    chunks = extract_chunks_from_file(filename, content_bytes)
    if not chunks:
        return 0

    # Re-upload replaces old chunks for the same filename
    try:
        existing = collection.get(where={"source": filename})
        if existing and existing.get("ids"):
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    ids = [f"{filename}-{i}" for i in range(len(chunks))]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    return len(chunks)


def retrieve(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    collection = get_collection()
    count = collection.count()
    if count == 0 or not query.strip():
        return []

    actual_k = min(top_k, count)
    results = collection.query(
        query_texts=[query],
        n_results=actual_k,
        include=["documents", "metadatas", "distances"]
    )

    items: List[Dict[str, Any]] = []
    if results and results.get("documents") and results["documents"][0]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

        for doc, meta, dist in zip(docs, metas, distances):
            score = round(1.0 - float(dist), 4)
            items.append({
                "text": doc,
                "source": meta.get("source", "unknown") if meta else "unknown",
                "page": int(meta.get("page", 1)) if meta and "page" in meta else 1,
                "score": score
            })

    return items


def list_documents() -> List[str]:
    collection = get_collection()
    all_data = collection.get(include=["metadatas"])
    if not all_data or not all_data.get("metadatas"):
        return []
    sources = set()
    for meta in all_data["metadatas"]:
        if meta and "source" in meta:
            sources.add(meta["source"])
    return sorted(list(sources))


def startup_ingest_data_folder() -> int:
    collection = get_collection()
    if collection.count() > 0:
        return collection.count()

    total_chunks = 0
    target_data_dirs = [DATA_DIR, Path("./data")]
    found_dir: Optional[Path] = None
    for d in target_data_dirs:
        if d.exists() and d.is_dir():
            found_dir = d
            break

    if not found_dir:
        return 0

    for file_path in sorted(found_dir.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in [".txt", ".md", ".pdf"]:
            try:
                content = file_path.read_bytes()
                chunks_added = ingest_file(file_path.name, content)
                total_chunks += chunks_added
            except Exception as e:
                print(f"Error ingesting sample file {file_path.name}: {e}")

    return total_chunks
