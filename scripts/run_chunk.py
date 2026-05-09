"""CLI: python scripts/run_chunk.py --strategy recursive"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.pipeline.chunker import chunk_all_docs


def main():
    parser = argparse.ArgumentParser(description="Chunk all ingested EDGAR documents")
    parser.add_argument("--strategy", type=str, default="recursive",
                        choices=["fixed", "recursive", "semantic"],
                        help="Chunking strategy (default: recursive)")
    args = parser.parse_args()

    def progress(pct, msg):
        print(f"[{pct*100:.0f}%] {msg}")

    chunks = chunk_all_docs(strategy=args.strategy, progress_callback=progress)
    print(f"\nCreated {len(chunks)} chunks using '{args.strategy}' strategy")


if __name__ == "__main__":
    main()
