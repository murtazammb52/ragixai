---
description: Switch embedding model and rebuild the vector index (local vs Cohere)
---

Change the embedding model and rebuild the ChromaDB collection from scratch.

**Available embedding models:**

| Model | Setting | Quality | Speed | Cost |
|-------|---------|---------|-------|------|
| `all-MiniLM-L6-v2` | `EMBED_MODEL=local` | Good | Fast | Free |
| Cohere Embed v3 | `EMBED_MODEL=cohere` | Best | Medium | Free tier (1000/mo) |

**To switch to Cohere (Config E):**
1. Get a free key at https://cohere.com
2. Set in `.env`: `EMBED_MODEL=cohere` and `COHERE_API_KEY=your_key`
3. Run `/embed-docs` to rebuild with Cohere embeddings

**To switch back to local:**
1. Set in `.env`: `EMBED_MODEL=local`
2. Run `/embed-docs` to rebuild with local embeddings

Run from repo root:
```
C:\Users\murta\anaconda3\python.exe scripts/run_build_index.py --reset
```

Each model uses a separate ChromaDB collection so switching is non-destructive — both are preserved.
Collections: `ragixai_local` (default) and `ragixai_cohere` (Cohere).
