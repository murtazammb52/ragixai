from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from backend.models.schemas import EvalRequest, EvalResult, ABTestRequest, ABTestResponse
from backend.models.auth import UserContext, require_user

router = APIRouter()


@router.post("/evaluate", response_model=EvalResult)
def evaluate(req: EvalRequest, ctx: UserContext = Depends(require_user("admin"))):
    try:
        from backend.evaluation.ragas_eval import run_evaluation
        result = run_evaluation(config=req.config, dataset=req.dataset, sample_size=req.sample_size)
        return result
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test", response_model=ABTestResponse)
def ab_test(req: ABTestRequest, ctx: UserContext = Depends(require_user("admin"))):
    try:
        from backend.evaluation.ab_test import run_ab_test
        return run_ab_test(
            configs=req.configs,
            dataset=req.dataset,
            sample_size=req.sample_size,
            run_judge=req.run_judge,
        )
    except Exception as e:
        logger.error(f"A/B test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
