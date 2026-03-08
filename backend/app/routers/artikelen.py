from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database import async_session
from app.models.article import Article

router = APIRouter()


@router.get("/api/artikelen")
async def list_articles() -> list[dict]:
    """List all articles, newest first."""
    async with async_session() as session:
        stmt = select(Article).order_by(Article.created_at.desc())
        result = await session.execute(stmt)
        articles = result.scalars().all()
        return [
            {
                "id": a.id,
                "title": a.title,
                "created_at": a.created_at.isoformat(),
            }
            for a in articles
        ]


@router.get("/api/artikelen/{article_id}")
async def get_article(article_id: str) -> dict:
    """Get a single article with full content."""
    async with async_session() as session:
        stmt = select(Article).where(Article.id == article_id)
        result = await session.execute(stmt)
        article = result.scalar_one_or_none()
        if not article:
            raise HTTPException(status_code=404, detail="Artikel niet gevonden")
        return {
            "id": article.id,
            "title": article.title,
            "content": article.content,
            "source_text": article.source_text,
            "created_at": article.created_at.isoformat(),
        }
