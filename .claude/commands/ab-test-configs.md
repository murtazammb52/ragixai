---
description: Run head-to-head A/B test across all 7 RAG retrieval configurations
---

Compare all 7 RAG configs on FinanceBench and print a ranked matrix with RAGAS metrics.
Optionally adds LLM-as-Judge scores alongside RAGAS for composite winner selection.

**Configs:**
| Config | Retrieval | Reranker | Notes |
|--------|-----------|----------|-------|
| A | Dense only | None | Baseline |
| B | BM25 only | None | Keyword-heavy |
| C | Hybrid (RRF) | None | Good balance |
| D | Hybrid (RRF) | CrossEncoder | **Default — best free-tier** |
| E | Hybrid (RRF) | CrossEncoder | Cohere Embed v3 — needs API key |
| F | Hybrid (RRF) | CrossEncoder | Alternate LLM baseline |
| G | Dense only | CrossEncoder | Dense + rerank |

**Usage:**
- `/ab-test-configs` — all 7 configs, 20 samples each (~30 min)
- `/ab-test-configs --n 5` — quick sanity check (5 min)
- `/ab-test-configs --configs config_a,config_d --n 10` — compare two specific configs
- `/ab-test-configs --n 10 --judge` — include LLM-as-Judge scores (slower)

Run from repo root:
```
C:\Users\murta\anaconda3\python.exe scripts/run_ab_test.py $ARGUMENTS
```

**Output:** Ranked table with faithfulness, relevancy, precision, recall, correctness, latency. Winner marked with ★.
