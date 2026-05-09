---
description: Ingest historical EDGAR filings (2020-2023) to cover FinanceBench gold dataset
---

Ingest older SEC EDGAR filings to cover years 2020–2023, which FinanceBench questions target.

**Why:** FinanceBench has 150 expert-annotated QA pairs covering financial years 2020–2023. Without these filings, many questions return "Answer not found in Corpus."

**Usage:**
- `/backfill` — ingest 2020–2023 for all 10 tracked companies
- `/backfill AAPL,MSFT --years 2020,2021` — specific companies/years

Run from repo root (fetch all 10 companies, 2020–2023):
```
C:\Users\murta\anaconda3\python.exe scripts/run_ingest.py --companies AAPL,MSFT,AMZN,GOOGL,META,NVDA,TSLA,JPM,BAC,WMT --years 2020,2021,2022,2023 --max-filings 10
```

**Important:** `--max-filings 10` is required. SEC EDGAR returns the N most-recent filings before year filtering. With `--max-filings 3`, only 2023–2025 filings are fetched and year filter eliminates them all.

**After backfill, rebuild the index:**
```
C:\Users\murta\anaconda3\python.exe scripts/run_chunk.py
C:\Users\murta\anaconda3\python.exe scripts/run_build_index.py --reset
```

**Current corpus target:** ~45 filings / ~8,976 chunks (all companies, 2020–2026).

**Verify coverage:**
```
curl http://localhost:8000/api/health
```
`chroma_docs` should be ≥ 8,000 after full backfill.
