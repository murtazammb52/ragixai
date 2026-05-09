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


class ABTestResponse(BaseModel):
    results: list[EvalResult]
    winner: str
    comparison_table: list[dict]


class HealthResponse(BaseModel):
    status: str
    chroma_docs: int
    embedding_model: str
    llm_model: str
    bm25_index_size: int
