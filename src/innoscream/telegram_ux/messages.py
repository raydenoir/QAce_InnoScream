from aiogram.utils.markdown import text, bold, escape_md

def get_scream_success_message():
    return text(
        "📢 Your scream has been heard!",
        "It's now anonymous in the scream pile.",
        "Others can react to it with 👍, ❤️, or 😂",
        sep="\n"
    )

def get_stats_message(post_count: int, reactions_received: dict):
    return text(
        bold("📊 Your Stats"),
        f"Total screams: {post_count}",
        "\nReactions received:",
        f"👍 {reactions_received.get('upvote', 0)}",
        f"❤️ {reactions_received.get('love', 0)}",
        f"😂 {reactions_received.get('laugh', 0)}",
        sep="\n"
    )

def get_top_scream_message(scream_text: str, reactions: dict, meme_url: str = None):
    message = text(
        bold("🔥 Today's Top Scream"),
        f'"{escape_md(scream_text)}"',
        "\nReactions:",
        f"👍 {reactions.get('upvote', 0)}",
        f"❤️ {reactions.get('love', 0)}",
        f"😂 {reactions.get('laugh', 0)}",
        sep="\n"
    )
    return message, meme_url