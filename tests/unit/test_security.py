import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
@patch("innoscream.tasks.scheduler.scheduler", new_callable=MagicMock)
def test_scheduler_registers_daily_job(mock_scheduler):
    from innoscream.tasks.scheduler import start_scheduler

    start_scheduler()

    # Check that a job was added
    mock_scheduler.add_job.assert_called_once()
    mock_scheduler.start.assert_called_once()
