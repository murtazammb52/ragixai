"""
Hybrid retrieval: Dense (ChromaDB) + BM25 sparse, fused with RRF.
Returns top-K ScoredChunks, optionally filtered to specific companies.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from loguru import logger

from backend.config import settings
from backend.models.db import get_collection, get_bm25_index
from backend.pipeline.embedder import get_embedder


@dataclass
class ScoredChunk:
    chunk_id: str
    text: str
    score: float
    doc_id: str
    company: str
    year: int
    section: str
    ticker: str = ""


def _rrf_score(rank: int, k: int = 60) -> float:
    return 1.0 / (k + rank + 1)


def retrieve(
    query: str,
    top_k: int | None = None,
    mode: str = "hybrid",  # "dense" | "bm25" | "hybrid"
    ticker_filter: list[str] | None = None,  # None = all tickers; e.g. ["AAPL"]
) -> list[ScoredChunk]:
    """
    Retrieve top_k chunks for query using the specified mode.
    mode="hybrid" uses RRF fusion of dense + BM25.
    ticker_filter restricts results to the given ticker symbols (matches the
    "ticker" metadata field in ChromaDB — e.g. ["AAPL", "MSFT"]).
    """
    k = top_k or settings.top_k_retrieve

    if mode == "dense":
        return _dense_retrieve(query, k, ticker_filter)
    if mode == "bm25":
        return _bm25_retrieve(query, k, ticker_filter)
    return _hybrid_retrieve(query, k, ticker_filter)


def _dense_retrieve(
    query: str, top_k: int, ticker_filter: list[str] | None = None
) -> list[ScoredChunk]:
    embedder = get_embedder()
    query_vec = embedder.embed_query(query)
    collection = get_collection()

    if collection.count() == 0:
        logger.warning("ChromaDB collection is empty")
        return []

    # Build optional ChromaDB where clause using ticker (standardised field)
    where = None
    if ticker_filter:
        where = (
            {"ticker": ticker_filter[0]}
            if len(ticker_filter) == 1
            else {"ticker": {"$in": ticker_filter}}
        )

    results = collection.query(
        query_embeddings=[query_vec],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
        where=where,
    )
    chunks = []
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    )):
        score = 1.0 - dist  # cosine distance → similarity
        chunks.append(ScoredChunk(
            chunk_id=results["ids"][0][i],
            text=doc,
            score=score,
            doc_id=meta.get("doc_id", ""),
            company=meta.get("company", ""),
            year=int(meta.get("year", 0)),
            section=meta.get("section", ""),
            ticker=meta.get("ticker", ""),
        ))
    return chunks


def _bm25_retrieve(
    query: str, top_k: int, ticker_filter: list[str] | None = None
) -> list[ScoredChunk]:
    bm25, doc_ids = get_bm25_index()
    if bm25 is None:
        logger.warning("BM25 index not available")
        return []

    tokenized = query.lower().split()
    scores = bm25.get_scores(tokenized)

    # Fetch more candidates when filtering so we still return top_k after pruning
    fetch_k = top_k * 4 if ticker_filter else top_k
    top_indices = np.argsort(scores)[-fetch_k:][::-1]

    collection = get_collection()
    result_ids = [doc_ids[i] for i in top_indices if scores[i] > 0]
    if not result_ids:
        return []

    fetched = collection.get(ids=result_ids, include=["documents", "metadatas"])
    id_to_meta = {fid: (fdoc, fmeta) for fid, fdoc, fmeta in zip(
        fetched["ids"], fetched["documents"], fetched["metadatas"]
    )}

    chunks = []
    for idx in top_indices:
        if len(chunks) >= top_k:
            break
        if scores[idx] <= 0:
            continue
        cid = doc_ids[idx]
        if cid not in id_to_meta:
            continue
        doc, meta = id_to_meta[cid]
        ticker = meta.get("ticker", "")
        if ticker_filter and ticker not in ticker_filter:
            continue
        chunks.append(ScoredChunk(
            chunk_id=cid,
            text=doc,
            score=float(scores[idx]),
            doc_id=meta.get("doc_id", ""),
            company=meta.get("company", ""),
            year=int(meta.get("year", 0)),
            section=meta.get("section", ""),
            ticker=ticker,
        ))
    return chunks


def _hybrid_retrieve(
    query: str, top_k: int, ticker_filter: list[str] | None = None
) -> list[ScoredChunk]:
    dense = _dense_retrieve(query, top_k, ticker_filter)
    sparse = _bm25_retrieve(query, top_k, ticker_filter)

    if not sparse:
        logger.debug("BM25 returned no results — using dense only")
        return dense[:top_k]

    dense_ids = {c.chunk_id: i for i, c in enumerate(dense)}
    sparse_ids = {c.chunk_id: i for i, c in enumerate(sparse)}
    all_ids = set(dense_ids) | set(sparse_ids)

    id_to_chunk: dict[str, ScoredChunk] = {c.chunk_id: c for c in dense + sparse}
    rrf_scores: dict[str, float] = {}

    for cid in all_ids:
        score = 0.0
        if cid in dense_ids:
            score += settings.dense_weight * _rrf_score(dense_ids[cid])
        if cid in sparse_ids:
            score += settings.bm25_weight * _rrf_score(sparse_ids[cid])
        rrf_scores[cid] = score

    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    results = []
    for cid, rrf_sc in ranked:
        chunk = id_to_chunk[cid]
        chunk.score = rrf_sc
        results.append(chunk)
    return results
