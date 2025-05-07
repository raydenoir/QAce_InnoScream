from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date, timedelta
from ..services import scream, meme
from ..core.config import get_settings
from ..bot.runner import bot


async def post_daily_top():
    """Posts daily top scream and a generated meme to configured channel,
    or a text-only fallback if meme generation fails."""
    yesterday = date.today() - timedelta(days=1)
    top = await scream.get_top_daily(yesterday)
    if not top:
        return
    meme_url = await meme.generate_meme(top["text"])

    caption = f"🏆 Top scream for {yesterday:%d %b} with {top['votes']} votes"

    if meme_url:
        await bot.send_photo(
            get_settings().channel_id,
            meme_url,
            caption=caption
        )
    else:
        await bot.send_message(
            get_settings().channel_id,
            f"{caption}\n\n{top['text']}"
        )

scheduler = AsyncIOScheduler()


def start_scheduler():
    """Initializes and configures the automated posting scheduler."""
    # daily at 00:05
    scheduler.add_job(
        post_daily_top,
        "cron",
        hour=0,
        minute=5,
        misfire_grace_time=3600
    )
    scheduler.start()
