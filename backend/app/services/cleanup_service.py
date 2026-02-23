import asyncio
import logging
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import delete

from app.database import async_session
from app.models.news import NewsArticle

logger = logging.getLogger(__name__)

AUDIO_BASE = Path("/data/audio/news")
RETENTION_DAYS = 7


async def cleanup_old_news() -> None:
    """Delete news articles and audio files older than RETENTION_DAYS."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)

    # Delete old DB records
    async with async_session() as session:
        result = await session.execute(
            delete(NewsArticle).where(NewsArticle.created_at < cutoff)
        )
        count = result.rowcount
        await session.commit()
        if count:
            logger.info("Cleaned up %d old news articles from database", count)

    # Delete old date directories
    if not AUDIO_BASE.exists():
        return

    for date_dir in AUDIO_BASE.iterdir():
        if not date_dir.is_dir():
            continue
        try:
            dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            if dir_date < cutoff:
                shutil.rmtree(date_dir)
                logger.info("Deleted old audio directory: %s", date_dir.name)
        except ValueError:
            pass  # skip non-date directories


async def daily_cleanup_loop() -> None:
    """Run cleanup once per day. Call as a background task in lifespan."""
    while True:
        await asyncio.sleep(86400)  # 24 hours
        try:
            await cleanup_old_news()
        except Exception:
            logger.exception("Cleanup failed")
