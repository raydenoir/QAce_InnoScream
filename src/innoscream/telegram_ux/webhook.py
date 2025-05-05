from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging
import ssl
import asyncio
from .handlers import TelegramUX
from .interface import BackendInterface

async def on_startup(bot: Bot, webhook_url: str = None, ssl_cert: str = None):
    """Actions on bot startup"""
    logging.warning('Starting InnoScream bot...')
    if webhook_url:
        await bot.set_webhook(
            webhook_url,
            certificate=open(ssl_cert, 'rb') if ssl_cert else None
        )

async def on_shutdown(bot: Bot, dispatcher: Dispatcher, webhook_url: str = None):
    """Actions on bot shutdown"""
    logging.warning('Shutting down InnoScream bot...')
    if webhook_url:
        await bot.delete_webhook()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

async def start_polling(dispatcher: Dispatcher, bot: Bot):
    """Start polling mode"""
    await dispatcher.start_polling(bot)

async def start_webhook(
    dispatcher: Dispatcher,
    bot: Bot,
    webhook_url: str,
    ssl_cert: str = None
):
    """Start webhook mode"""
    await bot.set_webhook(
        webhook_url,
        certificate=open(ssl_cert, 'rb') if ssl_cert else None
    )
    # Add your webhook server setup here if needed

def setup_bot(
    token: str, 
    backend: BackendInterface, 
    admins: list[int] = None,
    webhook_url: str = None, 
    ssl_cert: str = None
):
    """Initialize bot with webhook or polling"""
    bot = Bot(token=token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Create TelegramUX instance and register handlers
    telegram_ux = TelegramUX(backend)
    telegram_ux.register_handlers(dp, admins=admins)

    if webhook_url:
        # Webhook mode
        async def webhook_main():
            await on_startup(bot, webhook_url, ssl_cert)
            try:
                await dp.start_polling(bot)
            finally:
                await on_shutdown(bot, dp, webhook_url)

        asyncio.run(webhook_main())
    else:
        # Polling mode
        async def polling_main():
            await on_startup(bot)
            try:
                await dp.start_polling(bot)
            finally:
                await on_shutdown(bot, dp)

        asyncio.run(polling_main())