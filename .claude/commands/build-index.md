---
description: Build or rebuild the ChromaDB vector index and BM25 index from chunked documents
---

Embeds all chunks into ChromaDB (dense index) and builds the in-memory BM25 sparse index.
Both indexes are required for hybrid retrieval (configs C–G).

**Usage:**
- `/build-index` — add new chunks to existing index (incremental)
- `/build-index --reset` — wipe collection and rebuild from scratch (use after re-chunking)

Run from repo root:
```
C:\Users\murta\anaconda3\python.exe scripts/run_build_index.py $ARGUMENTS
```

**Embedding models (set in `.env`):**
- `EMBED_MODEL=local` — `sentence-transformers/all-MiniLM-L6-v2`, no key needed (default)
- `EMBED_MODEL=cohere` — Cohere Embed v3, requires `COHERE_API_KEY` (Config E)

Each model uses its own ChromaDB collection (`ragixai_local` / `ragixai_cohere`).

**After building:** restart the server or verify with `GET http://localhost:8000/api/health` — `chroma_docs` should match total chunk count.

**Pipeline order:** `/ingest-docs` → `/chunk-docs` → build-index → server ready
