"""
Load FinanceBench gold-standard QA pairs from HuggingFace.
PatronusAI/financebench: 150 expert-annotated QA pairs from real SEC filings.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from loguru import logger


@dataclass
class QAPair:
    question: str
    ground_truth: str
    source_doc: str
    company: str = ""


# Column names in the HuggingFace dataset (as of 2025)
_COL_CANDIDATES = {
    "question": ["question"],
    "answer":   ["answer", "expected_answer", "ground_truth"],
    "doc_name": ["doc_name", "source", "document_name", "doc"],
}


def _get(row: dict, candidates: list[str], default: str = "") -> str:
    for key in candidates:
        if key in row and row[key]:
            return str(row[key])
    return default


def load_financebench(sample_size: int = 50) -> list[QAPair]:
    """Load up to sample_size QA pairs from FinanceBench."""
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

    from datasets import load_dataset
    logger.info(f"Loading FinanceBench (sample_size={sample_size})...")

    # Try loading without trust_remote_code (deprecated in datasets >= 2.20)
    for kwargs in [
        {"split": "train"},
        {"split": "train", "trust_remote_code": True},
    ]:
        try:
            ds = load_dataset("PatronusAI/financebench", **kwargs)
            break
        except TypeError:
            continue
        except Exception as e:
            logger.warning(f"FinanceBench load attempt failed ({kwargs}): {e}")
            ds = None
            continue
    else:
        ds = None

    if ds is None:
        logger.error("All FinanceBench load attempts failed — using fallback samples")
        return _fallback_samples()

    pairs = []
    for row in ds.select(range(min(sample_size, len(ds)))):
        row = dict(row)
        question    = _get(row, _COL_CANDIDATES["question"])
        answer      = _get(row, _COL_CANDIDATES["answer"])
        doc_name    = _get(row, _COL_CANDIDATES["doc_name"])
        if not question or not answer:
            continue
        pairs.append(QAPair(
            question=question,
            ground_truth=answer,
            source_doc=doc_name,
            company=_extract_company(doc_name),
        ))

    if not pairs:
        logger.warning("FinanceBench loaded 0 valid pairs — using fallback")
        return _fallback_samples()

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
    """30 hardcoded QA pairs covering all 10 tracked companies (2020-2023)."""
    return [
        QAPair("What were Apple's total net sales in FY2023?", "$383.3 billion", "AAPL_2023_10K", "AAPL"),
        QAPair("What was Apple's net income for fiscal year 2022?", "$99.8 billion", "AAPL_2022_10K", "AAPL"),
        QAPair("What was Apple's revenue from iPhone in FY2021?", "$191.97 billion", "AAPL_2021_10K", "AAPL"),
        QAPair("What was Microsoft's total revenue in fiscal year 2023?", "$211.9 billion", "MSFT_2023_10K", "MSFT"),
        QAPair("What was Microsoft's cloud revenue in FY2023?", "$87.9 billion", "MSFT_2023_10K", "MSFT"),
        QAPair("What was Microsoft's net income for FY2022?", "$72.7 billion", "MSFT_2022_10K", "MSFT"),
        QAPair("What was Amazon's net sales in 2022?", "$513.98 billion", "AMZN_2022_10K", "AMZN"),
        QAPair("What is Amazon AWS revenue for 2022?", "$62.2 billion", "AMZN_2022_10K", "AMZN"),
        QAPair("What was Amazon's operating income in 2021?", "$24.88 billion", "AMZN_2021_10K", "AMZN"),
        QAPair("What was Alphabet's total revenue in 2022?", "$282.8 billion", "GOOGL_2022_10K", "GOOGL"),
        QAPair("What was Google's advertising revenue in 2021?", "$209.49 billion", "GOOGL_2021_10K", "GOOGL"),
        QAPair("What was Alphabet's net income for 2023?", "$73.8 billion", "GOOGL_2023_10K", "GOOGL"),
        QAPair("What was Meta's total revenue in 2022?", "$116.6 billion", "META_2022_10K", "META"),
        QAPair("What was Meta's net income in 2021?", "$39.37 billion", "META_2021_10K", "META"),
        QAPair("What was Meta's advertising revenue in 2023?", "$131.9 billion", "META_2023_10K", "META"),
        QAPair("What was NVIDIA's total revenue for fiscal year 2023?", "$26.97 billion", "NVDA_2023_10K", "NVDA"),
        QAPair("What was NVIDIA's data center revenue in FY2022?", "$15.0 billion", "NVDA_2022_10K", "NVDA"),
        QAPair("What was NVIDIA's net income for fiscal year 2024?", "$29.76 billion", "NVDA_2024_10K", "NVDA"),
        QAPair("What was Tesla's total revenue in 2022?", "$81.46 billion", "TSLA_2022_10K", "TSLA"),
        QAPair("What was Tesla's net income in 2021?", "$5.52 billion", "TSLA_2021_10K", "TSLA"),
        QAPair("What was Tesla's automotive revenue in 2023?", "$82.42 billion", "TSLA_2023_10K", "TSLA"),
        QAPair("What was JPMorgan Chase's net revenue in 2022?", "$128.7 billion", "JPM_2022_10K", "JPM"),
        QAPair("What was JPMorgan Chase's net income in 2021?", "$48.3 billion", "JPM_2021_10K", "JPM"),
        QAPair("What was JPMorgan's total assets in 2023?", "$3.87 trillion", "JPM_2023_10K", "JPM"),
        QAPair("What was Bank of America's total revenue in 2022?", "$94.95 billion", "BAC_2022_10K", "BAC"),
        QAPair("What was Bank of America's net income in 2021?", "$31.98 billion", "BAC_2021_10K", "BAC"),
        QAPair("What was Bank of America's total assets in 2023?", "$3.18 trillion", "BAC_2023_10K", "BAC"),
        QAPair("What was Walmart's total revenue for fiscal year 2023?", "$611.3 billion", "WMT_2023_10K", "WMT"),
        QAPair("What was Walmart's net income for fiscal year 2022?", "$13.67 billion", "WMT_2022_10K", "WMT"),
        QAPair("What was Walmart's US comparable store sales growth in FY2021?", "8.6%", "WMT_2021_10K", "WMT"),
    ]
