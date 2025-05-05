from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    """Keyboard for main commands"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("/scream"))
    keyboard.add(KeyboardButton("/stats"))
    keyboard.add(KeyboardButton("/help"))
    return keyboard

def get_reaction_keyboard(scream_id: str):
    """Inline keyboard for reactions"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("👍", callback_data=f"react_upvote_{scream_id}"),
        InlineKeyboardButton("❤️", callback_data=f"react_love_{scream_id}"),
        InlineKeyboardButton("😂", callback_data=f"react_laugh_{scream_id}")
    )
    return keyboard

def get_admin_keyboard():
    """Keyboard for admin commands"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("/delete"))
    keyboard.add(KeyboardButton("/moderate"))
    return keyboard