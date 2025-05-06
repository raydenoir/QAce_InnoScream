"""
ImgFlip meme generator (async).
"""
import os, random, logging, httpx
from typing import Optional, Tuple
from ..core.config import get_settings

logger = logging.getLogger(__name__)

IMGFLIP_API_URL = "https://api.imgflip.com/caption_image"

_MEME_TEMPLATES = [
    "181913649",  # Drake Hotline Bling
    "112126428",  # Distracted Boyfriend
    "87743020",   # Two Buttons
    "129242436",  # Change My Mind
    "188390779",  # Woman Yelling At Cat
    "61579",      # One Does Not Simply
    "247375501",  # Buff Doge vs. Cheems
    "438680",     # Success Kid
    "93895088",   # Thinking Bubble / Brain Cloud
    "101470",     # Ancient Aliens
]

_USERNAME = get_settings().imgflip_user
_PASSWORD = get_settings().imgflip_pass


def _split(text: str) -> Tuple[str, str]:
    words = text.split()
    if len(words) < 4:
        return "", text
    mid = len(words) // 2
    return " ".join(words[:mid]), " ".join(words[mid:])


async def generate_meme(text: str, template_id: Optional[str] = None) -> Optional[str]:
    if not _USERNAME or not _PASSWORD:
        logger.warning("IMGFLIP creds missing → skip meme gen")
        return None

    template = template_id or random.choice(_MEME_TEMPLATES)
    top, bottom = _split(text)
    payload = dict(
        template_id=template,
        username=_USERNAME,
        password=_PASSWORD,
        text0=top,
        text1=bottom,
    )

    try:
        async with httpx.AsyncClient() as c:
            r = await c.post(IMGFLIP_API_URL, data=payload)
            r.raise_for_status()
        data = r.json()
        return data["data"]["url"] if data.get("success") else None
    except Exception as ex:
        logger.error("meme gen failed: %s", ex)
        return None
