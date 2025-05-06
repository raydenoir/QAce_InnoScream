"""
ImgFlip meme generator (async).
"""
import os, random, logging, httpx
from typing import Optional, Tuple, Dict
from ..core.config import get_settings

logger = logging.getLogger(__name__)

IMGFLIP_API_URL = "https://api.imgflip.com/caption_image"

_TWO_TEXT_MEME_TEMPLATES = [
    "181913649",  # Drake Hotline Bling
    "112126428",  # Distracted Boyfriend
    "87743020",   # Two Buttons
    "129242436",  # Change My Mind
    "188390779",  # Woman Yelling At Cat
    "247375501",  # Buff Doge vs. Cheems
]

_SINGLE_TEXT_MEME_TEMPLATES = [
    "61579",      # One Does Not Simply
    "438680",     # Success Kid
    "93895088",   # Thinking Bubble / Brain Cloud
    "101470",     # Ancient Aliens
    "222403160",  # Boardroom Meeting Suggestion
    "1035805",    # Sad Keanu
    "195515965",  # Surprised Pikachu
]

_USERNAME = get_settings().imgflip_user
_PASSWORD = get_settings().imgflip_pass


def _split_for_two_boxes(text: str) -> Tuple[str, str]:
    words = text.split()
    mid = len(words) // 2
    return " ".join(words[:mid]), " ".join(words[mid:])

def _prepare_for_single_box(text: str, template_id: str) -> Dict[str, str]:
    target_box = "text0"
    if template_id in ["438680", "101470"]:
        target_box = "text1"
    
    if target_box == "text1":
        return {"text0": "", "text1": text}
    return {"text0": text, "text1": ""}

async def generate_meme(text: str, template_id: Optional[str] = None) -> Optional[str]:
    if not _USERNAME or not _PASSWORD:
        logger.warning("IMGFLIP creds missing → skip meme gen")
        return None

    words = text.split()
    use_single_text_template = len(words) < 4
    
    chosen_template_id: str
    text_payload_params: Dict[str, str]

    if template_id:
        chosen_template_id = template_id
        if chosen_template_id in _SINGLE_TEXT_MEME_TEMPLATES:
            text_payload_params = _prepare_for_single_box(text, chosen_template_id)
        elif chosen_template_id in _TWO_TEXT_MEME_TEMPLATES:
            top, bottom = _split_for_two_boxes(text)
            text_payload_params = {"text0": top, "text1": bottom}
        else:
            top, bottom = _split_for_two_boxes(text)
            if len(words) < 4 :
                 text_payload_params = {"text0": "", "text1": text}
            else:
                 text_payload_params = {"text0": top, "text1": bottom}

    elif use_single_text_template:
        if not _SINGLE_TEXT_MEME_TEMPLATES: return None
        chosen_template_id = random.choice(_SINGLE_TEXT_MEME_TEMPLATES)
        text_payload_params = _prepare_for_single_box(text, chosen_template_id)
    else:
        if not _TWO_TEXT_MEME_TEMPLATES: return None
        chosen_template_id = random.choice(_TWO_TEXT_MEME_TEMPLATES)
        top, bottom = _split_for_two_boxes(text)
        text_payload_params = {"text0": top, "text1": bottom}
        
    payload = dict(
        template_id=chosen_template_id,
        username=_USERNAME,
        password=_PASSWORD,
        **text_payload_params
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
