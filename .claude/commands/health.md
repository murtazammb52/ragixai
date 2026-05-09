---
description: Check RAGixAI system health — Ollama, ChromaDB, BM25, and index counts
---

Check the health of all RAGixAI subsystems.

```
curl http://localhost:8000/api/health
```

**Expected healthy response:**
```json
{
  "status": "ok",
  "chroma_docs": 8976,
  "bm25_docs": 8976,
  "ollama_ok": true,
  "embed_model": "local",
  "ollama_model": "llama3.2"
}
```

**What each field means:**
| Field | Healthy value | Fix if wrong |
|-------|--------------|--------------|
| `chroma_docs` | ≥ 1 (ideally 8976) | Run `/build-index` |
| `bm25_docs` | matches `chroma_docs` | Run `/build-index` |
| `ollama_ok` | `true` | Run `ollama serve` |
| `embed_model` | `local` or `cohere` | Check `.env` `EMBED_MODEL` |
| `ollama_model` | `llama3.2` | Check `.env` `OLLAMA_MODEL` |

**If server is not running:**
Start it first with `/server` (or `/deploy-local`).
