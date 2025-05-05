import asyncio
from aiogram import Bot, Dispatcher

from ..core.config import get_settings
from .handlers import router


async def start_bot():
    settings = get_settings()
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)