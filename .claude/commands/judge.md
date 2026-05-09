---
description: Run LLM-as-Judge evaluation scoring answers on 4 financial RAG dimensions
---

Score RAG answers using Ollama as judge on 4 domain-specific dimensions (faithfulness, completeness, citation_quality, hallucination_free). Each dimension scored 1–5 then normalized to 0–1. Pass threshold: ≥ 0.70.

**Usage:**
- `/judge` — evaluate config_d, 20 samples
- `/judge config_a --n 5` — quick sanity check on config_a
- `/judge config_d --n 50` — full evaluation

Run from repo root:
```
C:\Users\murta\anaconda3\python.exe scripts/run_judge.py --config $ARGUMENTS
```

**Default if no config given:**
```
C:\Users\murta\anaconda3\python.exe scripts/run_judge.py --config config_d --n 20
```

**Output:** per-dimension mean scores, PASS/FAIL vs 0.70 threshold, pass rate, fallback count.

**Note:** Requires Ollama running (`ollama serve`). If Ollama is unavailable or returns invalid JSON, heuristic fallback fires automatically (word-overlap scoring). Heuristic rows are flagged in output.

**API equivalent:**
```bash
curl -X POST http://localhost:8000/api/judge \
  -H "Authorization: Bearer admin-key" \
  -H "Content-Type: application/json" \
  -d '{"config":"config_d","sample_size":20}'
```

**Spot-check a single answer:**
```bash
curl -X POST http://localhost:8000/api/judge/row \
  -H "Authorization: Bearer analyst-key" \
  -H "Content-Type: application/json" \
  -d '{"question":"Apple net sales FY2023?","answer":"$383.3B [1]","contexts":["Apple net sales were $383.3 billion"],"ground_truth":"$383.3 billion"}'
```
