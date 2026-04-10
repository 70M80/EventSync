from __future__ import annotations
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Date
from app.core.session import Base
from app.models.mixins import TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .event import Event


class EventAnswer(TimestampMixin, Base):
    __tablename__ = "event_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="event_answers", lazy="selectin")
    user: Mapped["User"] = relationship("User", back_populates="event_answers", lazy="selectin")
