"""Bot commands handlers."""

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from datetime import timedelta
from datetime import date

from ..services import scream, analytics
from ..core.config import get_settings
from ..services import meme
from ..db import scream_repo
from aiogram.utils.markdown import text, bold

router = Router()

# --- Helper Functions ---
def get_main_keyboard():
    """Main menu keyboard with 2x2 button layout"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📢 Scream"),
                KeyboardButton(text="📊 My Stats")
            ],
            [
                KeyboardButton(text="ℹ️ Help"),
                KeyboardButton(text="🔥 Top Screams")
            ]
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Choose an action..."
    )

# --- Command Handlers ---
@router.message(Command("start"))
async def handle_start(msg: types.Message):
    """Welcome message with main keyboard"""
    welcome_msg = text(
        bold("Welcome to InnoScream! 👋"),
        "A safe space to anonymously share your frustrations and get support.",
        "\nHere's what you can do:",
        "- Share anonymously with /scream",
        "- See your stats with /stats",
        "- Get help with /help",
        "- See top posts with /top",
        sep="\n"
    )
    await msg.answer(welcome_msg, reply_markup=get_main_keyboard())


@router.message(Command("top"))
async def handle_top(msg: types.Message):
    """Show today's top screams with proper formatting"""
    top_post = await scream.get_top_daily(date.today())
    
    if not top_post:
        response = text(
            "No top screams yet today!",
            "Be the first to ", bold("/scream"),
            sep="\n"
        )
    else:
        response = text(
            bold("🔥 Today's Top Scream:"),
            "",
            f"\"{top_post['text']}\"",
            f"👍 {top_post['votes']} reactions",
            sep="\n"
        )
    
    await msg.answer(
        response,
        reply_markup=get_main_keyboard(),
        parse_mode="MarkdownV2"
    )

@router.message(Command("help"))
async def handle_help(msg: types.Message):
    """Detailed help instructions"""
    help_msg = text(
        bold("📖 InnoScream Help Guide"),
        "\nHow to use this bot:",
        "1. To share anonymously:",
        "   - Use /scream command",
        "   - Or press the '📢 Scream' button",
        "   Example: /scream Why are 9AM lectures a thing?",
        "\n2. To see your stats:",
        "   - Use /stats command",
        "   - Or press the '📊 My Stats' button",
        "\n3. To react to posts:",
        "   - Click on 💀, 🤡, or 🔥 under posts",
        "\nAll posts are completely anonymous!",
        sep="\n"
    )
    await msg.answer(help_msg, reply_markup=get_main_keyboard())

# --- Button Handlers ---
@router.message(F.text == "📢 Scream")
async def handle_scream_button(msg: types.Message):
    """Handle Scream button press"""
    await msg.answer(
        "Type your message after /scream:",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text == "📊 My Stats")
async def handle_stats_button(msg: types.Message):
    """Handle Stats button press"""
    await handle_stats(msg)

@router.message(F.text == "ℹ️ Help")
async def handle_help_button(msg: types.Message):
    """Handle Help button press"""
    await handle_help(msg)

@router.message(F.text == "🔥 Top Screams")
async def handle_top_button(msg: types.Message):
    """Handle Top Screams button press"""
    await handle_top(msg)


@router.message(Command("scream"))
async def handle_scream(msg: types.Message):
    """Post an anonymous scream to the channel."""
    try:
        text_content = msg.text.split(maxsplit=1)[1]
    except IndexError:
        await msg.answer(
            "Please provide text after /scream\nExample: /scream Why 9AM lectures?",
            reply_markup=get_main_keyboard()
        )
        return


    # Format the post with ID visible to admins
    formatted_text = text_content

    # Build reaction keyboard
    builder = InlineKeyboardBuilder()
    for emoji in scream.EMOJI_TO_COLUMN:
        builder.add(InlineKeyboardButton(
            text=f"{emoji} 0",
            callback_data=f"react_{emoji}_tmp"
        ))

    # Send to channel
    sent = await msg.bot.send_message(
        chat_id=get_settings().channel_id,
        text=formatted_text,
        reply_markup=builder.as_markup()
    )

    # Save to DB first to get the post_id
    post_id = await scream.save_scream(
        user_id=msg.from_user.id,
        text=text_content,
        message_id=sent.message_id,
        chat_id=get_settings().channel_id,
    )

    # Update keyboard with real post_id
    builder = InlineKeyboardBuilder()
    for emoji in scream.EMOJI_TO_COLUMN:
        builder.add(InlineKeyboardButton(
            text=f"{emoji} 0",
            callback_data=f"react_{emoji}_{post_id}"
        ))
    
    await sent.edit_reply_markup(reply_markup=builder.as_markup())
    await msg.answer(
        "✅ Your scream has been posted anonymously!",
        reply_markup=get_main_keyboard()
    )


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
    if msg.from_user.id not in get_settings().admin_ids:
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
    """Generate a meme from text and post it (admin only).

    /meme <text>
    """
    if msg.from_user.id not in get_settings().admin_ids:
        await msg.answer("⛔️ Unauthorized")
        return

    try:
        text = msg.text.split(maxsplit=1)[1]
    except IndexError:
        await msg.answer("Usage: /meme <text>")
        return

    meme_url = await meme.generate_meme(text)
    if meme_url:
        await msg.bot.send_photo(
            get_settings().channel_id, meme_url,
            caption=text
        )
        await msg.answer("✅ Meme posted!")
    else:
        await msg.answer("⚠️ Couldn’t generate meme (check ImgFlip creds?)")
