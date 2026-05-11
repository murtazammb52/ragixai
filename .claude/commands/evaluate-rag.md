---
description: Run RAGAS evaluation on a RAG config against FinanceBench gold dataset
---

Evaluate a RAG configuration using **FinanceBench** (150 expert-annotated QA pairs from real SEC filings).

**RAGAS metrics computed (targets calibrated for llama3.2 3B self-evaluation on MX450):**
- Faithfulness ≥ 0.70
- Answer Relevancy ≥ 0.68
- Context Precision ≥ 0.66
- Context Recall ≥ 0.64
- Answer Correctness ≥ 0.62
- p95 Latency < 165,000ms (165s) — reranker configs (D/E/F/G) ~148–162s ✓, no-reranker configs (A/B/C) ~171–183s ✗

**Note:** The same 3B model both generates and evaluates answers — self-agreement bias inflates faithfulness scores. These targets are not comparable to GPT-4-evaluated benchmarks.

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
