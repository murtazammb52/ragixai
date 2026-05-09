"""
Input guardrails for the RAG pipeline.
- Topic guard: only SEC/finance-related questions pass
- Offensive guard: blocks abusive/harmful content
- Ticker scope guard: scoped-analyst keys can only query their assigned tickers

Company detection uses TICKER symbols (AAPL, MSFT, …) as canonical identifiers
because they are standardised and never vary across SEC filings or HuggingFace
datasets, unlike company names ("Apple Inc." vs "APPLE INC." vs "Apple").
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# ── Topic filter ─────────────────────────────────────────────────────────────
_FINANCE_RE = re.compile(
    r"\b("
    r"revenue|profit|loss|earn(?:ing|ings|ed)?|eps|ebitda|ebit|margin|"
    r"income|expense|cash\s*flow|balance\s*sheet|asset|liabilit|equit|"
    r"debt|loan|credit|share|stock|dividend|market\s*cap|valuation|"
    r"sec|10-?k|10-?q|8-?k|annual\s*report|quarterly|filing|"
    r"fiscal|financial|quarter|guidance|forecast|outlook|"
    r"acqui|merger|divestiture|buyback|ipo|"
    r"apple|microsoft|amazon|google|alphabet|meta|nvidia|tesla|jpmorgan|"
    r"aapl|msft|amzn|googl|goog|nvda|tsla|jpm|"
    r"walmart|bank\s+of\s+america|netflix|"
    r"company|corporation|business|segment|subsidiary|"
    r"risk\s*factor|md&a|management|ceo|cfo|board|"
    r"invest|analyst|portfolio|fund|bond|"
    r"tax|depreciation|amortization|goodwill|impairment|"
    r"operating|capital|capex|free\s*cash|"
    r"sales|cost|gross|net\s+(?:income|sales|revenue|loss|profit)"
    r")(?:'s|s)?\b",
    re.IGNORECASE,
)

# ── Offensive content filter ──────────────────────────────────────────────────
_OFFENSIVE_RE = re.compile(
    r"\b("
    r"fuck|shit|bitch|bastard|cunt|dick|cock|pussy|"
    r"nigger|faggot|retard|slut|whore|"
    r"kill\s+(?:you|me|them|him|her|people)|murder|bomb\s+(?:threat|attack)|terror(?:ist|ism)|"
    r"porn|sex(?:ual\s+content)?|nude|nsfw"
    r")\b",
    re.IGNORECASE,
)

# ── Ticker alias map ──────────────────────────────────────────────────────────
# Maps question keywords → TICKER SYMBOL (the canonical identifier stored in
# ChromaDB metadata under the "ticker" field).
# Add a new entry here whenever a new company is ingested into the corpus.
_TICKER_ALIASES: dict[str, list[str]] = {
    "AAPL": ["apple", "aapl", "iphone", "ipad", "airpods", "imac", "macbook", "ios", "macos", "siri"],
    "MSFT": ["microsoft", "msft", "azure", "windows", "office", "xbox", "teams", "bing", "copilot"],
    "AMZN": ["amazon", "amzn", "aws", "alexa", "kindle", "prime", "whole foods"],
    "GOOGL": ["google", "alphabet", "googl", "youtube", "android", "waymo", "chrome", "gemini"],
    "META":  ["meta", "facebook", "instagram", "whatsapp", "oculus", "reels", "threads"],
    "NVDA":  ["nvidia", "nvda", "cuda", "geforce", "quadro", "jetson"],
    "TSLA":  ["tesla", "tsla", "powerwall", "megapack"],
    "JPM":   ["jpmorgan", "jp morgan", "jpm", "chase"],
    "NFLX":  ["netflix", "nflx"],
    "AMGN":  ["amgen", "amgn"],
    "BAC":   ["bank of america", "bofa", "bac", "merrill lynch", "merrill"],
    "WMT":   ["walmart", "wmt", "wal-mart", "sam's club", "sams club"],
}

_TOPIC_REJECTED_MSG = (
    "RAGixAI answers questions about SEC EDGAR financial filings only. "
    "Please ask about revenue, earnings, risk factors, 10-K filings, "
    "or other financial metrics from public company reports."
)
_OFFENSIVE_REJECTED_MSG = (
    "This question contains inappropriate content and cannot be processed."
)


@dataclass
class GuardResult:
    allowed: bool
    reason: str  # empty when allowed=True


def check_input(question: str) -> GuardResult:
    """Validate question topic and content. Does NOT check ticker scope."""
    q = question.strip()

    if not q:
        return GuardResult(False, "Question is empty.")
    if len(q) > 2000:
        return GuardResult(False, "Question exceeds the 2000 character limit.")
    if _OFFENSIVE_RE.search(q):
        return GuardResult(False, _OFFENSIVE_REJECTED_MSG)
    if not _FINANCE_RE.search(q):
        return GuardResult(False, _TOPIC_REJECTED_MSG)

    return GuardResult(True, "")


def detect_mentioned_tickers(question: str) -> set[str]:
    """
    Return the set of ticker symbols mentioned (directly or via keywords)
    in the question. Handles possessives: 'Microsofts', "Microsoft's", 'MSFT'.

    Returns empty set if no known company is detected — do not block in that case;
    let the retriever and LLM handle it.
    """
    q = question.lower()
    found: set[str] = set()
    for ticker, aliases in _TICKER_ALIASES.items():
        for alias in aliases:
            # Allow trailing possessive: "Microsofts", "Microsoft's", "Microsoft"
            pattern = r"\b" + re.escape(alias) + r"(?:'s|s)?\b"
            if re.search(pattern, q, re.IGNORECASE):
                found.add(ticker)
                break
    return found


def check_ticker_scope(question: str, allowed_tickers: list[str]) -> GuardResult:
    """
    For scoped-analyst keys: verify the question only asks about tickers the
    user is permitted to access.

    If the question mentions no known company, let it through — the retriever's
    ticker filter will naturally limit results to allowed companies.
    """
    mentioned = detect_mentioned_tickers(question)
    if not mentioned:
        return GuardResult(True, "")

    disallowed = [t for t in mentioned if t not in allowed_tickers]
    if disallowed:
        allowed_str = " and ".join(allowed_tickers)
        disallowed_str = ", ".join(disallowed)
        return GuardResult(
            False,
            f"Access denied: you don't have permission to query documents for "
            f"{disallowed_str}. Your access is restricted to {allowed_str}.",
        )

    return GuardResult(True, "")
