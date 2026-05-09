"""
Load FinanceBench gold-standard QA pairs from HuggingFace.
PatronusAI/financebench: 150 expert-annotated QA pairs from real SEC filings.
"""
from __future__ import annotations

from dataclasses import dataclass
from loguru import logger


@dataclass
class QAPair:
    question: str
    ground_truth: str
    source_doc: str
    company: str = ""


def load_financebench(sample_size: int = 50) -> list[QAPair]:
    """Load up to sample_size QA pairs from FinanceBench."""
    from datasets import load_dataset
    logger.info(f"Loading FinanceBench (sample_size={sample_size})...")
    try:
        ds = load_dataset("PatronusAI/financebench", split="train", trust_remote_code=True)
    except Exception as e:
        logger.error(f"Failed to load FinanceBench: {e}")
        return _fallback_samples()

    pairs = []
    for row in ds.select(range(min(sample_size, len(ds)))):
        company = _extract_company(row.get("doc_name", ""))
        pairs.append(QAPair(
            question=row.get("question", ""),
            ground_truth=row.get("answer", ""),
            source_doc=row.get("doc_name", ""),
            company=company,
        ))

    logger.info(f"Loaded {len(pairs)} FinanceBench QA pairs")
    return pairs


def _extract_company(doc_name: str) -> str:
    name = doc_name.lower()
    mapping = {
        "apple": "AAPL", "microsoft": "MSFT", "amazon": "AMZN",
        "alphabet": "GOOGL", "google": "GOOGL", "meta": "META",
        "facebook": "META", "nvidia": "NVDA", "tesla": "TSLA",
        "jpmorgan": "JPM", "jp morgan": "JPM", "bank of america": "BAC",
        "walmart": "WMT",
    }
    for k, v in mapping.items():
        if k in name:
            return v
    return doc_name[:10]


def _fallback_samples() -> list[QAPair]:
    """Minimal hardcoded samples in case HuggingFace is unavailable."""
    return [
        QAPair("What were Apple's total net sales in FY2023?", "$383.3 billion", "AAPL_2023_10K", "AAPL"),
        QAPair("What was Microsoft's cloud revenue in FY2023?", "$87.9 billion", "MSFT_2023_10K", "MSFT"),
        QAPair("What is Amazon AWS revenue for 2022?", "$62.2 billion", "AMZN_2022_10K", "AMZN"),
    ]
