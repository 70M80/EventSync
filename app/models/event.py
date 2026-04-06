from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, text
from app.core.session import Base
from app.models.mixins import TimestampMixin
from app.models.user import User
from app.models.event_response import EventResponse


class Event(TimestampMixin, Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    max_responses: Mapped[int] = mapped_column(
        Integer, default=20, server_default=text("20"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    admin_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="event", cascade="all, delete-orphan", lazy="selectin"
    )
    event_responses: Mapped[list["EventResponse"]] = relationship(
        "EventResponse",
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
