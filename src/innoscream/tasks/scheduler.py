"""Scheduler module."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date, timedelta
from ..services import scream, meme, analytics
from ..core.config import get_settings
from ..bot.runner import bot


async def post_daily_top():
    """Daily top poster.

    Post daily top scream and a generated meme to configured channel,
    or a text-only fallback if meme generation fails.
    """
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


async def post_weekly_stress_graph():
    """Posts the weekly stress graph to the main channel."""
    today = date.today()
    # Calculate the Monday of the *previous* week
    previous_monday = today - timedelta(days=today.weekday() + 7)
    
    labels, data = await scream.weekly_labels_counts(previous_monday)
    
    chart_image_url = await analytics.chart_url(labels, data)

    if chart_image_url:
        total_screams_this_week = sum(data)
        # Ensure divisor is not zero if no screams
        avg_screams_per_day = total_screams_this_week / 7.0 if total_screams_this_week > 0 else 0.0
        
        previous_sunday = previous_monday + timedelta(days=6)

        caption_parts = [
            f"📊 Weekly Stress Report ({previous_monday:%d %b} - {previous_sunday:%d %b %Y}) 📊",
            "",
            "Screams per day:"
        ]
        for day_label, count in zip(labels, data):
            caption_parts.append(f"  {day_label}: {count}")
        caption_parts.append("")
        caption_parts.append(f"Total this week: {total_screams_this_week}")
        caption_parts.append(f"Weekly Average: {avg_screams_per_day:.1f} screams/day")
        
        final_caption = "\n".join(caption_parts)
        
        await bot.send_photo(
            chat_id=get_settings().channel_id,
            photo=chart_image_url,
            caption=final_caption
        )


scheduler = AsyncIOScheduler()


def start_scheduler():
    """Initialize and configure the automated posting scheduler."""
    # daily at 00:05
    scheduler.add_job(
        post_daily_top,
        "cron",
        hour=0,
        minute=5,
        misfire_grace_time=3600
    )
    scheduler.add_job(
        post_weekly_stress_graph,
        "cron",
        day_of_week="mon",
        hour=0,      
        minute=15,
        misfire_grace_time=3600
    )
    
    scheduler.start()
