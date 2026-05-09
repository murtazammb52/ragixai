---
description: Show RAGixAI system status — server, index, corpus, and config summary
---

Print a full system status snapshot.

**Run from repo root:**
```
C:\Users\murta\anaconda3\python.exe scripts/run_status.py
```

**Or check manually:**

```bash
# 1. Server + index health
curl http://localhost:8000/api/health

# 2. Corpus summary (filing count per company/year)
C:\Users\murta\anaconda3\python.exe -c "
import json, pathlib
chunks = list(pathlib.Path('data/processed/chunks').glob('*.jsonl'))
print('Chunk files:', len(chunks))
"

# 3. ChromaDB collection sizes
C:\Users\murta\anaconda3\python.exe -c "
import chromadb
c = chromadb.PersistentClient('data/chroma_db')
for col in c.list_collections():
    print(col.name, col.count())
"

# 4. Ollama models available
ollama list
```

**What to check:**
| Item | Healthy |
|------|---------|
| Server status | `status: ok` |
| `chroma_docs` | ≥ 8,000 (full backfill) |
| `ollama_ok` | `true` |
| `ollama_model` | `llama3.2` |
| `embed_model` | `local` (or `cohere` if Config E) |
