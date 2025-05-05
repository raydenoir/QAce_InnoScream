from aiogram.utils.formatting import (
    Text,
    Bold,
    as_list,
    as_section
)

def get_scream_success_message():
    # Convert the formatted text to a string
    return str(as_list(
        as_section(
            Bold("📢 Your scream has been heard!"),
            "It's now anonymous in the scream pile.",
            "Others can react to it with 👍, ❤️, or 😂"
        )
    ))

def get_stats_message(post_count: int, reactions_received: dict):
    # Convert the formatted text to a string
    return str(as_list(
        as_section(
            Bold("📊 Your Stats"),
            f"Total screams: {post_count}",
            "",
            "Reactions received:",
            f"👍 {reactions_received.get('upvote', 0)}",
            f"❤️ {reactions_received.get('love', 0)}",
            f"😂 {reactions_received.get('laugh', 0)}"
        )
    ))

def get_top_scream_message(scream_text: str, reactions: dict, meme_url: str = None):
    # Convert the formatted text to a string
    message = str(as_list(
        as_section(
            Bold("🔥 Today's Top Scream"),
            f'"{scream_text}"',
            "",
            "Reactions:",
            f"👍 {reactions.get('upvote', 0)}",
            f"❤️ {reactions.get('love', 0)}",
            f"😂 {reactions.get('laugh', 0)}"
        )
    ))
    return message, meme_url