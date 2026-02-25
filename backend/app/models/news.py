import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    source: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(2000), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_piper: Mapped[str | None] = mapped_column(String(500), nullable=True)
    audio_parkiet: Mapped[str | None] = mapped_column(String(500), nullable=True)
    published_at: Mapped[datetime] = mapped_column()
    rendered_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)


class NewsPreferences(Base):
    __tablename__ = "news_preferences"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    feeds: Mapped[str] = mapped_column(
        Text,
        default='["https://feeds.nos.nl/nosnieuwsalgemeen","https://www.nu.nl/rss/Algemeen","https://tweakers.net/feeds/mixed.xml"]',
    )
    max_articles: Mapped[int] = mapped_column(default=20)
    categories_exclude: Mapped[str] = mapped_column(Text, default="[]")
