"""CLI: python scripts/run_ab_test.py --n 20 [--configs config_a,config_d]"""
import os
import argparse
import sys
from pathlib import Path

# Prevent RAGAS analytics from spawning a subprocess that crashes on Windows
os.environ.setdefault("RAGAS_DO_NOT_TRACK", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
# Note: CUDA_VISIBLE_DEVICES is NOT blanked here — Ollama uses GPU for generation

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.evaluation.ab_test import run_ab_test


def main():
    parser = argparse.ArgumentParser(description="Run A/B test across all 7 RAG configurations")
    parser.add_argument("--n", type=int, default=20, help="Samples per config (default: 20)")
    parser.add_argument("--configs", type=str, default=None, help="Comma-separated configs to test (default: all 7)")
    parser.add_argument("--dataset", default="financebench", choices=["financebench", "ragas_testset"])
    parser.add_argument("--judge", action="store_true",
                        help="Also run LLM-as-Judge alongside RAGAS (slower)")
    args = parser.parse_args()

    configs = [c.strip() for c in args.configs.split(",")] if args.configs else None
    result = run_ab_test(configs=configs, dataset=args.dataset, sample_size=args.n,
                         run_judge=args.judge)

    print(f"\n\n★ Winner: {result.winner}")
    print(f"\nComparison table saved. Full results for {len(result.results)} configs.")


if __name__ == "__main__":
    main()
