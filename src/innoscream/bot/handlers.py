from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..services import scream
from ..core.config import get_settings

router = Router()
settings = get_settings()


# /scream --------------------------------------------------------
@router.message(Command("scream"))
async def handle_scream(msg: types.Message):
    try:
        text = msg.text.split(maxsplit=1)[1]
    except IndexError:
        await msg.answer("Please provide text after /scream")
        return

    # Build initial keyboard (all counts 0)
    builder = InlineKeyboardBuilder()
    for e in scream.EMOJI_TO_COLUMN:
        builder.add(InlineKeyboardButton(text=f"{e} 0", callback_data=f"react_{e}_tmp"))

    sent = await msg.bot.send_message(
        chat_id=settings.channel_id,
        text=text,
        reply_markup=builder.as_markup()
    )

    # Persist & get real post_id
    post_id = await scream.save_scream(
        user_id=msg.from_user.id,
        text=text,
        message_id=sent.message_id,
        chat_id=sent.chat.id,
    )

    # Update callback_data with real post_id
    builder = InlineKeyboardBuilder()
    for e in scream.EMOJI_TO_COLUMN:
        builder.add(InlineKeyboardButton(text=f"{e} 0", callback_data=f"react_{e}_{post_id}"))
    await sent.edit_reply_markup(reply_markup=builder.as_markup())
    await msg.delete()


# reaction callbacks --------------------------------------------
@router.callback_query(F.data.startswith("react_"))
async def handle_reaction(cb: types.CallbackQuery):
    _, emoji, post_id = cb.data.split("_", 2)
    post_id = int(post_id)

    try:
        counts = await scream.add_reaction(post_id, cb.from_user.id, emoji)
    except RuntimeError:
        await cb.answer("You already picked that one!", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for e, c in zip(["💀", "🔥", "🤡"], counts):
        builder.add(InlineKeyboardButton(text=f"{e} {c}", callback_data=f"react_{e}_{post_id}"))

    await cb.message.edit_reply_markup(reply_markup=builder.as_markup())
    await cb.answer()


# /delete --------------------------------------------------------
@router.message(Command("delete"))
async def handle_delete(msg: types.Message):
    if msg.from_user.id not in settings.admin_ids:
        await msg.answer("⛔️ Unauthorized")
        return
    try:
        post_id = int(msg.text.split(maxsplit=1)[1])
    except (IndexError, ValueError):
        await msg.answer("Usage: /delete <post_id>")
        return

    await scream.delete_post(post_id, msg)
    await msg.answer(f"✅ Post {post_id} deleted")


# /stats ---------------------------------------------------------
@router.message(Command("stats"))
async def handle_stats(msg: types.Message):
    count = await scream.get_user_stats(msg.from_user.id)
    await msg.answer(f"📊 Your total screams: {count}")