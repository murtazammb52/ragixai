---
description: Start the RAGixAI FastAPI server locally on port 8000
---

Start the RAGixAI FastAPI server locally.

Starts on port 8000 (configurable via `PORT` in `.env`).

**Serves:**
- Chat UI:   http://localhost:8000/chat
- API docs:  http://localhost:8000/docs
- Health:    http://localhost:8000/api/health

**Usage:**
- `/deploy-local`           — start server on port 8000 (with reload)
- `/deploy-local --no-reload` — production-style (no hot-reload)

Run from repo root:
```
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Prerequisites:**
1. `C:\Users\murta\anaconda3\python.exe -m pip install -r requirements.txt`
2. Ollama running: `ollama serve` (and `ollama pull llama3.2` on first run)
3. Index built: `/build-index`

Stop with `Ctrl+C`.

**API keys (from `.env`):**
| Role | Key | Access |
|------|-----|--------|
| admin | `admin-key` | All endpoints |
| analyst (AAPL) | `aapl-analyst-key` | AAPL-scoped only |
| viewer | `viewer-key` | Read-only |
