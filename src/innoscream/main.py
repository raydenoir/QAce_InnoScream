import asyncio
import uvicorn
from fastapi import FastAPI

from .api.routes import router as api_router
from .bot.runner import start_bot
from .db.dao import init_db

app = FastAPI(title="InnoScream")
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    await init_db()
    asyncio.create_task(start_bot())