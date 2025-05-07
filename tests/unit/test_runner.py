# tests/unit/test_runner.py
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from aiogram import Bot, Dispatcher
import src.innoscream.bot.runner as runner
import importlib

@pytest.fixture(autouse=True)
def reset_runner_state():
    """Reset the runner's global state before each test."""
    runner._bot = None
    runner._dp = None

def test_get_bot_initialization():
    """Test that get_bot() initializes bot and dispatcher on first call."""
    with patch('src.innoscream.core.config.get_settings') as mock_settings:
        mock_settings.return_value.bot_token = "test_token"
        
        # First call should initialize
        bot = runner.get_bot()
        assert isinstance(bot, Bot)
        assert runner._dp is not None
        assert runner._bot is bot
        
        # Second call should return same instance
        assert runner.get_bot() is bot