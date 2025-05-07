"""Data Access Object (DAO) module."""
import aiosqlite
import pathlib
from contextlib import asynccontextmanager

from .schema import SCHEMA_DDL

_DB_PATH = pathlib.Path("data") / "screams.db"
_DB_PATH.parent.mkdir(exist_ok=True)


async def init_db() -> None:
    """Initialize the database with required schema.

    Creates the database file if it doesn't exist
    and executes the DDL schema script.
    """
    async with aiosqlite.connect(_DB_PATH) as db:
        await db.executescript(SCHEMA_DDL)
        await db.commit()


@asynccontextmanager
async def get_db():
    """Async context manager for database connections.

    Provides database connections with automatic cleanup,
    and configures SQLite to use Write-Ahead Logging (WAL) mode.

    Yields:
        aiosqlite.Connection: active database connection
    """
    db = await aiosqlite.connect(_DB_PATH)
    await db.execute("PRAGMA journal_mode=WAL;")
    try:
        yield db
    finally:
        await db.close()
