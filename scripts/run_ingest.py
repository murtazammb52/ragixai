"""CLI: python scripts/run_ingest.py --companies AAPL,MSFT --max-filings 3"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from backend.pipeline.ingest import ingest_from_huggingface, DEFAULT_COMPANIES


def main():
    parser = argparse.ArgumentParser(description="Ingest SEC EDGAR filings from HuggingFace")
    parser.add_argument("--companies", type=str, default=None,
                        help="Comma-separated tickers (default: 10 preset companies)")
    parser.add_argument("--max-filings", type=int, default=3,
                        help="Max filings per company (default: 3)")
    parser.add_argument("--years", type=str, default=None,
                        help="Comma-separated years to filter, e.g. 2018,2019,2020")
    args = parser.parse_args()

    companies = [c.strip().upper() for c in args.companies.split(",")] if args.companies else DEFAULT_COMPANIES
    years = [int(y) for y in args.years.split(",")] if args.years else None

    def progress(pct, msg):
        logger.info(f"[{pct*100:.0f}%] {msg}")

    docs = ingest_from_huggingface(companies=companies, max_filings=args.max_filings, years=years, progress_callback=progress)
    print(f"\nIngested {len(docs)} documents")
    for d in docs:
        print(f"   {d['doc_id']:30s}  {d['char_count']:>10,} chars")


if __name__ == "__main__":
    main()
