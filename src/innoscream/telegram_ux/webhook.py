from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from .handlers import register_handlers
import logging
import ssl

async def on_startup(dp: Dispatcher):
    """Actions on bot startup"""
    logging.warning('Starting InnoScream bot...')
    await dp.bot.set_webhook(WEBHOOK_URL, certificate=open(WEBHOOK_SSL_CERT, 'rb'))

async def on_shutdown(dp: Dispatcher):
    """Actions on bot shutdown"""
    logging.warning('Shutting down InnoScream bot...')
    await dp.bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()

def setup_bot(token: str, webhook_url: str = None, ssl_cert: str = None):
    """Initialize bot with webhook or polling"""
    bot = Bot(token=token)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    
    register_handlers(dp)
    
    if webhook_url:
        global WEBHOOK_URL, WEBHOOK_SSL_CERT
        WEBHOOK_URL = webhook_url
        WEBHOOK_SSL_CERT = ssl_cert
        
        from aiogram import executor
        executor.start_webhook(
            dispatcher=dp,
            webhook_path='',
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host='0.0.0.0',
            port=8443,
            ssl_context=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))
    else:
        from aiogram import executor
        executor.start_polling(dp, skip_updates=True)