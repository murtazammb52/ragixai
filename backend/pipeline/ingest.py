"""
Download SEC EDGAR 10-K filings directly from the SEC EDGAR API.
No HuggingFace dataset dependency — uses the official SEC REST API.

API docs: https://www.sec.gov/developer
Rate limit: 10 requests/second. We stay well below this.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import httpx
from loguru import logger
from tqdm import tqdm

from backend.config import settings

DEFAULT_COMPANIES = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META",
    "NVDA", "TSLA", "JPM", "BAC", "WMT",
]

# CIK numbers for target companies (from SEC EDGAR)
TICKER_TO_CIK = {
    "AAPL": "320193",
    "MSFT": "789019",
    "AMZN": "1018724",
    "GOOGL": "1652044",
    "META": "1326801",
    "NVDA": "1045810",
    "TSLA": "1318605",
    "JPM": "19617",
    "BAC": "70858",
    "WMT": "104169",
}

# Required by SEC EDGAR API
EDGAR_HEADERS = {
    "User-Agent": "RAGixAI capstone murtazammb@gmail.com",
    "Accept-Encoding": "gzip, deflate",
}


def _cik_padded(cik: str) -> str:
    return cik.zfill(10)


def _get_recent_10k_filings(ticker: str, max_filings: int = 3) -> list[dict]:
    """Return metadata for up to max_filings 10-K filings for this ticker."""
    cik = TICKER_TO_CIK.get(ticker)
    if not cik:
        logger.warning(f"Unknown ticker {ticker} -- skipping")
        return []

    url = f"https://data.sec.gov/submissions/CIK{_cik_padded(cik)}.json"
    try:
        r = httpx.get(url, headers=EDGAR_HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logger.error(f"Failed to fetch submissions for {ticker}: {e}")
        return []

    company_name = data.get("name", ticker)
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    acc_numbers = recent.get("accessionNumber", [])
    dates = recent.get("filingDate", [])
    primary_docs = recent.get("primaryDocument", [])

    results = []
    for i, form in enumerate(forms):
        if form == "10-K" and len(results) < max_filings:
            results.append({
                "ticker": ticker,
                "company_name": company_name,
                "cik": cik,
                "accession_number": acc_numbers[i],
                "primary_document": primary_docs[i] if i < len(primary_docs) else "",
                "year": int(dates[i][:4]),
                "date": dates[i],
            })
    return results


def _get_filing_text(cik: str, accession_number: str, primary_document: str) -> str:
    """Download the primary 10-K document and return as plain text."""
    acc_clean = accession_number.replace("-", "")

    if not primary_document:
        logger.warning(f"No primary document for CIK {cik} / {accession_number}")
        return ""

    doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_clean}/{primary_document}"
    try:
        r = httpx.get(doc_url, headers=EDGAR_HEADERS, timeout=90)
        r.raise_for_status()
        text = _html_to_text(r.text)
        return text
    except Exception as e:
        logger.warning(f"Failed to download document {doc_url}: {e}")
        return ""


def _html_to_text(html: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    # Remove script/style blocks
    html = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    html = re.sub(r'<[^>]+>', ' ', html)
    # Decode common HTML entities
    html = html.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    html = html.replace('&#160;', ' ').replace('&quot;', '"').replace('&#34;', '"')
    # Normalize whitespace
    html = re.sub(r'\s+', ' ', html)
    return html.strip()


def ingest_from_edgar_api(
    companies: list[str] | None = None,
    max_filings: int = 3,
    years: list[int] | None = None,
    progress_callback=None,
) -> list[dict]:
    """
    Download 10-K filings from SEC EDGAR API and save as text files.
    Returns list of metadata dicts for ingested docs.
    """
    tickers = companies or DEFAULT_COMPANIES
    raw_dir = Path(settings.repo_root) / settings.raw_data_dir / "edgar"
    raw_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Fetching SEC EDGAR 10-K filings for: {tickers} (max {max_filings} each)")

    ingested: list[dict] = []
    total_target = len(tickers) * max_filings
    processed = 0

    for ticker in tickers:
        logger.info(f"Processing {ticker}...")
        filings = _get_recent_10k_filings(ticker, max_filings)
        time.sleep(0.15)  # polite rate limiting for SEC API

        for filing in filings:
            if years and filing["year"] not in years:
                continue

            doc_id = f"{ticker}_{filing['year']}_{filing['accession_number'].replace('-', '')[:8]}"
            company_dir = raw_dir / ticker
            company_dir.mkdir(exist_ok=True)
            out_path = company_dir / f"{doc_id}.txt"

            if out_path.exists() and out_path.stat().st_size > 1000:
                logger.info(f"Skipping {doc_id} (already downloaded)")
                meta = {
                    "doc_id": doc_id,
                    "ticker": ticker,
                    "company_name": filing["company_name"],
                    "year": filing["year"],
                    "path": str(out_path),
                    "char_count": out_path.stat().st_size,
                }
                ingested.append(meta)
                continue

            logger.info(f"Downloading {doc_id} ({filing['date']}) -- {filing.get('primary_document','?')}...")
            text = _get_filing_text(filing["cik"], filing["accession_number"], filing.get("primary_document", ""))
            time.sleep(0.15)

            if len(text) < 500:
                logger.warning(f"Too short ({len(text)} chars) for {doc_id} — skipping")
                continue

            # Keep only meaningful sections (cap at 500k chars to avoid huge files)
            text = text[:500_000]
            out_path.write_text(text, encoding="utf-8")

            meta = {
                "doc_id": doc_id,
                "ticker": ticker,
                "company_name": filing["company_name"],
                "year": filing["year"],
                "path": str(out_path),
                "char_count": len(text),
            }
            ingested.append(meta)
            processed += 1

            if progress_callback:
                progress_callback(processed / total_target, f"Ingested {doc_id}")

            logger.info(f"Saved {doc_id} ({len(text):,} chars)")

    # Update manifest
    manifest_path = raw_dir / "manifest.json"
    existing = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    existing_ids = {d["doc_id"] for d in existing}
    new_docs = [d for d in ingested if d["doc_id"] not in existing_ids]
    manifest_path.write_text(json.dumps(existing + new_docs, indent=2))

    logger.info(f"Ingestion complete — {len(ingested)} filings saved")
    return ingested


# Keep old name as alias
def ingest_from_huggingface(
    companies=None, max_filings=3, years=None, progress_callback=None
) -> list[dict]:
    return ingest_from_edgar_api(
        companies=companies, max_filings=max_filings, years=years, progress_callback=progress_callback
    )


def load_manifest() -> list[dict]:
    manifest_path = Path(settings.repo_root) / settings.raw_data_dir / "edgar" / "manifest.json"
    if not manifest_path.exists():
        return []
    return json.loads(manifest_path.read_text())
