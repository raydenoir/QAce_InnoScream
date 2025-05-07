"""Application entrypoint."""

import asyncio
from fastapi import FastAPI

from .api.routes import router as api_router
from .bot.runner import start_bot
from .db.dao import init_db
from .tasks.scheduler import start_scheduler

app = FastAPI(title="InnoScream")
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Init on FastAPI startup."""
    await init_db()
    asyncio.create_task(start_bot())
    start_scheduler()
