import time
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from backend.models.schemas import ChatRequest, ChatResponse, Citation
from backend.models.history import save_query
from backend.models.auth import UserContext, require_user
from backend.pipeline.guardrails import check_input, check_ticker_scope, detect_mentioned_tickers
from backend.pipeline.retriever import retrieve
from backend.pipeline.reranker import rerank
from backend.pipeline.generator import generate_answer, NOT_FOUND_ANSWER
from backend.config import settings

router = APIRouter()

CONFIG_MODES = {
    "config_a": {"mode": "dense",  "use_reranker": False},
    "config_b": {"mode": "bm25",   "use_reranker": False},
    "config_c": {"mode": "hybrid", "use_reranker": False},
    "config_d": {"mode": "hybrid", "use_reranker": True},
    "config_e": {"mode": "hybrid", "use_reranker": True},
    "config_f": {"mode": "hybrid", "use_reranker": True},
    "config_g": {"mode": "dense",  "use_reranker": True},
}


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, ctx: UserContext = Depends(require_user("analyst"))):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    cfg_key = req.config.lower() if req.config else "config_d"
    if cfg_key not in CONFIG_MODES:
        cfg_key = "config_d"
    cfg = CONFIG_MODES[cfg_key]

    # ── Layer 1: topic + offensive guardrail ───────────────────────
    guard = check_input(req.question)
    if not guard.allowed:
        return _blocked_response(guard.reason, cfg_key)

    # ── Layer 2: ticker scope guardrail (scoped-analyst keys only) ─
    if ctx.is_scoped:
        scope_guard = check_ticker_scope(req.question, ctx.allowed_tickers)
        if not scope_guard.allowed:
            return _blocked_response(scope_guard.reason, cfg_key)

    t0 = time.perf_counter()

    try:
        candidates = retrieve(
            req.question,
            mode=cfg["mode"],
            ticker_filter=ctx.allowed_tickers,  # None = all tickers
        )
        retrieved_count = len(candidates)

        # ── Layer 3: cross-ticker hallucination guard ──────────────
        # If the question names specific tickers but none of those tickers
        # appear in the retrieved chunks, the corpus doesn't have that data.
        # Short-circuit before calling the LLM so it can't hallucinate.
        mentioned_tickers = detect_mentioned_tickers(req.question)
        if mentioned_tickers and candidates:
            retrieved_tickers = {c.ticker for c in candidates}
            if not (mentioned_tickers & retrieved_tickers):
                return _blocked_response(NOT_FOUND_ANSWER, cfg_key)

        if cfg["use_reranker"] and candidates:
            candidates = rerank(req.question, candidates)
        reranked_count = len(candidates)

        result = generate_answer(req.question, candidates)
    except Exception as e:
        logger.error(f"RAG pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    latency_ms = (time.perf_counter() - t0) * 1000

    citations = [
        Citation(
            chunk_id=c.chunk_id,
            text=c.text[:400],
            doc_id=c.doc_id,
            company=c.company,
            year=c.year,
            section=c.section,
            score=round(c.score, 4),
        )
        for c in result.citations
    ]

    try:
        save_query(
            session_id=req.session_id or "default",
            config=cfg_key,
            question=req.question,
            answer=result.answer,
            citations=[
                {"company": c.company, "year": c.year, "section": c.section, "score": round(c.score, 4)}
                for c in result.citations
            ],
            latency_ms=round(latency_ms, 1),
            retrieved_count=retrieved_count,
            reranked_count=reranked_count,
        )
    except Exception as e:
        logger.warning(f"Failed to save query to history: {e}")

    return ChatResponse(
        answer=result.answer,
        citations=citations,
        config_used=cfg_key,
        latency_ms=round(latency_ms, 1),
        retrieved_count=retrieved_count,
        reranked_count=reranked_count,
    )


def _blocked_response(reason: str, cfg_key: str) -> ChatResponse:
    return ChatResponse(
        answer=reason,
        citations=[],
        config_used=cfg_key,
        latency_ms=0.0,
        retrieved_count=0,
        reranked_count=0,
    )
