"""CLI: python scripts/run_build_index.py [--reset] [--resume] [--batch-size N]"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.pipeline.indexer import build_index, BATCH_SIZE


def main():
    parser = argparse.ArgumentParser(description="Build ChromaDB vector index from chunks")
    parser.add_argument("--reset", action="store_true",
                        help="Delete existing collection before indexing (full rebuild)")
    parser.add_argument("--resume", action="store_true",
                        help="Skip already-indexed chunks and continue from where a previous run stopped")
    parser.add_argument("--strategy", type=str, default=None,
                        help="Chunking strategy to load (default: from .env)")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE,
                        help=f"Chunks per embedding batch (default: {BATCH_SIZE})")
    args = parser.parse_args()

    n = build_index(
        strategy=args.strategy,
        reset=args.reset,
        resume=args.resume,
        batch_size=args.batch_size,
    )
    print(f"\nIndex built — {n} new chunks indexed")


if __name__ == "__main__":
    main()
