from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from app.core.session import Base
from app.models.mixins import TimestampMixin
from app.models.event import Event
from app.models.event_response import EventResponse


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), index=True
    )
    username: Mapped[str] = mapped_column(String(20), nullable=False)
    access_code: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)

    # Relationships
    event: Mapped["Event"] = relationship(
        "Event", back_populates="users", lazy="selectin"
    )
    event_responses: Mapped[list["EventResponse"]] = relationship(
        "EventResponse",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
