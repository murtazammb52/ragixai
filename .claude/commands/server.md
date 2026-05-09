---
description: Start, stop, or restart the RAGixAI FastAPI server
---

Manage the local RAGixAI server (FastAPI + uvicorn on port 8000).

**Quick start:**
```
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**URLs once running:**
| Endpoint | URL |
|----------|-----|
| Chat UI | http://localhost:8000/chat |
| API docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/api/health |

**Check server is up:**
```
curl http://localhost:8000/api/health
```
Response includes: `chroma_docs` (chunk count), `ollama_ok` (bool), `bm25_docs`.

**Common issues:**
- `Connection refused` → server not started; run the uvicorn command above
- `chroma_docs: 0` → run `/build-index` first
- `ollama_ok: false` → run `ollama serve` in a separate terminal

**Stop:** `Ctrl+C` in the terminal running uvicorn.
