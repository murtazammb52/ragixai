---
description: Run a one-off RAG query from the command line against the local index
---

Run a one-off RAG query from the command line.

**Usage:**
- `/query-rag "What were Apple's net sales in FY2023?"`
- `/query-rag "Apple net sales" --config config_a`
- `/query-rag "NVIDIA revenue breakdown" --config config_e`

Available configs: `config_a` through `config_g`
Default: `config_d` (Hybrid + CrossEncoder reranker — best free-tier accuracy)

Run from repo root:
```
C:\Users\murta\anaconda3\python.exe scripts/run_query.py --question "$ARGUMENTS" --config config_d
```

**Outputs:** answer text, citations with company/year/score, end-to-end latency.

**Prerequisites:** index built (`/build-index`) and Ollama running (`ollama serve`).
