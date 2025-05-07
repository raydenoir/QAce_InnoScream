"""ImgFlip meme generator module."""
import random
import logging
import httpx
from typing import Optional, Tuple, Dict
from ..core.config import get_settings

logger = logging.getLogger(__name__)

IMGFLIP_API_URL = "https://api.imgflip.com/caption_image"

_TWO_TEXT_MEME_TEMPLATES = [
    "181913649",  # Drake Hotline Bling
    "112126428",  # Distracted Boyfriend
    "87743020",   # Two Buttons
    "188390779",  # Woman Yelling At Cat
    "247375501",  # Buff Doge vs. Cheems
    "99683372",   # Sleeping Shaq
]

_SINGLE_TEXT_MEME_TEMPLATES = [
    "61579",      # One Does Not Simply
    "101470",     # Man Explaining
    "4087833",    # Waiting Sceleton
    "5496396",    # Leonardo Dicaprio Cheers
    "14371066",   # Yoda
    "142009471",  # is this butterfly
    "196652226",  # Spongebob Ight Imma Head Out
]


def _split_for_two_boxes(text: str) -> Tuple[str, str]:
    words = text.split()
    mid = len(words) // 2
    return " ".join(words[:mid]), " ".join(words[mid:])


def _prepare_for_single_box(text: str, template_id: str) -> Dict[str, str]:
    target_box = "text0"
    if template_id in ["5496396", "101470", "4087833"]:
        target_box = "text1"

    if target_box == "text1":
        return {"text0": "", "text1": text}
    return {"text0": text, "text1": ""}


async def _choose_template(
    text: str,
    template_id: Optional[str] = None
):
    words = text.split()
    use_single_text_template = len(words) < 4

    chosen_template_id: str
    text_payload_params: Dict[str, str]

    if template_id:
        chosen_template_id = template_id
        if chosen_template_id in _SINGLE_TEXT_MEME_TEMPLATES:
            text_payload_params = _prepare_for_single_box(
                text,
                chosen_template_id
            )
        elif chosen_template_id in _TWO_TEXT_MEME_TEMPLATES:
            top, bottom = _split_for_two_boxes(text)
            text_payload_params = {"text0": top, "text1": bottom}
        else:
            top, bottom = _split_for_two_boxes(text)
            if len(words) < 4:
                text_payload_params = {"text0": "", "text1": text}
            else:
                text_payload_params = {"text0": top, "text1": bottom}

    elif use_single_text_template:
        if not _SINGLE_TEXT_MEME_TEMPLATES:
            return None
        chosen_template_id = random.choice(_SINGLE_TEXT_MEME_TEMPLATES)
        text_payload_params = _prepare_for_single_box(text, chosen_template_id)
    else:
        if not _TWO_TEXT_MEME_TEMPLATES:
            return None
        chosen_template_id = random.choice(_TWO_TEXT_MEME_TEMPLATES)
        top, bottom = _split_for_two_boxes(text)
        text_payload_params = {"text0": top, "text1": bottom}

    return chosen_template_id, text_payload_params


def _get_imgflip_credentials():
    return get_settings().imgflip_user, get_settings().imgflip_pass


async def generate_meme(
    text: str,
    template_id: Optional[str] = None
) -> Optional[str]:
    """Generate IMGFLIP meme."""
    _USERNAME, _PASSWORD = _get_imgflip_credentials()

    if not _USERNAME or not _PASSWORD:
        logger.error("IMGFLIP credentials not configured!")
        return None  # Early return if no credentials

    try:
        template_data = await _choose_template(text, template_id)
        if not template_data:
            logger.error("No valid template selected")
            return None
            
        chosen_template_id, text_payload_params = template_data

        payload = {
            "template_id": chosen_template_id,
            "username": _USERNAME,
            "password": _PASSWORD,
            **text_payload_params
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(IMGFLIP_API_URL, data=payload)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("success"):
                logger.error(f"ImgFlip API error: {data.get('error_message', 'Unknown error')}")
                return None
                
            return data["data"]["url"]

    except httpx.HTTPError as e:
        logger.error(f"HTTP error during meme generation: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        
    return None
