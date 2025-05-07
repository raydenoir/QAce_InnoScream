from unittest.mock import MagicMock, patch
import pytest

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