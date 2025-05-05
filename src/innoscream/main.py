import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from telegram_ux import TelegramUX, CoreBackendImplementation

load_dotenv()

async def main():
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher()
    
    backend = CoreBackendImplementation()
    ux = TelegramUX(backend)
    ux.register_handlers(dp)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())