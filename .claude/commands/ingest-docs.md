---
description: Download SEC EDGAR 10-K filings for specified companies and years
---

Download 10-K filings directly from the **SEC EDGAR REST API** into `data/raw/edgar/`.
Already-downloaded files are skipped automatically — safe to re-run.

**Default companies (10):** AAPL, MSFT, AMZN, GOOGL, META, NVDA, TSLA, JPM, BAC, WMT

**Usage:**
- `/ingest-docs` — all 10 companies, 3 most recent filings each
- `/ingest-docs AAPL,MSFT` — subset of companies
- `/ingest-docs AAPL,MSFT --max-filings 5` — 5 filings each
- `/ingest-docs --years 2020,2021,2022,2023 --max-filings 10` — backfill for FinanceBench

Run from repo root:
```
C:\Users\murta\anaconda3\python.exe scripts/run_ingest.py $ARGUMENTS
```

**Pipeline order:** ingest → `/chunk-docs` → `/build-index`

**FinanceBench tip:** FinanceBench covers 2020–2023. Use `--years 2020,2021,2022,2023 --max-filings 10` to backfill so evaluation questions hit the corpus. Or run `/backfill` which does this automatically.
