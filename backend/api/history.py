from typing import Optional
from fastapi import APIRouter, Depends, Query
from backend.models.auth import UserContext, require_user
from backend.models.history import get_history

router = APIRouter()


@router.get("/history")
def history(
    limit: int = Query(200, ge=1, le=1000),
    config: Optional[str] = None,
    search: Optional[str] = None,
    ctx: UserContext = Depends(require_user("viewer")),
):
    return get_history(limit=limit, config=config, search=search)
