from aiogram import Router, types, F
from aiogram.filters import Command  # Add this import
from aiogram.utils.markdown import text, bold
from .messages import get_scream_success_message, get_stats_message
from .keyboards import get_main_keyboard, get_reaction_keyboard
import hashlib
import sqlite3
from .interface import BackendInterface
from aiogram import Dispatcher  # Add Dispatcher import

class TelegramUX:
    def __init__(self, backend: BackendInterface):
        self.backend = backend
        self.router = Router()
        self._register_handlers()

    def _register_handlers(self):
        """Register all command handlers"""
        self.router.message.register(self.start_command, Command("start"))
        self.router.message.register(self.help_command, Command("help"))
        self.router.message.register(self.scream_command, Command("scream"))
        self.router.message.register(self.stats_command, Command("stats"))
        self.router.callback_query.register(
            self.handle_reaction,
            F.data.startswith("react_")
        )

    async def start_command(self, message: types.Message):
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

    async def help_command(self, message: types.Message):
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
    
    async def scream_command(self, message: types.Message):
        """Handler for /scream command with backend integration"""
        # Get the text after the command
        if len(message.text.split()) > 1:
            scream_text = message.text.split(maxsplit=1)[1]
        else:
            await message.answer(
                "Please provide your scream after the command. Example: /scream I hate 9AM lectures!",
                reply_markup=get_main_keyboard()
            )
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
            chat_id="-1002513509359",  # Replace with your channel
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

    async def handle_reaction(self, callback: types.CallbackQuery):
        """Handle reaction button presses"""
        _, reaction_type, post_id = callback.data.split('_')
        post_id = int(post_id)
        
        success = await self.backend.add_reaction(post_id, reaction_type)
        if success:
            await callback.answer("Reaction added!")
        else:
            await callback.answer("Failed to add reaction", show_alert=True)

    async def handle_delete(self, message: types.Message, admins: list[int]):
        """Handles the /delete command."""
        if message.from_user.id not in admins:
            await message.answer("⛔️ Unauthorized!")
            return

        try:
            post_id = int(message.text.split(maxsplit=1)[1])
        except (IndexError, ValueError):
            await message.answer("Usage: /delete <post_id>")
            return

        with sqlite3.connect('screams.db') as conn:
            cursor = conn.execute("SELECT * FROM posts WHERE post_id = ?", (post_id,))
            post = cursor.fetchone()

            if not post:
                await message.answer("❌ Post not found!")
                return

            conn.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
            conn.commit()

        await message.answer(f"✅ Post {post_id} deleted")

    def register_handlers(self, dp: Dispatcher, admins: list[int] = None):
        """Register all handlers with the dispatcher"""
        dp.include_router(self.router)
        
        # Register admin handlers if admins list provided
        if admins:
            admin_router = Router()
            admin_router.message.register(
                lambda m: self.handle_delete(m, admins),
                Command("delete")
            )
            dp.include_router(admin_router)