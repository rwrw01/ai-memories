import json
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import NewsArticle, NewsPreferences

AUDIO_BASE = Path("/data/audio/news")


async def get_today_articles(session: AsyncSession) -> list[NewsArticle]:
    """Get all news articles created today, newest first."""
    today = date.today().isoformat()
    stmt = (
        select(NewsArticle)
        .where(NewsArticle.created_at >= datetime.fromisoformat(f"{today}T00:00:00"))
        .order_by(NewsArticle.published_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_audio_path(session: AsyncSession, article_id: str) -> Path | None:
    """Resolve the best available audio file for an article (parkiet > piper)."""
    stmt = select(NewsArticle).where(NewsArticle.id == article_id)
    result = await session.execute(stmt)
    article = result.scalar_one_or_none()
    if not article:
        return None

    rel_path = article.audio_parkiet or article.audio_piper
    if not rel_path:
        return None

    full_path = AUDIO_BASE / rel_path
    if not full_path.exists():
        return None
    return full_path


async def create_article(
    session: AsyncSession,
    source: str,
    title: str,
    url: str,
    published_at: datetime,
    description: str = "",
) -> NewsArticle:
    """Create a new news article. Caller must handle duplicate URL check."""
    article = NewsArticle(
        source=source,
        title=title,
        url=url,
        description=description,
        published_at=published_at,
    )
    session.add(article)
    await session.commit()
    await session.refresh(article)
    return article


async def save_audio(article_id: str, engine: str, audio_bytes: bytes) -> str:
    """Save MP3 audio to disk. Returns the relative path."""
    today = date.today().isoformat()
    rel_path = f"{today}/{article_id}_{engine}.mp3"
    full_path = AUDIO_BASE / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(audio_bytes)
    return rel_path


async def get_preferences(session: AsyncSession) -> NewsPreferences:
    """Get or create the single preferences row (id=1)."""
    stmt = select(NewsPreferences).where(NewsPreferences.id == 1)
    result = await session.execute(stmt)
    prefs = result.scalar_one_or_none()
    if not prefs:
        prefs = NewsPreferences(id=1)
        session.add(prefs)
        await session.commit()
        await session.refresh(prefs)
    return prefs


async def update_preferences(
    session: AsyncSession,
    feeds: list[str],
    max_articles: int,
    categories_exclude: list[str],
) -> NewsPreferences:
    """Update the single preferences row."""
    prefs = await get_preferences(session)
    prefs.feeds = json.dumps(feeds)
    prefs.max_articles = max_articles
    prefs.categories_exclude = json.dumps(categories_exclude)
    await session.commit()
    await session.refresh(prefs)
    return prefs
