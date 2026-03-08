import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())


class TimeSheet(Base):
    __tablename__ = "time_sheets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    datum: Mapped[date] = mapped_column(Date, default=date.today)
    source_text: Mapped[str] = mapped_column(Text)
    flow_execution_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)

    entries: Mapped[list["TimeEntry"]] = relationship(
        back_populates="time_sheet",
        cascade="all, delete-orphan",
        order_by="TimeEntry.start_tijd",
    )


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    time_sheet_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("time_sheets.id", ondelete="CASCADE")
    )
    start_tijd: Mapped[str] = mapped_column(String(5))
    eind_tijd: Mapped[str] = mapped_column(String(5))
    omschrijving: Mapped[str] = mapped_column(String(500))
    duur_minuten: Mapped[int] = mapped_column(Integer)

    time_sheet: Mapped["TimeSheet"] = relationship(back_populates="entries")
