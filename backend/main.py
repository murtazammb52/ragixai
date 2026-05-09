from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from backend.api import health, chat, ingest, evaluate, history
from backend.config import settings
from backend.models.db import build_bm25_index
from backend.models.history import init_db

app = FastAPI(title="RAGixAI", description="SEC EDGAR Financial RAG System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(evaluate.router, prefix="/api", tags=["evaluate"])
app.include_router(history.router, prefix="/api", tags=["history"])

# Serve chat UI at /chat
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/chat", StaticFiles(directory=str(frontend_dir), html=True), name="chat")

# Serve existing static site at /site
site_dir = Path(__file__).parent.parent
static_files = ["index.html", "css", "js", "pipeline.html", "evaluation.html", "aws.html", "roadmap.html", "problem.html", "solution.html"]


@app.on_event("startup")
async def startup():
    logger.info("RAGixAI starting up...")
    init_db()
    try:
        build_bm25_index()
    except Exception as e:
        logger.warning(f"BM25 index build on startup failed (collection may be empty): {e}")
    logger.info(f"Server ready — Chat UI: http://localhost:{settings.port}/chat")
    logger.info(f"API docs: http://localhost:{settings.port}/docs")


@app.get("/")
def root():
    return {
        "name": "RAGixAI",
        "description": "SEC EDGAR Financial RAG System",
        "chat_ui": "/chat",
        "api_docs": "/docs",
        "health": "/api/health",
    }
