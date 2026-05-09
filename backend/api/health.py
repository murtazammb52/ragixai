from fastapi import APIRouter, Depends
from backend.models.db import get_collection, get_bm25_index
from backend.models.schemas import HealthResponse
from backend.models.auth import UserContext, require_user
from backend.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    try:
        collection = get_collection()
        doc_count = collection.count()
    except Exception:
        doc_count = 0

    _, bm25_ids = get_bm25_index()

    return HealthResponse(
        status="ok",
        chroma_docs=doc_count,
        embedding_model=settings.embed_model_name if settings.embed_model == "local" else "cohere-embed-english-v3.0",
        llm_model=settings.ollama_model,
        bm25_index_size=len(bm25_ids),
    )


@router.get("/me")
def me(ctx: UserContext = Depends(require_user("viewer"))):
    """Validate API key and return the caller's role and ticker scope."""
    return {
        "role": ctx.role,
        "tickers": ctx.allowed_tickers,  # null = all tickers
        "scoped": ctx.is_scoped,
    }
