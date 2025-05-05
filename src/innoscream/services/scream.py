from typing import Tuple
from ..db import dao
from ..services.security import hash_user_id
from ..core.config import get_settings

settings = get_settings()

EMOJI_TO_COLUMN = {
    "💀": "skull",
    "🔥": "fire",
    "🤡": "clown",
}


async def save_scream(user_id: int, text: str, message_id: int, chat_id: int) -> int:
    """Insert a scream and return its post_id."""
    async with dao.get_db() as db:
        hashed = hash_user_id(user_id)
        cur = await db.execute(
            """INSERT INTO posts (user_hash, text, message_id, chat_id)
               VALUES (?,?,?,?)""",
            (hashed, text, message_id, chat_id),
        )
        await db.execute(
            """INSERT INTO user_stats(user_hash, post_count)
               VALUES(?, 1)
               ON CONFLICT(user_hash) DO UPDATE SET post_count = post_count + 1""",
            (hashed,),
        )
        await db.commit()
        return cur.lastrowid


async def add_reaction(post_id: int, emoji: str) -> Tuple[int, int, int]:
    column = EMOJI_TO_COLUMN.get(emoji)
    if column is None:
        raise ValueError("Unsupported reaction")
    async with dao.get_db() as db:
        await db.execute(
            f"UPDATE posts SET {column} = {column} + 1 WHERE post_id = ?",
            (post_id,),
        )
        await db.commit()
        cur = await db.execute(
            "SELECT skull, fire, clown FROM posts WHERE post_id = ?", (post_id,)
        )
        row = await cur.fetchone()
        return row  # skull, fire, clown


async def delete_post(post_id: int, ctx):
    await ctx.bot.delete_message(chat_id=settings.channel_id, message_id=post_id)
    async with dao.get_db() as db:
        await db.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
        await db.commit()


async def get_user_stats(user_id: int) -> int:
    async with dao.get_db() as db:
        hashed = hash_user_id(user_id)
        cur = await db.execute(
            "SELECT post_count FROM user_stats WHERE user_hash = ?", (hashed,)
        )
        row = await cur.fetchone()
        return row[0] if row else 0