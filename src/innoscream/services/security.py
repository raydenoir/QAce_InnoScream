"""Security module."""

import hashlib
from ..core.config import get_settings


def hash_user_id(user_id: int) -> str:
    """Hashes the user's ID using salt.

    Returns:
        hashed ID
    """
    salt = get_settings().hash_salt
    return hashlib.sha256(f"{salt}{user_id}".encode()).hexdigest()
