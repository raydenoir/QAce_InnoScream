from datetime import date, timedelta
from ..db import dao
from ..services.security import hash_user_id
from ..services.analytics import weekly_counts
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


async def add_reaction(post_id: int, user_id: int, emoji: str) -> tuple[int, int, int]:
    if emoji not in EMOJI_TO_COLUMN:
        raise ValueError("Bad emoji")

    new_col = EMOJI_TO_COLUMN[emoji]
    hashed = hash_user_id(user_id)

    async with dao.get_db() as db:
        # check existing
        cur = await db.execute(
            "SELECT emoji FROM reactions WHERE post_id=? AND user_hash=?",
            (post_id, hashed),
        )
        row = await cur.fetchone()

        if row is None:
            # first time
            await db.execute(
                "INSERT INTO reactions(post_id, user_hash, emoji) VALUES (?,?,?)",
                (post_id, hashed, emoji),
            )
            await db.execute(
                f"UPDATE posts SET {new_col} = {new_col} + 1 WHERE post_id=?",
                (post_id,),
            )
        else:
            old_emoji = row[0]
            if old_emoji == emoji:
                raise RuntimeError("same-emoji")

            old_col = EMOJI_TO_COLUMN[old_emoji]

            # switch
            await db.execute(
                "UPDATE reactions SET emoji=? WHERE post_id=? AND user_hash=?",
                (emoji, post_id, hashed),
            )
            await db.execute(
                f"""
                UPDATE posts
                SET {old_col} = {old_col} - 1,
                    {new_col} = {new_col} + 1
                WHERE post_id=?
                """,
                (post_id,),
            )

        await db.commit()

        cur = await db.execute(
            "SELECT skull, fire, clown FROM posts WHERE post_id=?",
            (post_id,),
        )
        return await cur.fetchone()


async def delete_post(post_id: int, ctx):
    await ctx.bot.delete_message(chat_id=settings.channel_id, message_id=post_id)

    async with dao.get_db() as db:
        result = await db.execute(
            "SELECT user_hash FROM posts WHERE message_id = ?", (post_id,)
        )
        row = await result.fetchone()

        if row:
            user_hash = row[0]

            await db.execute(
                "UPDATE user_stats SET post_count = post_count - 1 WHERE user_hash = ?",
                (user_hash,)
            )
            await db.execute(
                "UPDATE posts SET is_deleted = 1 WHERE message_id = ?",
                (post_id,)
            )

            # for security reasons, I believe the initial post should be kept
            # await db.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
            await db.commit()
        else:
            print(f"Post with ID {post_id} not found.")


async def get_user_stats(user_id: int) -> int:
    async with dao.get_db() as db:
        hashed = hash_user_id(user_id)
        cur = await db.execute(
            "SELECT post_count FROM user_stats WHERE user_hash = ?", (hashed,)
        )
        row = await cur.fetchone()
        return row[0] if row else 0


async def get_top_daily(day: date) -> dict | None:
    async with dao.get_db() as db:
        cur = await db.execute(
            """
            SELECT post_id, text, skull+fire+clown AS votes
            FROM posts
            WHERE is_deleted = 0
              AND date(created_at)=?
            ORDER BY votes DESC
            LIMIT 1
            """,
            (day.isoformat(),),
        )
        row = await cur.fetchone()            # ← fetch result here

    if row:
        return {"id": row[0], "text": row[1], "votes": row[2]}
    return None


async def weekly_labels_counts(week_start: date):
    counts = await weekly_counts(week_start)
    labels = [(week_start + timedelta(d)).strftime("%a") for d in range(7)]
    return labels, counts
