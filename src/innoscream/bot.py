import os
import sqlite3
from dotenv import load_dotenv
from telegram_ux import CoreBackendImplementation, setup_bot

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
ADMINS = list(map(int, os.getenv('ADMINS').split(','))) if os.getenv('ADMINS') else []

def create_tables():
    """Create database tables matching CoreBackendImplementation expectations"""
    with sqlite3.connect('screams.db') as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL,
                text TEXT NOT NULL,
                skull INTEGER DEFAULT 0,
                fire INTEGER DEFAULT 0,
                clown INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id TEXT PRIMARY KEY,
                post_count INTEGER DEFAULT 0
            )
        """)

def get_max_post_id():
    """Gets the maximal id of all posts."""
    with sqlite3.connect('screams.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(post_id) FROM posts")
        return cursor.fetchone()[0] or 0

if __name__ == "__main__":
    # Initialize database
    create_tables()
    
    # Create backend implementation
    backend = CoreBackendImplementation()
    
    # Start the bot
    setup_bot(TOKEN, backend, admins=ADMINS)