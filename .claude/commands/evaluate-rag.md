---
description: Run RAGAS evaluation on a RAG config against FinanceBench gold dataset
---

Evaluate a RAG configuration using **FinanceBench** (150 expert-annotated QA pairs from real SEC filings).

**RAGAS metrics computed:**
- Faithfulness ≥ 0.89
- Answer Relevancy ≥ 0.87
- Context Precision ≥ 0.84
- Context Recall ≥ 0.84
- Answer Correctness ≥ 0.82
- p95 Latency < 3000ms

**Usage:**
- `/evaluate-rag` — config_d, 50 samples
- `/evaluate-rag config_a` — test a specific config
- `/evaluate-rag config_d --n 20` — quick test with 20 samples

Run from repo root:
```
C:\Users\murta\anaconda3\python.exe scripts/run_evaluate.py --config $ARGUMENTS --dataset financebench --n 50
```

**For LLM-as-Judge evaluation instead** (interpretable per-dimension scoring):
```
C:\Users\murta\anaconda3\python.exe scripts/run_judge.py --config config_d --n 20
```

**FinanceBench coverage note:** FinanceBench covers 2020–2023. Run `/backfill` first to ensure your corpus covers those years, otherwise many questions will return "Answer not found in Corpus".
