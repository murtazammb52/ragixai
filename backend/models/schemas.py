from typing import Optional
from pydantic import BaseModel


class Citation(BaseModel):
    chunk_id: str
    text: str
    doc_id: str
    company: str
    year: int
    section: str
    score: float


class ChatRequest(BaseModel):
    question: str
    config: str = "config_d"
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    config_used: str
    latency_ms: float
    retrieved_count: int
    reranked_count: int


class IngestRequest(BaseModel):
    companies: Optional[list[str]] = None
    max_filings: int = 3
    years: Optional[list[int]] = None


class IngestStatusResponse(BaseModel):
    job_id: str
    status: str  # "running" | "completed" | "failed"
    progress: float
    message: str
    docs_ingested: int


class EvalRequest(BaseModel):
    dataset: str = "financebench"  # "financebench" | "ragas_testset"
    config: str = "config_d"
    sample_size: int = 50


class EvalResult(BaseModel):
    config: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float
    answer_correctness: float
    response_latency_p95_ms: float
    sample_size: int


class ABTestRequest(BaseModel):
    configs: Optional[list[str]] = None  # None means all 7
    dataset: str = "financebench"
    sample_size: int = 20
    run_judge: bool = False  # opt-in: also run LLM-as-Judge alongside RAGAS


class ABTestResponse(BaseModel):
    results: list[EvalResult]
    winner: str
    comparison_table: list[dict]


# ── LLM-as-Judge schemas ───────────────────────────────────────────────────

class DimensionScore(BaseModel):
    score_raw: int    # 1–5 as returned by the LLM
    score_norm: float  # score_raw / 5.0, range [0.0, 1.0]
    passed: bool      # score_norm >= 0.70
    reasoning: str    # one-sentence LLM explanation


class JudgeResult(BaseModel):
    question: str
    config: str
    company: str
    faithfulness: DimensionScore
    completeness: DimensionScore
    citation_quality: DimensionScore
    hallucination_free: DimensionScore
    overall_score: float  # mean of the four score_norms
    passed: bool          # True only if ALL four dimensions passed
    judge_model: str
    fallback_used: bool   # True when heuristic fallback was used


class JudgeAggregateResult(BaseModel):
    config: str
    faithfulness_mean: float
    completeness_mean: float
    citation_quality_mean: float
    hallucination_free_mean: float
    overall_mean: float
    pass_rate: float    # fraction of rows where passed=True
    sample_size: int
    fallback_count: int  # rows that used heuristic fallback


class JudgeRequest(BaseModel):
    dataset: str = "financebench"
    config: str = "config_d"
    sample_size: int = 20


class SingleRowJudgeRequest(BaseModel):
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    config: str = "manual"
    company: str = ""


class HealthResponse(BaseModel):
    status: str
    chroma_docs: int
    embedding_model: str
    llm_model: str
    bm25_index_size: int
