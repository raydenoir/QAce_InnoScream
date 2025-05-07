"""
QuickChart graph generator + helpers to pull weekly counts.
"""
import httpx, logging, datetime as dt
from typing import List, Optional
from ..db import dao

logger = logging.getLogger(__name__)
_QC_URL = "https://quickchart.io/chart/create"


async def weekly_counts(start: dt.date) -> List[int]:
    """Return list[7] of scream counts Mon‑Sun starting at `start`."""
    async with dao.get_db() as db:
        rows = await db.execute_fetchall(
            """
            SELECT strftime('%w', created_at) AS dow, COUNT(*)
            FROM posts
            WHERE is_deleted = 0
                AND date(created_at) BETWEEN ? AND ?
            GROUP BY dow
            """,
            (start.isoformat(), (start + dt.timedelta(days=6)).isoformat()),
        )
    mapping = {int(dow): n for dow, n in rows}
    return [mapping.get(i, 0) for i in range(1, 8)]  # Mon=1…Sun=7


async def chart_url(labels: List[str], data: List[int]) -> Optional[str]:
    """Generates a chart URL from provided data using QuickChart service.

        Args:
            labels: list of label strings for the X-axis
            data: list of integer values for the Y-axis dataset

        Returns:
            URL string of the generated chart if successful, None otherwise

        Raises:
            httpx.HTTPStatusError: if the chart generation request fails
    """
    cfg = {
        "type": "line",
        "data": {"labels": labels, "datasets": [{"label": "Screams", "data": data}]},
        "options": {"responsive": True},
    }
    async with httpx.AsyncClient() as c:
        r = await c.post(_QC_URL, json={"chart": cfg, "backgroundColor": "white"})
        r.raise_for_status()
    jd = r.json()
    return jd["url"] if jd.get("success") else None
