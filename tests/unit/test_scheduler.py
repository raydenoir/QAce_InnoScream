import pytest
from datetime import date, timedelta
from innoscream.tasks import scheduler as sched_mod


class DummyBot:
    async def send_photo(self, chat_id, url, caption): ...
    async def send_message(self, chat_id, text): ...


@pytest.mark.asyncio
async def test_post_daily_top_photo(monkeypatch):
    """If meme URL exists → bot.send_photo is called once."""
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("CHANNEL_ID", "123")

    yesterday = date.today() - timedelta(days=1)

    async def fake_get_top(d):
        return {"text": "hello", "votes": 10} if d == yesterday else None

    async def fake_generate(_):
        return "http://img"

    monkeypatch.setattr(sched_mod.scream, "get_top_daily", fake_get_top)
    monkeypatch.setattr(sched_mod.meme,  "generate_meme",  fake_generate)

    called = {}

    async def fake_send_photo(chat_id, url, caption):
        called["photo"] = (chat_id, url, caption)

    dummy = DummyBot()
    monkeypatch.setattr(dummy, "send_photo", fake_send_photo)
    monkeypatch.setattr(sched_mod, "get_bot", lambda: dummy)

    await sched_mod.post_daily_top()

    assert "photo" in called
    assert called["photo"][1] == "http://img"


@pytest.mark.asyncio
async def test_post_daily_top_text(monkeypatch):
    """If meme URL is None → bot.send_message is called."""
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("CHANNEL_ID", "123")

    async def fake_get_top(_):
        return {"text": "hello", "votes": 10}

    async def fake_generate(_):
        return None

    monkeypatch.setattr(sched_mod.scream, "get_top_daily", fake_get_top)
    monkeypatch.setattr(sched_mod.meme,  "generate_meme",  fake_generate)

    called = {}

    async def fake_send_message(chat_id, text):
        called["msg"] = (chat_id, text)

    dummy = DummyBot()
    monkeypatch.setattr(dummy, "send_message", fake_send_message)
    monkeypatch.setattr(sched_mod, "get_bot", lambda: dummy)

    await sched_mod.post_daily_top()

    assert "msg" in called
    assert "hello" in called["msg"][1]


def test_start_scheduler_registers_job(monkeypatch):
    """start_scheduler should register exactly one job."""
    test_sched = sched_mod.AsyncIOScheduler()
    monkeypatch.setattr(sched_mod, "scheduler", test_sched)
    monkeypatch.setattr(test_sched, "start", lambda: None)

    sched_mod.start_scheduler()

    jobs = test_sched.get_jobs()
    assert len(jobs) == 2
    assert jobs[0].func == sched_mod.post_daily_top