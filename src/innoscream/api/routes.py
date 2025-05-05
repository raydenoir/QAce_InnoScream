from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..services import scream
from ..core.config import get_settings

router = APIRouter(prefix="/api/v1", tags=["screams"])
settings = get_settings()


class ScreamIn(BaseModel):
    text: str
    user_id: int
    message_id: int
    chat_id: int


@router.post("/screams")
async def create_scream(payload: ScreamIn):
    post_id = await scream.save_scream(
        payload.user_id, payload.text, payload.message_id, payload.chat_id
    )
    return {"id": post_id, "text": payload.text}