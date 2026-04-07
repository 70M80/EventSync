from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.event_response import EventResponse


class EventResponseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, event_response: EventResponse) -> EventResponse:
        self.db.add(event_response)
        await self.db.flush()
        await self.db.refresh(event_response)
        return event_response

    async def get_by_id(self, event_response_id: int) -> EventResponse | None:
        query = select(EventResponse).where(EventResponse.id == event_response_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_event_id(self, event_id: int) -> list[EventResponse]:
        query = select(EventResponse).where(EventResponse.event_id == event_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete(self, event_response: EventResponse) -> None:
        await self.db.delete(event_response)
        await self.db.flush()
