from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import select

from app.database import async_session
from app.models.news import NewsArticle
from app.schemas.news import NewsArticleCreate
from app.services.news_service import create_article, save_audio

router = APIRouter(prefix="/api/news/ingest")


@router.post("/article")
async def ingest_article(data: NewsArticleCreate) -> dict:
    """Create a new news article. Called by n8n after RSS fetch."""
    async with async_session() as session:
        # Check for duplicate URL
        stmt = select(NewsArticle).where(NewsArticle.url == data.url)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return {"id": existing.id, "duplicate": True}

        article = await create_article(
            session,
            source=data.source,
            title=data.title,
            url=data.url,
            description=data.description,
            published_at=data.published_at,
        )
        return {"id": article.id, "duplicate": False}


@router.post("/article/{article_id}/audio")
async def upload_audio(article_id: str, engine: str, file: UploadFile) -> dict:
    """Upload rendered MP3 audio. Called by n8n after TTS."""
    if engine not in ("piper", "parkiet"):
        raise HTTPException(status_code=400, detail="engine must be 'piper' or 'parkiet'")

    async with async_session() as session:
        stmt = select(NewsArticle).where(NewsArticle.id == article_id)
        result = await session.execute(stmt)
        article = result.scalar_one_or_none()
        if not article:
            raise HTTPException(status_code=404, detail="Artikel niet gevonden")

        audio_bytes = await file.read()
        rel_path = await save_audio(article_id, engine, audio_bytes)

        if engine == "piper":
            article.audio_piper = rel_path
        else:
            article.audio_parkiet = rel_path
        article.rendered_at = datetime.now(timezone.utc)
        await session.commit()
        return {"status": "ok", "path": rel_path}
