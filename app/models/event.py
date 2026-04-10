from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, text
from app.core.session import Base
from app.models.mixins import TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .event_answer import EventAnswer


class Event(TimestampMixin, Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    max_responses: Mapped[int] = mapped_column(Integer, default=20, server_default=text("20"), nullable=False)  # user
    code: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    admin_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="event", cascade="all, delete-orphan", lazy="selectin"
    )
    event_answers: Mapped[list["EventAnswer"]] = relationship(
        "EventAnswer",
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
