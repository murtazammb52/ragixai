---
description: Run the full RAGixAI pipeline end-to-end: ingest → chunk → index → verify
---

Run the complete data pipeline from scratch. Use this for a fresh setup or after a corpus reset.

**Full pipeline (all 10 companies, 2020–2026):**

```bash
# Step 1: Ingest (downloads 10-K/10-Q filings from SEC EDGAR)
C:\Users\murta\anaconda3\python.exe scripts/run_ingest.py \
  --companies AAPL,MSFT,AMZN,GOOGL,META,NVDA,TSLA,JPM,BAC,WMT \
  --years 2020,2021,2022,2023,2024 --max-filings 10

# Step 2: Chunk (splits into overlapping segments with metadata)
C:\Users\murta\anaconda3\python.exe scripts/run_chunk.py --strategy recursive

# Step 3: Build index (embeds into ChromaDB + builds BM25)
C:\Users\murta\anaconda3\python.exe scripts/run_build_index.py --reset

# Step 4: Verify
curl http://localhost:8000/api/health
```

**Dependency order:** ingest → chunk → build-index → server ready to serve queries

**Individual steps:**
- `/ingest-docs` — download only
- `/chunk-docs` — rechunk only (after re-ingesting)
- `/build-index` — reindex only (after rechunking)
- `/backfill` — add historical years for FinanceBench coverage

**Time estimates (10 companies, 5 years):**
| Step | Duration |
|------|----------|
| Ingest | 5–15 min (network) |
| Chunk | 2–5 min |
| Build index | 10–20 min (CPU embedding) |
