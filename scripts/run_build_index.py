"""CLI: python scripts/run_build_index.py [--reset] [--strategy recursive]"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.pipeline.indexer import build_index


def main():
    parser = argparse.ArgumentParser(description="Build ChromaDB vector index from chunks")
    parser.add_argument("--reset", action="store_true",
                        help="Delete existing collection before indexing")
    parser.add_argument("--strategy", type=str, default=None,
                        help="Chunking strategy to load (default: from .env)")
    args = parser.parse_args()

    n = build_index(strategy=args.strategy, reset=args.reset)
    print(f"\nIndex built -- {n} chunks indexed")


if __name__ == "__main__":
    main()
