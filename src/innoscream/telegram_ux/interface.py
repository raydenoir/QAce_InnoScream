from typing import Optional, Dict
from dataclasses import dataclass
import sqlite3
class BackendInterface:
    """Interface for communication with core logic"""
    
    async def post_scream(self, user_id_hash: str, scream_text: str):
        """Post a new scream to the backend"""
        raise NotImplementedError
        
    async def get_stats(self, user_id_hash: str) -> Dict[str, int]:
        """Get user statistics"""
        raise NotImplementedError
        
    async def add_reaction(self, scream_id: str, reaction_type: str) -> bool:
        """Add reaction to a scream"""
        raise NotImplementedError

@dataclass
class ScreamPost:
    id: str
    text: str
    author_hash: str
    reactions: Dict[str, int]

class CoreBackendImplementation(BackendInterface):
    """Implementation of BackendInterface using the core logic database"""
    
    async def post_scream(self, user_id_hash: str, scream_text: str) -> ScreamPost:
        """Post a new scream to the backend"""
        with sqlite3.connect('screams.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(post_id) FROM posts")
            post_id = cursor.fetchone()[0] or 0
            post_id += 1
            
            cursor.execute("""
                INSERT INTO posts (post_id, user_id, text, skull, fire, clown)
                VALUES (?, ?, ?, 0, 0, 0)
            """, (post_id, user_id_hash, scream_text))
            conn.commit()
            
        return ScreamPost(
            id=str(post_id),
            text=scream_text,
            author_hash=user_id_hash,
            reactions={'skull': 0, 'fire': 0, 'clown': 0}
        )
        
    async def get_stats(self, user_id_hash: str) -> Dict[str, int]:
        """Get user statistics"""
        with sqlite3.connect('screams.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT post_count FROM user_stats WHERE user_id = ?
            """, (user_id_hash,))
            result = cursor.fetchone()
            
            cursor.execute("""
                SELECT SUM(skull), SUM(fire), SUM(clown) 
                FROM posts WHERE user_id = ?
            """, (user_id_hash,))
            reactions = cursor.fetchone()
            
        return {
            'post_count': result[0] if result else 0,
            'skull': reactions[0] if reactions[0] else 0,
            'fire': reactions[1] if reactions[1] else 0,
            'clown': reactions[2] if reactions[2] else 0
        }
        
    async def add_reaction(self, scream_id: str, reaction_type: str) -> bool:
        """Add reaction to a scream"""
        column_map = {
            'upvote': 'skull',
            'love': 'fire',
            'laugh': 'clown'
        }
        
        if reaction_type not in column_map:
            return False
            
        with sqlite3.connect('screams.db') as conn:
            conn.execute(f"""
                UPDATE posts SET {column_map[reaction_type]} = {column_map[reaction_type]} + 1
                WHERE post_id = ?
            """, (scream_id,))
            conn.commit()
            
        return True