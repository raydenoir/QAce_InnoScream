from fastapi import APIRouter, HTTPException
from datetime import date
from ..db import scream_repo as repo

router = APIRouter(prefix="/api/v1", tags=["screams"])


@router.get("/top/{day}")
async def top(day: date):
    item = await repo.top_daily(day)
    if not item:
        raise HTTPException(404, "no screams that day")
    return item
