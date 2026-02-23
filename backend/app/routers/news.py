import json
from datetime import date

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.database import async_session
from app.schemas.news import (
    NewsArticleResponse,
    NewsPreferencesRequest,
    NewsPreferencesResponse,
    NewsTodayResponse,
)
from app.services.news_service import (
    get_audio_path,
    get_preferences,
    get_today_articles,
    update_preferences,
)

router = APIRouter()


@router.get("/api/news/today", response_model=NewsTodayResponse)
async def news_today() -> NewsTodayResponse:
    """List today's news articles with audio status."""
    async with async_session() as session:
        articles = await get_today_articles(session)

    items = []
    for a in articles:
        audio_quality = None
        if a.audio_parkiet:
            audio_quality = "parkiet"
        elif a.audio_piper:
            audio_quality = "piper"

        items.append(
            NewsArticleResponse(
                id=a.id,
                source=a.source,
                title=a.title,
                url=a.url,
                description=a.description,
                audio_ready=audio_quality is not None,
                audio_quality=audio_quality,
                published_at=a.published_at,
                rendered_at=a.rendered_at,
            )
        )

    return NewsTodayResponse(
        date=date.today().isoformat(),
        articles=items,
        total=len(items),
        audio_ready_count=sum(1 for i in items if i.audio_ready),
    )


@router.get("/api/news/{article_id}/audio")
async def news_audio(article_id: str) -> FileResponse:
    """Stream the best available audio for a news article."""
    async with async_session() as session:
        path = await get_audio_path(session, article_id)

    if not path:
        raise HTTPException(status_code=404, detail="Audio niet beschikbaar")

    return FileResponse(
        path=str(path),
        media_type="audio/mpeg",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.put("/api/news/preferences", response_model=NewsPreferencesResponse)
async def put_preferences(req: NewsPreferencesRequest) -> NewsPreferencesResponse:
    """Update news feed preferences."""
    async with async_session() as session:
        prefs = await update_preferences(
            session, req.feeds, req.max_articles, req.categories_exclude
        )
        return NewsPreferencesResponse(
            feeds=json.loads(prefs.feeds),
            max_articles=prefs.max_articles,
            categories_exclude=json.loads(prefs.categories_exclude),
        )


@router.get("/api/news/preferences", response_model=NewsPreferencesResponse)
async def get_news_preferences() -> NewsPreferencesResponse:
    """Get current news feed preferences."""
    async with async_session() as session:
        prefs = await get_preferences(session)
        return NewsPreferencesResponse(
            feeds=json.loads(prefs.feeds),
            max_articles=prefs.max_articles,
            categories_exclude=json.loads(prefs.categories_exclude),
        )


@router.post("/api/news/refresh")
async def news_refresh() -> dict:
    """Trigger the n8n news-briefing workflow via webhook."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post("http://n8n:5678/webhook/news-refresh")
            resp.raise_for_status()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="n8n niet beschikbaar")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="n8n webhook mislukt")
    return {"status": "ok", "message": "News refresh triggered"}
