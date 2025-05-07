from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import timedelta

from ..services import scream, analytics
from ..core.config import get_settings
from ..services import meme

router = Router()
settings = get_settings()


# /scream --------------------------------------------------------
@router.message(Command("scream"))
async def handle_scream(msg: types.Message):
    """Post an anonymous scream to the channel."""
    try:
        text = msg.text.split(maxsplit=1)[1]
    except IndexError:
        await msg.answer("Please provide text after /scream")
        return

    # Build initial keyboard (all counts 0)
    builder = InlineKeyboardBuilder()
    for e in scream.EMOJI_TO_COLUMN:
        builder.add(
            InlineKeyboardButton(
                text=f"{e} 0",
                callback_data=f"react_{e}_tmp"
                )
            )

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
        builder.add(
            InlineKeyboardButton(
                text=f"{e} 0",
                callback_data=f"react_{e}_{post_id}"
                )
            )
    await sent.edit_reply_markup(reply_markup=builder.as_markup())
    await msg.delete()


# reaction callbacks --------------------------------------------
@router.callback_query(F.data.startswith("react_"))
async def handle_reaction(cb: types.CallbackQuery):
    """Handle reaction button clicks."""
    _, emoji, post_id = cb.data.split("_", 2)
    post_id = int(post_id)

    try:
        counts = await scream.add_reaction(post_id, cb.from_user.id, emoji)
    except RuntimeError:
        await cb.answer(
            "You already picked that one!",
            show_alert=True
        )
        return

    builder = InlineKeyboardBuilder()
    for e, c in zip(["💀", "🔥", "🤡"], counts):
        builder.add(
            InlineKeyboardButton(
                text=f"{e} {c}",
                callback_data=f"react_{e}_{post_id}"
                )
            )

    await cb.message.edit_reply_markup(reply_markup=builder.as_markup())
    await cb.answer()


# /delete --------------------------------------------------------
@router.message(Command("delete"))
async def handle_delete(msg: types.Message):
    """Delete a scream (admin only)."""
    if msg.from_user.id not in settings.admin_ids:
        await msg.answer("⛔️ Unauthorized")
        return
    try:
        message_id = int(msg.text.split(maxsplit=1)[1])
    except (IndexError, ValueError):
        await msg.answer("Usage: /delete <post_id>")
        return

    await scream.delete_post(message_id, msg)
    await msg.answer(f"✅ Post {message_id} deleted")


# /stats ---------------------------------------------------------
@router.message(Command("stats"))
async def handle_stats(msg: types.Message):
    """Send personal stats with weekly graph."""
    count = await scream.get_user_stats(msg.from_user.id)

    # weekly graph
    monday = (msg.date - timedelta(days=msg.date.weekday())).date()
    labels, data = await scream.weekly_labels_counts(monday)
    chart = await analytics.chart_url(labels, data)

    text = f"📊 You’ve posted **{count}** screams so far."
    await msg.answer_photo(chart, caption=text, parse_mode="Markdown")


@router.message(Command("meme"))
async def handle_meme(msg: types.Message):
    """
    /meme <text>
    Generate a meme from text and post it (admin only).
    """
    if msg.from_user.id not in settings.admin_ids:
        await msg.answer("⛔️ Unauthorized")
        return

    try:
        text = msg.text.split(maxsplit=1)[1]
    except IndexError:
        await msg.answer("Usage: /meme <text>")
        return

    meme_url = await meme.generate_meme(text)
    if meme_url:
        await msg.bot.send_photo(settings.channel_id, meme_url, caption=text)
        await msg.answer("✅ Meme posted!")
    else:
        await msg.answer("⚠️ Couldn’t generate meme (check ImgFlip creds?)")
