import aiosqlite
import pathlib
from contextlib import asynccontextmanager

from .schema import SCHEMA_DDL

_DB_PATH = pathlib.Path("data") / "screams.db"
_DB_PATH.parent.mkdir(exist_ok=True)


async def init_db() -> None:
    async with aiosqlite.connect(_DB_PATH) as db:
        await db.executescript(SCHEMA_DDL)
        await db.commit()


@asynccontextmanager
async def get_db():
    db = await aiosqlite.connect(_DB_PATH)
    await db.execute("PRAGMA journal_mode=WAL;")
    try:
        yield db
    finally:
        await db.close()