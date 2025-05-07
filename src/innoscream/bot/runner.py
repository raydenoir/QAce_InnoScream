from aiogram import Bot, Dispatcher
from ..core.config import get_settings
from .handlers import router

# -- create singleton objects at import time -------------------
settings = get_settings()
bot = Bot(token=settings.bot_token)
dp = Dispatcher()
dp.include_router(router)
# --------------------------------------------------------------


async def start_bot() -> None:
    """Launch aiogram polling loop (non‑blocking if awaited in a task)."""
    await dp.start_polling(bot)
