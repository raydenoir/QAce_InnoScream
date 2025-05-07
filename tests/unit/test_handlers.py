# tests/unit/test_handlers.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import types, Router
from aiogram.filters import Command

@pytest.fixture(autouse=True)
def mock_settings():
    with patch('innoscream.core.config.get_settings') as mock_settings:
        mock_settings.return_value = MagicMock(
            bot_token="test_token",
            channel_id="-1001234567890",
            admin_ids={123},
            imgflip_user="test_user",
            imgflip_pass="test_pass"
        )
        yield
        

@pytest.fixture
def mock_message():
    """Fixture providing a properly mocked message."""
    msg = MagicMock(spec=types.Message)
    msg.from_user = MagicMock()
    msg.from_user.id = 123
    msg.answer = AsyncMock()
    msg.bot.send_message = AsyncMock()
    return msg

@pytest.mark.asyncio
async def test_handle_start(mock_message):
    """Test /start command handler."""
    from innoscream.bot.handlers import handle_start
    
    await handle_start(mock_message)
    mock_message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_handle_scream_success(mock_message):
    """Test successful scream posting."""
    from innoscream.bot.handlers import handle_scream
    
    mock_message.text = "/scream test message"
    with patch('innoscream.services.scream.save_scream', new=AsyncMock(return_value=1)):
        await handle_scream(mock_message)
        mock_message.bot.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_handle_reaction():
    """Test reaction handling."""
    mock_callback = MagicMock()
    mock_callback.data = "react_🔥_123"
    mock_callback.from_user = MagicMock()
    mock_callback.from_user.id = 456
    mock_callback.message = MagicMock()
    mock_callback.message.edit_reply_markup = AsyncMock()
    mock_callback.answer = AsyncMock()
    
    with patch('innoscream.services.scream.add_reaction', new=AsyncMock(return_value=(1, 2, 3))):
        from innoscream.bot.handlers import handle_reaction
        await handle_reaction(mock_callback)
        mock_callback.message.edit_reply_markup.assert_called_once()


@pytest.mark.asyncio
async def test_handle_top_no_posts():
    """Test /top command when there are no posts."""
    mock_message = MagicMock(spec=types.Message)
    mock_message.answer = AsyncMock()
    
    with patch('innoscream.services.scream.get_top_daily', new=AsyncMock(return_value=None)):
        from innoscream.bot.handlers import handle_top
        await handle_top(mock_message)
        assert "No top screams yet today!" in mock_message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_scream_missing_text():
    """Test /scream command with missing text."""
    mock_message = MagicMock(spec=types.Message)
    mock_message.text = "/scream"
    mock_message.answer = AsyncMock()
    
    from innoscream.bot.handlers import handle_scream
    await handle_scream(mock_message)
    assert "Please provide text after /scream" in mock_message.answer.call_args[0][0]

# tests/unit/test_handlers.py
@pytest.mark.asyncio
async def test_handle_delete_unauthorized():
    """Test /delete command by non-admin."""
    mock_message = MagicMock(spec=types.Message)
    mock_message.from_user = MagicMock()  # Add this line
    mock_message.from_user.id = 123
    mock_message.answer = AsyncMock()
    
    with patch('innoscream.core.config.get_settings') as mock_settings:
        mock_settings.return_value.admin_ids = {456}
        from innoscream.bot.handlers import handle_delete
        await handle_delete(mock_message)
        mock_message.answer.assert_called_with("⛔️ Unauthorized")
