from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from backend.api import health, chat, ingest, evaluate, history, judge
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
app.include_router(judge.router, prefix="/api", tags=["judge"])

# Serve documentation page at /documentation
frontend_dir = Path(__file__).parent.parent / "frontend"

@app.get("/documentation")
def serve_docs():
    docs_path = frontend_dir / "docs.html"
    if docs_path.exists():
        return FileResponse(str(docs_path), media_type="text/html")
    return {"error": "docs.html not found"}

# Serve static assets (gold_data.js, etc.) at /static
static_dir = frontend_dir / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Serve chat UI at /chat
if frontend_dir.exists():
    app.mount("/chat", StaticFiles(directory=str(frontend_dir), html=True), name="chat")

# Serve root-level static site pages (nav links from /chat use ../<page>.html → /<page>.html)
site_dir = Path(__file__).parent.parent
_site_pages = ["index.html", "pipeline.html", "evaluation.html", "solution.html",
               "roadmap.html", "problem.html", "aws.html"]

for _page in _site_pages:
    _path = site_dir / _page
    if _path.exists():
        app.get(f"/{_page}")(lambda p=str(_path): FileResponse(p, media_type="text/html"))

# Serve CSS and JS asset directories used by the static site pages
for _asset_dir, _mount in [("css", "/css"), ("js", "/js")]:
    _d = site_dir / _asset_dir
    if _d.exists():
        app.mount(_mount, StaticFiles(directory=str(_d)), name=_asset_dir)


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
        "documentation": "/documentation",
        "api_docs": "/docs",
        "health": "/api/health",
    }
