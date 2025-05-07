# tests/unit/test_analytics.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import datetime as dt
from src.innoscream.services.analytics import weekly_counts, chart_url

@pytest.mark.asyncio
async def test_weekly_counts_empty():
    """Test weekly_counts with no data."""
    with patch('src.innoscream.db.dao.get_db') as mock_db:
        mock_db.return_value.__aenter__.return_value.execute_fetchall.return_value = []
        result = await weekly_counts(dt.date(2023, 1, 1))
        assert result == [0, 0, 0, 0, 0, 0, 0]

@pytest.mark.asyncio
async def test_weekly_counts_with_data():
    """Test weekly_counts with sample data."""
    test_data = [("1", 5), ("3", 2), ("5", 7)]  # Mon=5, Wed=2, Fri=7
    with patch('src.innoscream.db.dao.get_db') as mock_db:
        mock_db.return_value.__aenter__.return_value.execute_fetchall.return_value = test_data
        result = await weekly_counts(dt.date(2023, 1, 1))
        assert result == [5, 0, 2, 0, 7, 0, 0]

@pytest.mark.asyncio
async def test_chart_url_success():
    """Test successful chart generation."""
    test_labels = ["Mon", "Tue"]
    test_data = [5, 3]
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "url": "https://quickchart.io/chart/123"}
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient.post', new=AsyncMock(return_value=mock_response)):
        result = await chart_url(test_labels, test_data)
        assert result == "https://quickchart.io/chart/123"

@pytest.mark.asyncio
async def test_chart_url_failure():
    """Test failed chart generation."""
    test_labels = ["Mon", "Tue"]
    test_data = [5, 3]
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": False}
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient.post', new=AsyncMock(return_value=mock_response)):
        result = await chart_url(test_labels, test_data)
        assert result is None