import pytest
from aiogram import types
from unittest.mock import AsyncMock, MagicMock

from src.innoscream.telegram_ux.handlers import scream_command

@pytest.mark.asyncio
async def test_scream_command_valid():
    """Test /scream command with valid input"""
    message = AsyncMock()
    message.get_args.return_value = "Test scream text"
    message.from_user.id = 12345
    
    await scream_command(message)
    
    message.answer.assert_called_once()
    assert "Your scream has been heard" in message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_scream_command_empty():
    """Test /scream command with empty input"""
    message = AsyncMock()
    message.get_args.return_value = ""
    
    await scream_command(message)
    
    message.answer.assert_called_once()
    assert "Please provide your scream" in message.answer.call_args[0][0]