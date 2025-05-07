"""Bot runner."""

from aiogram import Bot, Dispatcher
from .handlers import router
from ..core.config import get_settings

_bot: Bot | None = None
_dp: Dispatcher | None = None


def get_bot() -> Bot:
    """Return singleton Bot, create on first call."""
    global _bot, _dp
    if _bot is None:
        settings = get_settings()
        _bot = Bot(token=settings.bot_token)
        _dp = Dispatcher()
        _dp.include_router(router)
    return _bot


async def start_bot() -> None:
    """Launch polling loop once."""
    bot = get_bot()
    await _dp.start_polling(bot)
