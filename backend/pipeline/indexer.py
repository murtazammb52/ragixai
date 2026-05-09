"""
ChromaDB write path: embed chunks and upsert into vector store.
Supports resumable indexing — already-indexed chunk IDs are skipped automatically.
"""
from __future__ import annotations

import gc
import hashlib
from loguru import logger
from tqdm import tqdm

from backend.models.db import get_collection, build_bm25_index
from backend.pipeline.embedder import get_embedder
from backend.pipeline.chunker import load_chunks
from backend.config import settings

BATCH_SIZE = 32


def _chunk_id(doc_id: str, chunk_index: int) -> str:
    raw = f"{doc_id}_{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def build_index(
    chunks: list[dict] | None = None,
    strategy: str | None = None,
    reset: bool = False,
    resume: bool = False,
    batch_size: int = BATCH_SIZE,
) -> int:
    """
    Embed chunks and upsert into ChromaDB.

    resume=True  — skip chunks whose IDs are already in the collection (safe to re-run
                   after a crash; combines with reset=False for true continuation).
    reset=True   — wipe the collection first (full rebuild from zero).
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

    # Build the full ID list up-front so we can diff against existing
    all_ids = [_chunk_id(c["metadata"]["doc_id"], c["metadata"]["chunk_index"]) for c in chunks]

    if resume or not reset:
        existing_ids: set[str] = set()
        existing_count = collection.count()
        if existing_count > 0:
            logger.info(f"Collection has {existing_count} existing docs — fetching IDs to skip duplicates...")
            page_size = 5000
            offset = 0
            while True:
                page = collection.get(limit=page_size, offset=offset, include=[])
                if not page["ids"]:
                    break
                existing_ids.update(page["ids"])
                offset += page_size
                if len(page["ids"]) < page_size:
                    break
            logger.info(f"Will skip {len(existing_ids)} already-indexed chunks")

        pending_pairs = [(c, cid) for c, cid in zip(chunks, all_ids) if cid not in existing_ids]
    else:
        pending_pairs = list(zip(chunks, all_ids))

    if not pending_pairs:
        logger.info("All chunks already indexed. Nothing to do.")
        build_bm25_index()
        return 0

    logger.info(f"Indexing {len(pending_pairs)} chunks into '{settings.chroma_collection_name}'...")

    embedder = get_embedder()

    indexed = 0
    for batch_start in tqdm(range(0, len(pending_pairs), batch_size), desc="Indexing"):
        batch_pairs = pending_pairs[batch_start: batch_start + batch_size]
        batch_chunks = [p[0] for p in batch_pairs]
        batch_ids    = [p[1] for p in batch_pairs]

        texts = [c["text"] for c in batch_chunks]
        metas = [c["metadata"] for c in batch_chunks]

        embeddings = embedder.embed_documents(texts)

        safe_metas = [
            {k: (str(v) if not isinstance(v, (str, int, float, bool)) else v) for k, v in m.items()}
            for m in metas
        ]

        collection.upsert(
            ids=batch_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=safe_metas,
        )
        indexed += len(batch_pairs)
        gc.collect()

    logger.info(f"Indexed {indexed} new chunks. Collection total: {collection.count()}")
    build_bm25_index()
    return indexed
