from __future__ import annotations

import chromadb
from rank_bm25 import BM25Okapi
from loguru import logger

from backend.config import settings

_chroma_client: chromadb.PersistentClient | None = None
_chroma_collection: chromadb.Collection | None = None
_bm25_index: BM25Okapi | None = None
_bm25_doc_ids: list[str] = []


def get_chroma_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _chroma_client


def get_collection() -> chromadb.Collection:
    global _chroma_collection
    if _chroma_collection is None:
        client = get_chroma_client()
        _chroma_collection = client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB collection '{settings.chroma_collection_name}' — {_chroma_collection.count()} docs")
    return _chroma_collection


def build_bm25_index() -> tuple[BM25Okapi, list[str]]:
    """Build BM25 index from all chunks stored in ChromaDB."""
    global _bm25_index, _bm25_doc_ids
    collection = get_collection()
    count = collection.count()
    if count == 0:
        logger.warning("ChromaDB collection is empty — BM25 index not built")
        _bm25_index = None
        _bm25_doc_ids = []
        return None, []

    logger.info(f"Building BM25 index from {count} chunks...")
    results = collection.get(include=["documents"])
    texts = results["documents"]
    ids = results["ids"]
    tokenized = [t.lower().split() for t in texts]
    _bm25_index = BM25Okapi(tokenized)
    _bm25_doc_ids = ids
    logger.info(f"BM25 index ready — {len(ids)} chunks")
    return _bm25_index, ids


def get_bm25_index() -> tuple[BM25Okapi | None, list[str]]:
    global _bm25_index, _bm25_doc_ids
    if _bm25_index is None:
        build_bm25_index()
    return _bm25_index, _bm25_doc_ids


def reset_collection() -> None:
    global _chroma_collection, _bm25_index, _bm25_doc_ids
    client = get_chroma_client()
    try:
        client.delete_collection(settings.chroma_collection_name)
        logger.info(f"Deleted collection '{settings.chroma_collection_name}'")
    except Exception:
        pass
    _chroma_collection = None
    _bm25_index = None
    _bm25_doc_ids = []
    get_collection()
