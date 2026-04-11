from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.event_answer import EventAnswer


class EventAnswerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, event_answer: EventAnswer) -> EventAnswer:
        self.db.add(event_answer)
        await self.db.flush()
        await self.db.refresh(event_answer)
        return event_answer

    async def get_by_id(self, event_answer_id: int) -> EventAnswer | None:
        query = select(EventAnswer).where(EventAnswer.id == event_answer_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_event_id(self, event_id: int) -> list[EventAnswer]:
        query = select(EventAnswer).where(EventAnswer.event_id == event_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: int) -> list[EventAnswer]:
        query = select(EventAnswer).where(EventAnswer.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_user_id_for_update(self, user_id: int) -> list[EventAnswer]:
        query = select(EventAnswer).where(EventAnswer.user_id == user_id).with_for_update()
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete(self, event_answer: EventAnswer) -> None:
        await self.db.delete(event_answer)
        await self.db.flush()
