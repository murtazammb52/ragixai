"""
ChromaDB write path: embed chunks and upsert into vector store.
"""
from __future__ import annotations

import hashlib
from loguru import logger
from tqdm import tqdm

from backend.models.db import get_collection, build_bm25_index
from backend.pipeline.embedder import get_embedder
from backend.pipeline.chunker import load_chunks
from backend.config import settings

BATCH_SIZE = 128


def _chunk_id(doc_id: str, chunk_index: int) -> str:
    raw = f"{doc_id}_{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def build_index(chunks: list[dict] | None = None, strategy: str | None = None, reset: bool = False) -> int:
    """
    Embed chunks and upsert into ChromaDB.
    If chunks is None, loads from processed/chunks/*.jsonl.
    Returns the number of chunks indexed.
    """
    from backend.models.db import reset_collection

    if reset:
        reset_collection()
        logger.info("Collection reset")

    if chunks is None:
        chunks = load_chunks(strategy)

    if not chunks:
        logger.error("No chunks to index. Run chunking first.")
        return 0

    collection = get_collection()
    embedder = get_embedder()

    logger.info(f"Indexing {len(chunks)} chunks into '{settings.chroma_collection_name}'...")

    indexed = 0
    for batch_start in tqdm(range(0, len(chunks), BATCH_SIZE), desc="Indexing"):
        batch = chunks[batch_start: batch_start + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        metas = [c["metadata"] for c in batch]
        ids = [_chunk_id(m["doc_id"], m["chunk_index"]) for m in metas]

        embeddings = embedder.embed_documents(texts)

        # ChromaDB metadata values must be str/int/float/bool
        safe_metas = []
        for m in metas:
            safe_metas.append({k: (str(v) if not isinstance(v, (str, int, float, bool)) else v) for k, v in m.items()})

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=safe_metas,
        )
        indexed += len(batch)

    logger.info(f"Indexed {indexed} chunks. Collection total: {collection.count()}")
    build_bm25_index()
    return indexed
