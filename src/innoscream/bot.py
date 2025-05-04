import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
ADMINS = list(map(int, os.getenv('ADMINS').split(','))) if os.getenv('ADMINS') else [] #TODO: get from database

bot = Bot(token=TOKEN)
dp = Dispatcher()

# posts have to be stored in the database
posts = {}
user_stats = {}
next_post_id = 1


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
    reactions = ["💀", "🔥", "🤡"]
    for emoji in reactions:
        builder.add(InlineKeyboardButton(
            text=f"{emoji} 0",
            callback_data=f"react_{emoji}_{post_id}"
        ))

    # send message
    sent_message = await message.answer(
        f"🗣️ Anonymous scream:\n\n{text}",
        reply_markup=builder.as_markup()
    )

    # store post data
    #TODO: database module integration
    posts[post_id] = {
        "user_id": message.from_user.id,
        "text": text,
        "reactions": {reaction: 0 for reaction in reactions},
        "message_id": sent_message.message_id,
        "chat_id": sent_message.chat.id
    }

    # update user stats
    user_stats[message.from_user.id] = user_stats.get(message.from_user.id, 0) + 1

    # delete original message
    await message.delete()


@dp.callback_query(F.data.startswith("react_"))
async def handle_reaction(callback: types.CallbackQuery):
    """Helper function handling the reactions."""
    _, emoji, post_id = callback.data.split('_')
    post_id = int(post_id)

    if post_id not in posts:
        await callback.answer("Post not found!")
        return

    # update reaction count
    posts[post_id]["reactions"][emoji] += 1 # TODO: database

    # update keyboard
    builder = InlineKeyboardBuilder()
    for reaction, count in posts[post_id]["reactions"].items():
        builder.add(InlineKeyboardButton(
            text=f"{reaction} {count}",
            callback_data=f"react_{reaction}_{post_id}"
        ))

    await callback.message.edit_reply_markup(
        reply_markup=builder.as_markup()
    )
    await callback.answer()


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

    if post_id not in posts:
        await message.answer("❌ Post not found!")
        return

    await bot.delete_message(
        chat_id=posts[post_id]["chat_id"],
        message_id=posts[post_id]["message_id"]
    )

    del posts[post_id]
    await message.answer(f"✅ Post {post_id} deleted")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())