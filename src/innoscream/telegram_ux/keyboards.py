from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    """Keyboard for main commands"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/scream")],
            [KeyboardButton(text="/stats")],
            [KeyboardButton(text="/help")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_reaction_keyboard(scream_id: str):
    """Inline keyboard for reactions"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍", callback_data=f"react_upvote_{scream_id}"),
                InlineKeyboardButton(text="❤️", callback_data=f"react_love_{scream_id}"),
                InlineKeyboardButton(text="😂", callback_data=f"react_laugh_{scream_id}")
            ]
        ]
    )
    return keyboard

def get_admin_keyboard():
    """Keyboard for admin commands"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/delete")],
            [KeyboardButton(text="/moderate")]
        ],
        resize_keyboard=True
    )
    return keyboard