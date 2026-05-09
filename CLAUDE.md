# RAGixAI — Claude Code Project Guide

## What This Project Is
RAGixAI is a local-first RAG (Retrieval-Augmented Generation) system over SEC EDGAR financial filings.
It answers questions about 10-K/10-Q/8-K reports with cited answers, and runs a full evaluation suite (RAGAS).

## Key Directories
- `backend/` — FastAPI Python server (port 8000), owns all RAG logic
- `frontend/chat.html` — Chat UI served at http://localhost:8000/chat
- `data/raw/edgar/` — downloaded 10-K text files
- `data/chroma_db/` — ChromaDB vector store (do NOT delete unless resetting)
- `scripts/` — standalone CLI scripts for pipeline steps
- `.claude/commands/` — 8 slash command skill files

## Setup (First Time)
```bash
# 1. Install Ollama: https://ollama.com → then:
ollama pull llama3.2

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# 3. Install Python deps
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env if needed (default settings work out of the box with Ollama)

# 5. Ingest documents and build index (run once)
python scripts/run_ingest.py --companies AAPL,MSFT,AMZN,GOOGL,META
python scripts/run_chunk.py
python scripts/run_build_index.py

# 6. Start the server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
# Then open: http://localhost:8000/chat
```

## Running the Server
```bash
uvicorn backend.main:app --reload   # from repo root
```
The server serves:
- API: http://localhost:8000/api/*
- Chat UI: http://localhost:8000/chat
- API docs: http://localhost:8000/docs

## Pipeline Stage Order (dependencies)
ingest → chunk → build-index → (server running) → query / evaluate

## All Scripts Must Run from Repo Root
```bash
python scripts/run_ingest.py --companies AAPL,MSFT
python scripts/run_chunk.py --strategy recursive
python scripts/run_build_index.py [--reset]
python scripts/run_query.py --question "What were Apple's net sales in FY2023?"
python scripts/run_evaluate.py --config config_d --dataset financebench --n 50
python scripts/run_ab_test.py --n 20
```

## Config E (Cohere Embed v3)
Config E uses Cohere Embed v3 for superior embeddings. To enable:
1. Get a free Cohere API key at https://cohere.com (1000 calls/month free)
2. Set `COHERE_API_KEY=your_key` and `EMBED_MODEL=cohere` in `.env`
3. Re-run `/build-index` to re-embed with Cohere

## ChromaDB Collections
Each embedding model gets its own collection:
- `ragixai_local` — sentence-transformers (default)
- `ragixai_cohere` — Cohere Embed v3 (Config E)

## Python Version
Requires Python 3.10+
