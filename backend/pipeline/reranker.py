"""
Cross-encoder reranking: top-20 → top-5.
Model: cross-encoder/ms-marco-MiniLM-L-6-v2 (~85MB, local)
"""
from __future__ import annotations

from loguru import logger

from backend.config import settings
from backend.pipeline.retriever import ScoredChunk

_cross_encoder = None


def _get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        from sentence_transformers import CrossEncoder
        logger.info(f"Loading CrossEncoder: {settings.rerank_model}")
        _cross_encoder = CrossEncoder(settings.rerank_model)
    return _cross_encoder


def rerank(query: str, candidates: list[ScoredChunk], top_k: int | None = None) -> list[ScoredChunk]:
    """Rerank candidates with cross-encoder, return top_k."""
    k = top_k or settings.top_k_rerank
    if not candidates:
        return []
    if len(candidates) == 1:
        return candidates

    model = _get_cross_encoder()
    pairs = [(query, c.text) for c in candidates]
    scores = model.predict(pairs)

    ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
    results = []
    for score, chunk in ranked[:k]:
        chunk.score = float(score)
        results.append(chunk)
    return results
