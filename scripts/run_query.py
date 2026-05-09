"""CLI: python scripts/run_query.py --question "What were Apple's net sales in FY2023?" --config config_d"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.pipeline.retriever import retrieve
from backend.pipeline.reranker import rerank
from backend.pipeline.generator import generate_answer
from backend.config import settings

CONFIG_MODES = {
    "config_a": {"mode": "dense",  "reranker": False},
    "config_b": {"mode": "bm25",   "reranker": False},
    "config_c": {"mode": "hybrid", "reranker": False},
    "config_d": {"mode": "hybrid", "reranker": True},
    "config_e": {"mode": "hybrid", "reranker": True},  # same as D; E uses Cohere embed
    "config_f": {"mode": "hybrid", "reranker": True},
    "config_g": {"mode": "dense",  "reranker": True},
}


def main():
    parser = argparse.ArgumentParser(description="Query the RAG pipeline")
    parser.add_argument("--question", "-q", required=True, help="Question to ask")
    parser.add_argument("--config", default="config_d", choices=list(CONFIG_MODES), help="RAG config to use")
    parser.add_argument("--top-k", type=int, default=None, help="Override top_k_retrieve")
    args = parser.parse_args()

    cfg = CONFIG_MODES[args.config]
    t0 = time.perf_counter()

    candidates = retrieve(args.question, top_k=args.top_k, mode=cfg["mode"])
    print(f"\nRetrieved {len(candidates)} chunks")

    if cfg["reranker"] and candidates:
        candidates = rerank(args.question, candidates)
        print(f"Reranked → top {len(candidates)} chunks")

    result = generate_answer(args.question, candidates)
    latency = (time.perf_counter() - t0) * 1000

    print(f"\n{'='*60}")
    print(f"ANSWER (config={args.config}, latency={latency:.0f}ms):")
    print(f"{'='*60}")
    print(result.answer)
    print(f"\n{'─'*60}")
    print("CITATIONS:")
    for i, c in enumerate(result.citations, 1):
        print(f"  [{i}] {c.company} {c.year} — score: {c.score:.3f}")
        print(f"       {c.text[:120]}...")


if __name__ == "__main__":
    main()
