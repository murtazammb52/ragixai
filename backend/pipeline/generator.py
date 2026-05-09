"""
Answer generation via Ollama (local LLM).
Extracts [1][2][3] style citations and links them to source chunks.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from loguru import logger

from backend.config import settings
from backend.pipeline.retriever import ScoredChunk

NOT_FOUND_ANSWER = "Answer not found in Corpus"

PROMPT_TEMPLATE = """You are a financial analyst assistant. Answer questions ONLY using the SEC filing excerpts provided below.

Rules you MUST follow:
1. Cite every fact with [1], [2], etc. matching the excerpt numbers.
2. If the answer cannot be found in the excerpts below, respond EXACTLY with: Answer not found in Corpus
3. Do NOT use any knowledge from outside the provided excerpts.
4. Do NOT speculate, infer, or add information not explicitly in the excerpts.
5. If the question asks about Company X but the excerpts are from Company Y, respond EXACTLY with: Answer not found in Corpus

--- SEC Filing Excerpts ---
{context}
--- End of Excerpts ---

Question: {question}

Answer (cite sources with [N]):"""

# Patterns that indicate the LLM answered from parametric knowledge or found nothing
_NOT_FOUND_RE = re.compile(
    r"(?:I\s+(?:cannot|can'?t|could\s+not|couldn'?t)\s+find"
    r"|(?:is|are|was|were)\s+not\s+(?:mentioned|found|provided|available|stated|given|included)"
    r"|not\s+(?:found|mentioned|provided|available|stated)\s+in\s+the"
    r"|no\s+(?:information|data|details?|mention)\s+(?:is\s+)?(?:available|found|provided|present)"
    r"|(?:the\s+)?(?:provided\s+)?(?:excerpts?|filings?|context|corpus)\s+(?:do(?:es)?\s+not|don'?t)\s+(?:contain|mention|include|provide)"
    r")",
    re.IGNORECASE,
)


@dataclass
class GeneratorOutput:
    answer: str
    citations: list[ScoredChunk]
    raw_response: str


def generate_answer(question: str, contexts: list[ScoredChunk]) -> GeneratorOutput:
    """Generate a cited answer using Ollama."""
    if not contexts:
        return GeneratorOutput(
            answer=NOT_FOUND_ANSWER,
            citations=[],
            raw_response="",
        )

    context_block = "\n\n".join([
        f"[{i + 1}] (Source: {c.company} {c.year} 10-K, relevance: {c.score:.2f})\n{c.text[:800]}"
        for i, c in enumerate(contexts)
    ])

    prompt = PROMPT_TEMPLATE.format(context=context_block, question=question)

    try:
        import ollama
        response = ollama.generate(
            model=settings.ollama_model,
            prompt=prompt,
            options={"temperature": 0.1, "num_predict": 250},
        )
        raw = response["response"].strip()
    except Exception as e:
        logger.error(f"Ollama generation failed: {e}")
        raw = f"[LLM unavailable: {e}] Based on the retrieved excerpts: {contexts[0].text[:300]}..."

    raw = _normalize_not_found(raw)

    cited_indices = _extract_citation_indices(raw)
    used_chunks = [contexts[i - 1] for i in cited_indices if 1 <= i <= len(contexts)]
    if not used_chunks and raw != NOT_FOUND_ANSWER:
        used_chunks = contexts[:3]

    return GeneratorOutput(answer=raw, citations=used_chunks, raw_response=raw)


def _normalize_not_found(text: str) -> str:
    """Collapse common 'I cannot find' phrases to the canonical not-found string."""
    if len(text) < 400 and _NOT_FOUND_RE.search(text):
        return NOT_FOUND_ANSWER
    return text


def _extract_citation_indices(text: str) -> list[int]:
    matches = re.findall(r"\[(\d+)\]", text)
    seen = set()
    result = []
    for m in matches:
        idx = int(m)
        if idx not in seen:
            seen.add(idx)
            result.append(idx)
    return result
