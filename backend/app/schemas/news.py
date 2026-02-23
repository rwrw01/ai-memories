from datetime import datetime

from pydantic import BaseModel


# --- User-facing response models ---


class NewsArticleResponse(BaseModel):
    id: str
    source: str
    title: str
    url: str
    description: str | None
    audio_ready: bool
    audio_quality: str | None  # "parkiet" | "piper" | None
    published_at: datetime
    rendered_at: datetime | None


class NewsTodayResponse(BaseModel):
    date: str
    articles: list[NewsArticleResponse]
    total: int
    audio_ready_count: int


class NewsPreferencesRequest(BaseModel):
    feeds: list[str]
    max_articles: int = 20
    categories_exclude: list[str] = []


class NewsPreferencesResponse(BaseModel):
    feeds: list[str]
    max_articles: int
    categories_exclude: list[str]


# --- n8n ingest models ---


class NewsArticleCreate(BaseModel):
    source: str
    title: str
    url: str
    description: str = ""
    published_at: datetime
