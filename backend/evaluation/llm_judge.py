"""
LLM-as-Judge evaluation module for RAGixAI.

Scores individual QA rows on 4 financial-RAG-specific dimensions using the
local Ollama model at temperature=0. Falls back to word-overlap heuristics
if Ollama is unavailable or returns malformed JSON.

Dimensions (all scored 1–5, normalised to 0–1):
  - faithfulness        : every claim traceable to retrieved contexts
  - completeness        : all question parts addressed
  - citation_quality    : [N] markers correctly placed next to facts
  - hallucination_free  : no external knowledge beyond retrieved contexts

Pass threshold: score_norm >= 0.70 (i.e., raw score >= 4 out of 5)
"""
from __future__ import annotations

import json
import re

import numpy as np
from loguru import logger
from tqdm import tqdm

from backend.config import settings
from backend.models.schemas import (
    DimensionScore,
    JudgeAggregateResult,
    JudgeResult,
)

PASS_THRESHOLD: float = 0.7
_SCORE_SCALE: int = 5

JUDGE_PROMPT = """\
You are an expert financial RAG evaluator. Your job is to assess the quality \
of a generated answer using ONLY the provided information.

**Question:**
{question}

**Ground Truth Answer:**
{ground_truth}

**Generated Answer:**
{answer}

**Retrieved Contexts (numbered):**
{contexts}

Score the Generated Answer on exactly 4 dimensions. Each score must be an \
INTEGER from 1 to 5.

Dimension definitions:
1. faithfulness — every factual claim in the answer must be directly traceable \
to one of the retrieved contexts (1=fabricates facts, 5=fully grounded)
2. completeness — answer fully addresses all parts of the question given \
available contexts (1=major gaps, 5=thorough)
3. citation_quality — [N] citation markers placed immediately next to the \
specific facts they support (1=none/misplaced, 5=all correct)
4. hallucination_free — answer avoids introducing any knowledge not present in \
retrieved contexts (1=adds external data, 5=purely corpus-grounded)

Return ONLY valid JSON, no other text before or after:
{{
  "faithfulness": {{"score": <1-5>, "reasoning": "<one sentence>"}},
  "completeness": {{"score": <1-5>, "reasoning": "<one sentence>"}},
  "citation_quality": {{"score": <1-5>, "reasoning": "<one sentence>"}},
  "hallucination_free": {{"score": <1-5>, "reasoning": "<one sentence>"}}
}}"""

_DIMENSIONS = ["faithfulness", "completeness", "citation_quality", "hallucination_free"]


# ── Public API ────────────────────────────────────────────────────────────────

def judge_row(
    question: str,
    answer: str,
    contexts: list[str],
    ground_truth: str,
    config: str = "unknown",
    company: str = "",
) -> JudgeResult:
    """
    Judge a single QA row. Calls Ollama at temperature=0.
    Falls back to heuristic scores if the LLM is unavailable or returns
    malformed JSON. Always returns a valid JudgeResult.
    """
    context_block = "\n\n".join(
        f"[{i + 1}] {ctx[:600]}" for i, ctx in enumerate(contexts)
    )
    prompt = JUDGE_PROMPT.format(
        question=question,
        ground_truth=ground_truth,
        answer=answer,
        contexts=context_block,
    )

    fallback_used = False
    parsed: dict | None = None
    try:
        raw = _call_ollama_judge(prompt)
        parsed = _parse_judge_response(raw)
    except Exception as e:
        logger.warning(f"LLM judge call failed: {e}")

    if parsed is None:
        fallback_used = True
        scores, reasonings = _heuristic_judge(question, answer, contexts, ground_truth)
        parsed = {
            dim: {"score": scores[dim], "reasoning": reasonings[dim]}
            for dim in _DIMENSIONS
        }

    dim_scores = {
        dim: _build_dimension_score(parsed[dim]["score"], parsed[dim]["reasoning"])
        for dim in _DIMENSIONS
    }

    overall = round(sum(d.score_norm for d in dim_scores.values()) / 4, 4)

    return JudgeResult(
        question=question,
        config=config,
        company=company,
        faithfulness=dim_scores["faithfulness"],
        completeness=dim_scores["completeness"],
        citation_quality=dim_scores["citation_quality"],
        hallucination_free=dim_scores["hallucination_free"],
        overall_score=overall,
        passed=all(d.passed for d in dim_scores.values()),
        judge_model=settings.ollama_model,
        fallback_used=fallback_used,
    )


def run_judge_evaluation(
    config: str = "config_d",
    dataset: str = "financebench",
    sample_size: int = 20,
) -> JudgeAggregateResult:
    """
    Run LLM-as-judge over a full dataset for one config.
    Reuses CONFIG_MODES and _load_dataset from ragas_eval to stay in sync.
    """
    from backend.evaluation.ragas_eval import CONFIG_MODES, _load_dataset
    from backend.pipeline.generator import generate_answer
    from backend.pipeline.reranker import rerank
    from backend.pipeline.retriever import retrieve

    cfg = CONFIG_MODES.get(config.lower(), CONFIG_MODES["config_d"])
    qa_pairs = _load_dataset(dataset, sample_size)

    row_results: list[JudgeResult] = []
    for qa in tqdm(qa_pairs, desc=f"LLM Judge [{config}]"):
        try:
            candidates = retrieve(qa.question, mode=cfg["mode"])
            if cfg["use_reranker"] and candidates:
                candidates = rerank(qa.question, candidates)
            gen = generate_answer(qa.question, candidates)
        except Exception as e:
            logger.warning(f"Pipeline error for '{qa.question[:60]}': {e}")
            continue

        contexts = [c.text for c in gen.citations] or ["No context retrieved."]
        result = judge_row(
            question=qa.question,
            answer=gen.answer,
            contexts=contexts,
            ground_truth=qa.ground_truth,
            config=config,
            company=qa.company,
        )
        row_results.append(result)

    n = len(row_results)
    fallback_count = sum(1 for r in row_results if r.fallback_used)

    def _mean(attr: str) -> float:
        vals = [getattr(r, attr).score_norm for r in row_results]
        return round(float(np.mean(vals)), 4) if vals else 0.0

    overall_vals = [r.overall_score for r in row_results]
    return JudgeAggregateResult(
        config=config,
        faithfulness_mean=_mean("faithfulness"),
        completeness_mean=_mean("completeness"),
        citation_quality_mean=_mean("citation_quality"),
        hallucination_free_mean=_mean("hallucination_free"),
        overall_mean=round(float(np.mean(overall_vals)), 4) if overall_vals else 0.0,
        pass_rate=round(sum(1 for r in row_results if r.passed) / n, 4) if n > 0 else 0.0,
        sample_size=n,
        fallback_count=fallback_count,
    )


# ── Internal helpers ──────────────────────────────────────────────────────────

def _call_ollama_judge(prompt: str) -> str:
    import ollama
    response = ollama.generate(
        model=settings.ollama_model,
        prompt=prompt,
        options={"temperature": 0, "num_predict": 600},
    )
    return response["response"].strip()


def _parse_judge_response(raw: str) -> dict | None:
    """
    Extract and validate JSON from the LLM response.
    Handles markdown fences and preamble text. Returns None on any failure.
    """
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group())
    except json.JSONDecodeError:
        return None

    for dim in _DIMENSIONS:
        if dim not in parsed:
            return None
        entry = parsed[dim]
        if not isinstance(entry, dict) or "score" not in entry:
            return None
        score = entry["score"]
        if not isinstance(score, int) or score < 1 or score > 5:
            return None

    return parsed


def _build_dimension_score(raw_score: int, reasoning: str) -> DimensionScore:
    norm = round(raw_score / _SCORE_SCALE, 4)
    return DimensionScore(
        score_raw=raw_score,
        score_norm=norm,
        passed=norm >= PASS_THRESHOLD,
        reasoning=reasoning,
    )


def _heuristic_judge(
    question: str,
    answer: str,
    contexts: list[str],
    ground_truth: str,
) -> tuple[dict[str, int], dict[str, str]]:
    """Word-overlap heuristics for when the LLM is unavailable."""
    def tokenize(text: str) -> set[str]:
        return set(re.findall(r"\b\w+\b", text.lower()))

    answer_tokens = tokenize(answer)
    context_tokens = tokenize(" ".join(contexts))
    question_tokens = tokenize(question)

    def overlap_score(a: set[str], b: set[str]) -> float:
        return len(a & b) / len(a) if a else 0.0

    def to_bin(ratio: float) -> int:
        if ratio < 0.10:
            return 1
        if ratio < 0.30:
            return 2
        if ratio < 0.50:
            return 3
        if ratio < 0.70:
            return 4
        return 5

    citation_count = len(re.findall(r"\[\d+\]", answer))
    citation_score = min(citation_count + 1, 5)

    scores = {
        "faithfulness":      to_bin(overlap_score(answer_tokens, context_tokens)),
        "completeness":      to_bin(overlap_score(question_tokens, answer_tokens)),
        "citation_quality":  citation_score,
        "hallucination_free": to_bin(overlap_score(answer_tokens, context_tokens)),
    }
    reason = "Heuristic fallback (LLM unavailable)"
    reasonings = {dim: reason for dim in _DIMENSIONS}
    return scores, reasonings
