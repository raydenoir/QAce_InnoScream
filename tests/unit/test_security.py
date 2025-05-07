import pytest
from innoscream.services.security import hash_user_id


@pytest.fixture(autouse=True)
def patch_required_env(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "dummy")
    monkeypatch.setenv("CHANNEL_ID", "123")
    monkeypatch.setenv("HASH_SALT", "test-salt")


def test_hash_user_id_is_consistent():
    user_id = 123
    hashed1 = hash_user_id(user_id)
    hashed2 = hash_user_id(user_id)
    assert hashed1 == hashed2
    assert isinstance(hashed1, str)
    assert len(hashed1) == 64
