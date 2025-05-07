"""Scream repo module."""
from datetime import date, timedelta
from typing import Tuple, Optional
from ..db import dao
from ..services.security import hash_user_id
from ..services.analytics import weekly_counts
from ..core.config import get_settings

EMOJI_TO_COLUMN = {"💀": "skull", "🔥": "fire", "🤡": "clown"}


# ------------------------------------------------------------------ CRUD -----
async def create_post(
    user_id: int,
    text: str,
    message_id: int,
    chat_id: int
) -> int:
    """Insert a scream, update user_stats, return post_id."""
    async with dao.get_db() as db:
        h = hash_user_id(user_id)
        query = (
            "INSERT INTO posts (user_hash, text, message_id, chat_id) "
            "VALUES (?, ?, ?, ?)"
        )
        cur = await db.execute(
            query,
            (h, text, message_id, chat_id),
        )
        await db.execute(
            """INSERT INTO user_stats(user_hash,post_count)
               VALUES(?,1)
               ON CONFLICT(user_hash) DO UPDATE SET post_count=post_count+1""",
            (h,),
        )
        await db.commit()
        return cur.lastrowid


async def switch_reaction(
    post_id: int, user_id: int, emoji: str
) -> Tuple[int, int, int]:
    """Add, switch or remove a reaction.

    • first click      → add reaction   (+1 to that emoji)
    • click same emoji → remove reaction (‑1)
    • click other      → switch: ‑1 old, +1 new
    Returns fresh counts (skull, fire, clown).
    """
    if emoji not in EMOJI_TO_COLUMN:
        raise ValueError("bad emoji")

    new_col = EMOJI_TO_COLUMN[emoji]
    h = hash_user_id(user_id)

    async with dao.get_db() as db:
        cur = await db.execute(
            "SELECT emoji FROM reactions WHERE post_id=? AND user_hash=?",
            (post_id, h),
        )
        row = await cur.fetchone()

        if row is None:  # --- first time -----------------------------------
            await db.execute(
                (
                    "INSERT INTO reactions(post_id,user_hash,emoji) "
                    "VALUES (?,?,?)"
                ),
                (post_id, h, emoji),
            )
            await db.execute(
                f"UPDATE posts SET {new_col}={new_col}+1 WHERE post_id=?",
                (post_id,),
            )

        else:            # --- already reacted ------------------------------
            old_emoji = row[0]
            old_col = EMOJI_TO_COLUMN[old_emoji]

            if old_emoji == emoji:
                # toggle off  → remove row & decrement
                await db.execute(
                    "DELETE FROM reactions WHERE post_id=? AND user_hash=?",
                    (post_id, h),
                )
                await db.execute(
                    f"UPDATE posts SET {old_col}={old_col}-1 WHERE post_id=?",
                    (post_id,),
                )
            else:
                # switch to a new emoji
                await db.execute(
                    (
                        "UPDATE reactions SET emoji=? WHERE "
                        "post_id=? AND user_hash=?"
                    ),
                    (emoji, post_id, h),
                )
                await db.execute(
                    f"""UPDATE posts
                        SET {old_col}={old_col}-1,
                            {new_col}={new_col}+1
                        WHERE post_id=?""",
                    (post_id,),
                )

        await db.commit()

        cur = await db.execute(
            "SELECT skull,fire,clown FROM posts WHERE post_id=?", (post_id,)
        )
        return await cur.fetchone()


async def soft_delete(message_id: int, ctx):
    """Soft‑delete a post and fix counters."""
    await ctx.bot.delete_message(
        chat_id=get_settings().channel_id,
        message_id=message_id,
    )

    async with dao.get_db() as db:
        cur = await db.execute(
            "SELECT user_hash FROM posts WHERE message_id=?",
            (message_id,),
        )
        row = await cur.fetchone()
        if not row:
            return

        user_hash = row[0]

        await db.execute(
            (
                "UPDATE user_stats SET post_count = post_count - 1 "
                "WHERE user_hash=?"
            ),
            (user_hash,),
        )
        await db.execute(
            "UPDATE posts SET is_deleted = 1 WHERE message_id=?",
            (message_id,),
        )
        await db.commit()


# --------------------------- reporting helpers ---
async def user_post_count(user_id: int) -> int:
    """Get user post count."""
    async with dao.get_db() as db:
        cur = await db.execute(
            "SELECT post_count FROM user_stats WHERE user_hash=?",
            (hash_user_id(user_id),),
        )
        row = await cur.fetchone()

    return row[0] if row else 0


async def top_daily(day: date) -> Optional[dict]:
    """Obtain top post of the day."""
    async with dao.get_db() as db:
        cur = await db.execute(
            """
            SELECT message_id,text,skull+fire+clown AS votes
            FROM posts
            WHERE is_deleted=0 AND date(created_at)=?
            ORDER BY votes DESC LIMIT 1
            """,
            (day.isoformat(),),
        )
        row = await cur.fetchone()
    return {"id": row[0], "text": row[1], "votes": row[2]} if row else None


async def weekly_labels_counts(week_start: date):
    """Get weekly stats."""
    counts = await weekly_counts(week_start)
    labels = [(week_start + timedelta(d)).strftime("%a") for d in range(7)]
    return labels, counts
