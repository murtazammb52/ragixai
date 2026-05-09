---
description: Chunk all ingested EDGAR documents into overlapping text segments
---

Split raw filing texts into overlapping chunks stored in `data/processed/chunks/chunks_recursive.jsonl`.
Each chunk carries full metadata: ticker, company, year, section, chunk_index.

**Strategies:**
- `recursive` (default) — respects sentence/paragraph boundaries, best quality
- `fixed` — exact 512-token splits via tiktoken
- `semantic` — splits at topic-shift boundaries using sentence embeddings

**Usage:**
- `/chunk-docs` — recursive strategy (default, recommended)
- `/chunk-docs fixed` — fixed-size chunks
- `/chunk-docs semantic` — semantic boundary detection

Run from repo root:
```
C:\Users\murta\anaconda3\python.exe scripts/run_chunk.py --strategy $ARGUMENTS
```

**Pipeline order:** `/ingest-docs` → chunk → `/build-index`

Existing chunks are fully replaced each run (not incremental). After chunking, run `/build-index --reset` to re-embed.
