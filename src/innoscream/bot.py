import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
ADMINS = list(map(int, os.getenv('ADMINS').split(','))) if os.getenv('ADMINS') else [] #TODO: get from database
CHANNEL_ID = os.getenv('CHANNEL_ID')

bot = Bot(token=TOKEN)
dp = Dispatcher()


def create_tables():
    """Connects to the database if it exists, otherwise creates and connects."""
    with sqlite3.connect('screams.db') as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                skull INTEGER DEFAULT 0,
                fire INTEGER DEFAULT 0,
                clown INTEGER DEFAULT 0,
                message_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                post_count INTEGER DEFAULT 0
            )
        """)


def get_max_post_id():
    """Gets the maximal id of all posts."""
    with sqlite3.connect('screams.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(post_id) FROM posts")
        return cursor.fetchone()[0] or 0

create_tables()
next_post_id = get_max_post_id() + 1

@dp.message(Command("scream"))
async def handle_scream(message: types.Message):
    """Handles /scream command."""
    global next_post_id

    try:
        text = message.text.split(maxsplit=1)[1]
    except IndexError:
        await message.answer("Please provide a message after /scream")
        return

    # create a post entry
    post_id = next_post_id
    next_post_id += 1

    # create reactions keyboard
    builder = InlineKeyboardBuilder()
    reactions = ['💀', '🔥', '🤡']
    for emoji in reactions:
        builder.add(InlineKeyboardButton(
            text=f"{emoji} 0",
            callback_data=f"react_{emoji}_{post_id}"
        ))

    try:
        # send message
        sent_message = await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        await message.answer("Failed to post scream. Please try again later.")
        return

    # store post data
    with sqlite3.connect('screams.db') as conn:
        conn.execute("""
            INSERT INTO posts 
            (post_id, user_id, text, message_id, chat_id)
            VALUES (?, ?, ?, ?, ?)
        """, (next_post_id, message.from_user.id, text,
              sent_message.message_id, sent_message.chat.id))

        # Update user stats
        conn.execute("""
            INSERT INTO user_stats (user_id, post_count)
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET 
            post_count = post_count + 1
        """, (message.from_user.id,))

        conn.commit()

    next_post_id += 1
    await message.delete()


@dp.callback_query(F.data.startswith("react_"))
async def handle_reaction(callback: types.CallbackQuery):
    """Helper function handling the reactions."""
    _, emoji, post_id = callback.data.split('_')
    post_id = int(post_id)

    # update reaction in database
    column = {'💀': 'skull', '🔥': 'fire', '🤡': 'clown'}.get(emoji)
    if not column:
        await callback.answer("Invalid reaction")
        return

    with sqlite3.connect('screams.db') as conn:
        conn.execute(f"""
            UPDATE posts SET {column} = {column} + 1 
            WHERE post_id = ?
        """, (post_id,))

        cursor = conn.execute("""
                SELECT channel_id, message_id, skull, fire, clown 
                FROM posts WHERE post_id = ?
            """, (post_id,))
        post_data = cursor.fetchone()
    
    if not post_data:
         await callback.answer("Post not found!")
         return
 
    channel_id, message_id, skull, fire, clown = post_data

    if not post_data:
        await callback.answer("Post not found!")
        return

    channel_id, message_id, skull, fire, clown = post_data

    builder = InlineKeyboardBuilder()
    for emoji, count in zip(['💀', '🔥', '🤡'], [skull, fire, clown]):
        builder.add(InlineKeyboardButton(
            text=f"{emoji} {count}",
            callback_data=f"react_{emoji}_{post_id}"
        ))

    try:
        await bot.edit_message_reply_markup(
            chat_id=channel_id,
            message_id=message_id,
            reply_markup=builder.as_markup()
        )
        await callback.answer()
    except Exception as e:
        await callback.answer("Failed to update reactions", show_alert=True)


@dp.message(Command("delete"))
async def handle_delete(message: types.Message):
    """Handles the /delete command."""
    if message.from_user.id not in ADMINS:
        await message.answer("⛔️ Unauthorized!")
        return

    try:
        post_id = int(message.text.split(maxsplit=1)[1])
    except (IndexError, ValueError):
        await message.answer("Usage: /delete <post_id>")
        return

    with sqlite3.connect('screams.db') as conn:
        cursor = conn.execute("""
                SELECT chat_id, message_id 
                FROM posts WHERE post_id = ?
            """, (post_id,))
        post = cursor.fetchone()

        if not post:
            await message.answer("❌ Post not found!")
            return

        # delete from database
        conn.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
        conn.commit()

    await bot.delete_message(chat_id=post[0], message_id=post[1])
    await message.answer(f"✅ Post {post_id} deleted")


@dp.message(Command("stats"))
async def handle_stats(message: types.Message):
    """Handles /stats command."""
    with sqlite3.connect('screams.db') as conn:
        cursor = conn.execute("""
            SELECT post_count FROM user_stats 
            WHERE user_id = ?
        """, (message.from_user.id,))
        result = cursor.fetchone()

    count = result[0] if result else 0
    await message.answer(f"📊 Your total screams: {count}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())