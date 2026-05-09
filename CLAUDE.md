# RAGixAI — Claude Code Project Guide

## What This Project Is
RAGixAI is a local-first RAG (Retrieval-Augmented Generation) system over SEC EDGAR financial filings.
It answers questions about 10-K/10-Q/8-K reports with cited, scoped answers, and runs a full evaluation suite (RAGAS + LLM-as-Judge).

**10 tracked companies:** AAPL, MSFT, AMZN, GOOGL, META, NVDA, TSLA, JPM, BAC, WMT
**Corpus:** ~45 filings / ~8,976 chunks (2020–2026)
**Gold eval dataset:** FinanceBench (150 expert-annotated QA pairs, 2020–2023)

---

## Key Directories

| Path | Purpose |
|------|---------|
| `backend/` | FastAPI server (port 8000) — all RAG logic |
| `backend/api/` | FastAPI routers: chat, evaluate, judge, ingest, health, history |
| `backend/pipeline/` | ingest, chunker, embedder, indexer, retriever, reranker, generator, guardrails |
| `backend/evaluation/` | ragas_eval, llm_judge, financebench_loader, ab_test |
| `backend/models/` | schemas, auth, db, history |
| `frontend/chat.html` | Chat UI at http://localhost:8000/chat |
| `data/raw/edgar/` | Downloaded filing text files (gitignored) |
| `data/processed/chunks/` | Chunked JSONL files (gitignored) |
| `data/chroma_db/` | ChromaDB vector store — do NOT delete unless resetting |
| `scripts/` | Standalone CLI scripts for every pipeline step |
| `.claude/commands/` | 14 slash command definitions |
| `.claude/hooks/` | Pre/post tool hooks (syntax check, secret guard, requirements reminder) |

---

## Python / Environment

**Python:** Anaconda at `C:\Users\murta\anaconda3\python.exe` (Python 3.10+)
**Do NOT use:** `python`, `pip`, or `venv\Scripts\activate` — these resolve to the wrong interpreter on this machine.

Always prefix scripts with the full Anaconda path:
```
C:\Users\murta\anaconda3\python.exe scripts/run_<name>.py
```

---

## First-Time Setup

```bash
# 1. Install Ollama: https://ollama.com — then pull the model:
ollama pull llama3.2

# 2. Install Python dependencies (Anaconda pip)
C:\Users\murta\anaconda3\python.exe -m pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
# Defaults work out of the box with Ollama

# 4. Ingest + backfill (all 10 companies, 2020–2026)
C:\Users\murta\anaconda3\python.exe scripts/run_ingest.py --companies AAPL,MSFT,AMZN,GOOGL,META,NVDA,TSLA,JPM,BAC,WMT --years 2020,2021,2022,2023,2024 --max-filings 10

# 5. Chunk and build index
C:\Users\murta\anaconda3\python.exe scripts/run_chunk.py --strategy recursive
C:\Users\murta\anaconda3\python.exe scripts/run_build_index.py --reset

# 6. Start the server (from repo root)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
# Open: http://localhost:8000/chat
```

---

## Running the Server

```bash
uvicorn backend.main:app --reload
```

| URL | What |
|-----|------|
| http://localhost:8000/chat | Chat UI |
| http://localhost:8000/docs | Swagger API docs |
| http://localhost:8000/api/health | Health + index counts |

---

## Pipeline Stage Order

```
ingest → chunk → build-index → (server running) → query / evaluate
```

Each stage depends on the previous. After changing chunking strategy or re-ingesting, always run `build-index --reset`.

---

## All Scripts (from repo root)

```bash
C:\Users\murta\anaconda3\python.exe scripts/run_ingest.py --companies AAPL,MSFT --years 2020,2021,2022,2023 --max-filings 10
C:\Users\murta\anaconda3\python.exe scripts/run_chunk.py --strategy recursive
C:\Users\murta\anaconda3\python.exe scripts/run_build_index.py [--reset]
C:\Users\murta\anaconda3\python.exe scripts/run_query.py --question "Apple net sales FY2023?"
C:\Users\murta\anaconda3\python.exe scripts/run_evaluate.py --config config_d --dataset financebench --n 50
C:\Users\murta\anaconda3\python.exe scripts/run_ab_test.py --n 20 [--judge]
C:\Users\murta\anaconda3\python.exe scripts/run_judge.py --config config_d --n 20
```

---

## RAG Retrieval Configurations

| Config | Retrieval | Reranker | Notes |
|--------|-----------|----------|-------|
| A | Dense only | None | Baseline |
| B | BM25 only | None | Keyword-heavy |
| C | Hybrid (RRF) | None | Good balance |
| D | Hybrid (RRF) | CrossEncoder | **Default — best free-tier** |
| E | Hybrid (RRF) | CrossEncoder | Cohere Embed v3 (needs API key) |
| F | Hybrid (RRF) | CrossEncoder | Alternate LLM baseline |
| G | Dense only | CrossEncoder | Dense + rerank |

Default: **config_d** (best accuracy, no API key required).

---

## RBAC — API Keys

Three roles with scoped access. Keys are set in `.env` (see `.env.example`).

| Role | Key (default) | Access |
|------|--------------|--------|
| admin | `admin-key` | All endpoints, all companies |
| viewer | `viewer-key` | Read-only, all companies |
| analyst (AAPL) | `aapl-analyst-key` | AAPL-scoped only |
| analyst (MSFT) | `msft-analyst-key` | MSFT-scoped only |
| analyst (AMZN) | `amzn-analyst-key` | AMZN-scoped only |
| analyst (GOOGL) | `googl-analyst-key` | GOOGL-scoped only |
| analyst (META) | `meta-analyst-key` | META-scoped only |
| analyst (NVDA) | `nvda-analyst-key` | NVDA-scoped only |
| analyst (TSLA) | `tsla-analyst-key` | TSLA-scoped only |
| analyst (JPM) | `jpm-analyst-key` | JPM-scoped only |
| analyst (BAC) | `bac-analyst-key` | BAC-scoped only |
| analyst (WMT) | `wmt-analyst-key` | WMT-scoped only |

**RBAC is enforced at three layers:**
1. Input scope guard — blocks questions about out-of-scope tickers
2. Post-retrieval ticker intersection check — filters retrieved chunks to allowed tickers
3. Prompt rule — LLM is instructed not to use out-of-scope company data

---

## Guardrails (Three Layers)

Implemented in `backend/pipeline/guardrails.py`:
1. **Topic filter** (`_FINANCE_RE`) — passes finance questions, blocks off-topic (e.g., recipes). Handles plurals/possessives via `(?:'s|s)?\b` suffix.
2. **Ticker-scope RBAC** — rejects questions about companies outside the user's allowed tickers.
3. **Post-retrieval hallucination guard** — strips chunks whose `ticker` metadata is not in the user's allowed set.

---

## Evaluation

### RAGAS (automated metrics)
```bash
C:\Users\murta\anaconda3\python.exe scripts/run_evaluate.py --config config_d --dataset financebench --n 50
```
Metrics: faithfulness ≥ 0.89, answer_relevancy ≥ 0.87, context_precision ≥ 0.84, context_recall ≥ 0.84, answer_correctness ≥ 0.82, p95 latency < 3000ms.

### LLM-as-Judge (interpretable scoring)
```bash
C:\Users\murta\anaconda3\python.exe scripts/run_judge.py --config config_d --n 20
```
4 dimensions: faithfulness, completeness, citation_quality, hallucination_free. Scores 1–5 normalized to 0–1. Pass threshold: ≥ 0.70. Heuristic fallback if Ollama unavailable.

**Judge is evaluation-only** — it does not run at inference time (too slow, GPU conflict with generator).

### A/B Test (all 7 configs head-to-head)
```bash
C:\Users\murta\anaconda3\python.exe scripts/run_ab_test.py --n 20 --judge
```
Ranked matrix. `--judge` adds composite winner: `ragas_score + judge_overall * 2`.

---

## Gold Dataset — FinanceBench

- Source: `PatronusAI/financebench` on HuggingFace
- 150 expert-annotated QA pairs from real SEC 10-K/10-Q filings
- Covers **2020–2023** — requires backfill corpus (run `/backfill` first)
- Loaded in `backend/evaluation/financebench_loader.py`

---

## ChromaDB Collections

Each embedding model uses a separate collection (non-destructive switching):

| Collection | Model | Setting |
|------------|-------|---------|
| `ragixai_local` | sentence-transformers/all-MiniLM-L6-v2 | `EMBED_MODEL=local` (default) |
| `ragixai_cohere` | Cohere Embed v3 | `EMBED_MODEL=cohere` |

To enable Cohere (Config E): get a free API key at https://cohere.com (1000 calls/month), set `COHERE_API_KEY` and `EMBED_MODEL=cohere` in `.env`, then run `/embed-docs`.

---

## Claude Code Slash Commands (14 total)

| Command | Description |
|---------|-------------|
| `/ingest-docs` | Download SEC EDGAR filings |
| `/chunk-docs` | Chunk ingested documents |
| `/build-index` | Build ChromaDB + BM25 indexes |
| `/embed-docs` | Switch embedding model and rebuild |
| `/backfill` | Ingest 2020–2023 for FinanceBench alignment |
| `/pipeline` | Run full pipeline end-to-end |
| `/query-rag` | One-off RAG query from CLI |
| `/evaluate-rag` | RAGAS evaluation vs FinanceBench |
| `/judge` | LLM-as-Judge evaluation |
| `/ab-test-configs` | Head-to-head test all 7 configs |
| `/deploy-local` | Start FastAPI server |
| `/server` | Server management |
| `/health` | System health check |
| `/status` | Full system status snapshot |

---

## Claude Code Hooks

Configured in `.claude/settings.json`:

| Trigger | File | What It Does |
|---------|------|-------------|
| PreToolUse: Bash | `guard_secrets.py` | Blocks `git add .env`, `git add .`, `git add -A` |
| PostToolUse: Edit\|Write | `check_syntax.py` | Runs `python -m py_compile` on edited `.py` files |
| PostToolUse: Edit\|Write | `requirements_reminder.py` | Reminds to reinstall when `requirements.txt` changes |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError` | Wrong Python | Use `C:\Users\murta\anaconda3\python.exe` |
| `chroma_docs: 0` | Index not built | Run `/build-index` |
| `ollama_ok: false` | Ollama not running | Run `ollama serve` |
| "Answer not found in Corpus" | Missing 2020–2023 filings | Run `/backfill` |
| CUDA error in judge | GPU shared with generator | Expected — heuristic fallback fires |
| `git add -A` blocked | guard_secrets hook | Use `git add <specific files>` |
| FinanceBench all "not found" | Corpus only has 2024+ | Run `/backfill` with `--max-filings 10` |
| Invalid JSON from Ollama | Wrong model | Ensure `OLLAMA_MODEL=llama3.2` in `.env` |
