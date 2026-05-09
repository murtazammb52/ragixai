from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from backend.models.schemas import (
    JudgeAggregateResult,
    JudgeRequest,
    JudgeResult,
    SingleRowJudgeRequest,
)
from backend.models.auth import UserContext, require_user

router = APIRouter()


@router.post("/judge", response_model=JudgeAggregateResult)
def run_judge(
    req: JudgeRequest,
    ctx: UserContext = Depends(require_user("admin")),
) -> JudgeAggregateResult:
    """Run LLM-as-judge evaluation for a config over the financebench dataset."""
    try:
        from backend.evaluation.llm_judge import run_judge_evaluation
        return run_judge_evaluation(
            config=req.config,
            dataset=req.dataset,
            sample_size=req.sample_size,
        )
    except Exception as e:
        logger.error(f"Judge evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/judge/row", response_model=JudgeResult)
def judge_single_row(
    req: SingleRowJudgeRequest,
    ctx: UserContext = Depends(require_user("analyst")),
) -> JudgeResult:
    """Judge a single QA row — useful for spot-checking any generated answer."""
    try:
        from backend.evaluation.llm_judge import judge_row
        return judge_row(
            question=req.question,
            answer=req.answer,
            contexts=req.contexts,
            ground_truth=req.ground_truth,
            config=req.config,
            company=req.company,
        )
    except Exception as e:
        logger.error(f"Single-row judge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
