from typing import Any, Mapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.event import Event


class EventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, event: Event) -> Event:
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def get_by_id(self, event_id: int) -> Event | None:
        query = select(Event).where(Event.id == event_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: int) -> Event | None:
        query = select(Event).where(Event.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, event: Event, update_data: Mapping[str, Any]) -> Event:
        """
        Updates Event entity with partial data.
        None values will be saved as NULL in the database.
        """
        for key, value in update_data.items():
            setattr(event, key, value)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def delete(self, event: Event) -> None:
        await self.db.delete(event)
        await self.db.flush()
