from fastapi import APIRouter
from pydantic import BaseModel

from ..services import scream
from ..core.config import get_settings

router = APIRouter(prefix="/api/v1", tags=["screams"])
settings = get_settings()


class ScreamIn(BaseModel):
    """Model for creating a new scream post.

        Attributes:
            text: content text of the scream.
            user_id: unique identifier of the user creating the post.
            message_id: unique identifier of the associated message.
            chat_id: unique identifier of the chat context where the scream was posted.
    """
    text: str
    user_id: int
    message_id: int
    chat_id: int


@router.post("/screams")
async def create_scream(payload: ScreamIn):
    """Creates and saves a new scream post in the system.

        Arguments:
            payload: ScreamIn model containing post content and associated identifiers.
    """
    post_id = await scream.save_scream(
        payload.user_id, payload.text, payload.message_id, payload.chat_id
    )
    return {"id": post_id, "text": payload.text}
