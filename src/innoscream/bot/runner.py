"""Bot runner."""

from aiogram import Bot, Dispatcher
from .handlers import router
from ..core.config import get_settings

bot: Bot | None = None
dp: Dispatcher | None = None


def init_bot():
    """Initialize bot."""
    global bot, dp
    settings = get_settings()
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)


async def start_bot() -> None:
    """Launch aiogram polling loop (non‑blocking if awaited in a task)."""
    if bot is None or dp is None:
        init_bot()
    await dp.start_polling(bot)
