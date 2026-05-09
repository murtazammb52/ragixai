import uuid
from fastapi import APIRouter, BackgroundTasks, Depends
from loguru import logger

from backend.models.schemas import IngestRequest, IngestStatusResponse
from backend.models.auth import UserContext, require_user

router = APIRouter()

_jobs: dict[str, dict] = {}


def _run_ingest(job_id: str, companies: list[str] | None, max_filings: int, years: list[int] | None):
    from backend.pipeline.ingest import ingest_from_huggingface
    from backend.pipeline.chunker import chunk_all_docs
    from backend.pipeline.indexer import build_index

    _jobs[job_id]["status"] = "running"
    _jobs[job_id]["message"] = "Starting ingestion..."

    def progress(pct, msg):
        _jobs[job_id]["progress"] = pct
        _jobs[job_id]["message"] = msg

    try:
        docs = ingest_from_huggingface(companies=companies, max_filings=max_filings, years=years, progress_callback=progress)
        _jobs[job_id]["docs_ingested"] = len(docs)
        _jobs[job_id]["message"] = f"Ingested {len(docs)} docs — chunking..."
        _jobs[job_id]["progress"] = 0.5

        chunk_all_docs(progress_callback=progress)
        _jobs[job_id]["message"] = "Chunks ready — building index..."
        _jobs[job_id]["progress"] = 0.75

        n = build_index()
        _jobs[job_id]["status"] = "completed"
        _jobs[job_id]["progress"] = 1.0
        _jobs[job_id]["message"] = f"Done — {n} chunks indexed"
        logger.info(f"Ingest job {job_id} complete")
    except Exception as e:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["message"] = str(e)
        logger.error(f"Ingest job {job_id} failed: {e}")


@router.post("/ingest")
def trigger_ingest(
    req: IngestRequest,
    background_tasks: BackgroundTasks,
    ctx: UserContext = Depends(require_user("admin")),
):
    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {"status": "running", "progress": 0.0, "message": "Queued", "docs_ingested": 0}
    background_tasks.add_task(
        _run_ingest, job_id, req.companies, req.max_filings, req.years
    )
    return {"status": "started", "job_id": job_id}


@router.get("/ingest/status/{job_id}", response_model=IngestStatusResponse)
def ingest_status(job_id: str, ctx: UserContext = Depends(require_user("admin"))):
    job = _jobs.get(job_id, {"status": "not_found", "progress": 0, "message": "Job not found", "docs_ingested": 0})
    return IngestStatusResponse(job_id=job_id, **job)
