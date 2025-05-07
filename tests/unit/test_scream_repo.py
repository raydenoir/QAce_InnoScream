# tests/unit/test_scream_repo.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date
from innoscream.db import scream_repo

@pytest.mark.asyncio
async def test_soft_delete_success():
    """Test successful message deletion."""
    mock_ctx = MagicMock()
    mock_ctx.bot.delete_message = AsyncMock()
    mock_ctx.get_settings.return_value.channel_id = -100123
    
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.execute_fetchall = AsyncMock(return_value=[("user_hash",)])
    mock_db.commit = AsyncMock()
    
    with patch('src.innoscream.db.dao.get_db', return_value=mock_db):
        await scream_repo.soft_delete(123, mock_ctx)
        mock_ctx.bot.delete_message.assert_called_once()

# tests/unit/test_scream_repo.py
@pytest.mark.asyncio
async def test_create_post():
    """Test post creation."""
    mock_db = AsyncMock()
    mock_cursor = AsyncMock()
    mock_cursor.lastrowid = 1
    mock_db.execute.return_value = mock_cursor
    mock_db.commit = AsyncMock()
    
    # Properly mock the async context manager
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_db
    mock_context.__aexit__.return_value = None
    
    with patch('src.innoscream.db.dao.get_db', return_value=mock_context):
        post_id = await scream_repo.create_post(
            user_id=123,
            text="test",
            message_id=456,
            chat_id=789
        )
        assert post_id == 1


@pytest.mark.asyncio
async def test_switch_reaction_invalid_emoji():
    """Test switch_reaction with invalid emoji."""
    with pytest.raises(ValueError, match="bad emoji"):
        await scream_repo.switch_reaction(1, 123, "❌")


# tests/unit/test_scream_repo.py
@pytest.mark.asyncio
async def test_user_post_count_no_posts():
    """Test user_post_count when user has no posts."""
    mock_db = AsyncMock()
    # Mock execute_fetchall to return None (no rows)
    mock_db.execute_fetchall = AsyncMock(return_value=None)
    
    # Mock cursor to return None for fetchone
    mock_cursor = AsyncMock()
    mock_cursor.fetchone.return_value = None
    mock_db.execute.return_value = mock_cursor
    
    # Mock the context manager
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_db
    mock_context.__aexit__.return_value = None
    
    with patch('src.innoscream.db.dao.get_db', return_value=mock_context), \
         patch('src.innoscream.db.scream_repo.hash_user_id', return_value="hashed"):
        count = await scream_repo.user_post_count(123)
        assert count == 0

@pytest.mark.asyncio
async def test_top_daily_no_posts():
    """Test top_daily when there are no posts."""
    mock_db = AsyncMock()
    # Mock execute_fetchall to return empty list (no rows)
    mock_db.execute_fetchall = AsyncMock(return_value=[])
    # Mock fetchone to return None
    mock_db.execute.return_value.fetchone.return_value = None

    # Mock the context manager
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_db
    mock_context.__aexit__.return_value = None

    with patch('src.innoscream.db.dao.get_db', return_value=mock_context):
        result = await scream_repo.top_daily(date.today())
        assert result is None
