from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.markdown import text, bold
from .messages import get_scream_success_message
from .keyboards import get_main_keyboard, get_reaction_keyboard
import hashlib
import uuid
from .interface import BackendInterface

async def start_command(message: types.Message):
    """Handler for /start command"""
    welcome_text = text(
        bold("Welcome to InnoScream!"),
        "Here you can anonymously share your frustrations and get support from the community.",
        "\nAvailable commands:",
        "/scream [text] - Share your frustration anonymously",
        "/stats - View your post statistics",
        "/help - Show this message",
        sep="\n"
    )
    await message.answer(welcome_text)

async def help_command(message: types.Message):
    """Handler for /help command"""
    help_text = text(
        bold("InnoScream Help"),
        "This bot allows you to:",
        "- Share frustrations anonymously with /scream",
        "- View top daily screams",
        "- See your statistics with /stats",
        "- React to others' posts with emojis",
        sep="\n"
    )
    await message.answer(help_text)

class TelegramUX:
    def __init__(self, backend: BackendInterface):
        self.backend = backend
    
    async def scream_command(self, message: types.Message):
        """Handler for /scream command with backend integration"""
        scream_text = message.get_args()
        
        if not scream_text:
            await message.answer("Please provide your scream after the command. Example: /scream I hate 9AM lectures!")
            return
        
        # Generate anonymous ID
        user_id_hash = hashlib.sha256(str(message.from_user.id).encode()).hexdigest()[:8]
        
        # Call backend to post the scream
        post = await self.backend.post_scream(user_id_hash, scream_text)
        
        # Send confirmation to user
        await message.answer(
            get_scream_success_message(),
            reply_markup=get_main_keyboard()
        )
        
        # Post to channel (could be moved to backend)
        channel_message = f"New scream (#{post.id}):\n{scream_text}"
        await message.bot.send_message(
            chat_id="@InnoScreamDemo",  # Replace with your channel
            text=channel_message,
            reply_markup=get_reaction_keyboard(post.id)
        )

    async def stats_command(self, message: types.Message):
        """Handler for /stats command"""
        user_id_hash = hashlib.sha256(str(message.from_user.id).encode()).hexdigest()[:8]
        stats = await self.backend.get_stats(user_id_hash)
        
        await message.answer(
            get_stats_message(
                stats['post_count'],
                {
                    'upvote': stats['skull'],
                    'love': stats['fire'],
                    'laugh': stats['clown']
                }
            ),
            reply_markup=get_main_keyboard()
        )

    def register_handlers(self, dp: Dispatcher):
        """Register all command handlers"""
        # Register basic commands as standalone functions
        dp.register_message_handler(start_command, commands=["start"])
        dp.register_message_handler(help_command, commands=["help"])
        dp.register_message_handler(start_command, commands=["start"])
        dp.register_message_handler(self.scream_command, commands=["scream"])
        dp.register_message_handler(self.stats_command, commands=["stats"])
        
        # Register scream command with backend integration
        dp.register_message_handler(
            self.scream_command, 
            commands=["scream"], 
            commands_prefix="/"
        )