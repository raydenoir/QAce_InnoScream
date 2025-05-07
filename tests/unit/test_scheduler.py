import pytest
from innoscream.tasks.scheduler import start_scheduler, scheduler


@pytest.mark.asyncio
async def test_scheduler_registers_daily_job():
    scheduler.remove_all_jobs()
    start_scheduler()
    await asyncio.sleep(0)
    jobs = scheduler.get_jobs()
    assert any(job.func.__name__ == "post_daily_top" for job in jobs)
