from innoscream.tasks.scheduler import start_scheduler, scheduler


def test_scheduler_registers_daily_job():
    scheduler.remove_all_jobs()
    start_scheduler()
    jobs = scheduler.get_jobs()
    assert any(job.name == "post_daily_top" or job.func.__name__ == "post_daily_top" for job in jobs)
