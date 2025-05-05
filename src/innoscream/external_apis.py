import httpx
import os
import logging
import json
import random
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")

# --- ImgFlip Meme Generation ---
IMGFLIP_API_URL = "https://api.imgflip.com/caption_image"

MEME_TEMPLATE_IDS = [
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


def _split_text(text: str) -> Tuple[str, str]:
    """Crude way to split text into two parts for meme captions."""
    words = text.split()
    split_point = len(words) // 2
    top_text = " ".join(words[:split_point])
    bottom_text = " ".join(words[split_point:])
    if len(words) < 4:
        return "", text
    return top_text, bottom_text

async def generate_meme_from_text(
    scream_text: str,
    template_id: Optional[str] = None
) -> Optional[str]:
    """
    Generates a meme using the ImgFlip API based on input text.
    If template_id is not provided, randomly selects a suitable template
    from a predefined list.

    Args:
        scream_text: The text from the user's scream.
        template_id: Optional. A specific ImgFlip template ID to use.
                     If None, a random template from SUITABLE_MEME_TEMPLATE_IDS is chosen.

    Returns:
        The URL of the generated meme image, or None if generation failed.
    """
    if not IMGFLIP_USERNAME or not IMGFLIP_PASSWORD:
        logger.error("ImgFlip username or password not configured in environment variables.")
        return None

    if template_id is None:
        if not MEME_TEMPLATE_IDS:
            logger.error("Meme generation failed: SUITABLE_MEME_TEMPLATE_IDS list is empty.")
            return None
        try:
            selected_template_id = random.choice(MEME_TEMPLATE_IDS)
            logger.info(f"Randomly selected meme template ID: {selected_template_id}")
        except IndexError:
             logger.error("Meme generation failed: Could not select from empty SUITABLE_MEME_TEMPLATE_IDS list.")
             return None
    else:
        selected_template_id = template_id
        logger.info(f"Using specified meme template ID: {selected_template_id}")

    top_text, bottom_text = _split_text(scream_text)

    params = {
        "template_id": selected_template_id,
        "username": IMGFLIP_USERNAME,
        "password": IMGFLIP_PASSWORD,
        "text0": top_text,   # Top text
        "text1": bottom_text # Bottom text
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(IMGFLIP_API_URL, data=params)
            response.raise_for_status()

        result = response.json()

        if result.get("success"):
            meme_url = result.get("data", {}).get("url")
            if meme_url:
                logger.info(f"Successfully generated meme (Template: {selected_template_id}): {meme_url}")
                return meme_url
            else:
                logger.error(f"ImgFlip API success (Template: {selected_template_id}), but no meme URL found.")
                return None
        else:
            error_message = result.get("error_message", "Unknown ImgFlip API error")
            logger.error(f"ImgFlip API error (Template: {selected_template_id}): {error_message}")
            return None

    except httpx.RequestError as e:
        logger.error(f"HTTP request error calling ImgFlip API: {e}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP status error calling ImgFlip API: {e.response.status_code} - {e.response.text}")
        return None
    except json.JSONDecodeError as err:
        logger.error(f"Failed to decode JSON response from ImgFlip API: {err} - Response: '{response.text[:200]}...'") # Log part of response
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during meme generation (Template: {selected_template_id}): {e}")
        return None


# --- QuickChart.io Chart Generation ---
QUICKCHART_API_URL = "https://quickchart.io/chart/create"

async def generate_chart_url(
    chart_type: str,
    labels: List[str],
    data: List[int],
    dataset_label: str = "Count",
    title: Optional[str] = None
) -> Optional[str]:
    chart_config = {
        "type": chart_type,
        "data": {
            "labels": labels,
            "datasets": [{
                "label": dataset_label,
                "data": data,
                "backgroundColor": "rgba(54, 162, 235, 0.5)",
                "borderColor": "rgb(54, 162, 235)",
                "fill": False if chart_type == 'line' else True,
                "tension": 0.1 if chart_type == 'line' else 0
            }]
        },
        "options": {
            "responsive": True,
             "plugins": {
                "title": {
                    "display": bool(title),
                    "text": title if title else ""
                }
            }
        }
    }
    payload_json = {
        "backgroundColor": "white",
        "width": 500,
        "height": 300,
        "format": "png",
        "chart": chart_config
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(QUICKCHART_API_URL, json=payload_json)
            response.raise_for_status()
        result = response.json()
        if result.get("success"):
            chart_url = result.get("url")
            if chart_url:
                logger.info(f"Successfully generated chart: {chart_url}")
                return chart_url
            else:
                 logger.error("QuickChart API success, but no chart URL found in response.")
                 return None
        else:
            error_message = result.get("error", "Unknown QuickChart API error")
            logger.error(f"QuickChart API error: {error_message}")
            return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error calling QuickChart API: {e}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP status error calling QuickChart API: {e.response.status_code} - {e.response.text}")
        return None
    except json.JSONDecodeError as err:
        logger.error(f"Failed to decode JSON response from QuickChart API: {err} - Response: '{response.text[:200]}...'")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during chart generation: {e}")
        return None


if __name__ == "__main__":
    import asyncio

    async def test_apis():
        print("Testing Meme Generation (will use random template)...")
        meme_url = await generate_meme_from_text(
            "I get c for perfectly fine assignment"
        )
        if meme_url:
            print(f"Meme URL: {meme_url}")
        else:
            print("Meme generation failed.")

        print("\nTesting Chart Generation...")
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        stress_levels = [5, 8, 15, 12, 9, 3, 2]

        chart_url = await generate_chart_url(
            chart_type='line',
            labels=days,
            data=stress_levels,
            dataset_label="Screams per Day",
            title="Weekly Stress Levels"
        )
        if chart_url:
            print(f"Chart URL: {chart_url}")
        else:
            print("Chart generation failed.")

    asyncio.run(test_apis())
