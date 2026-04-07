from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.repositories.event_repository import EventRepository
from app.repositories.event_response_repository import EventResponseRepository


class UnitOfWork:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)
        self.events = EventRepository(db)
        self.event_responses = EventResponseRepository(db)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.db.rollback()
        else:
            await self.db.commit()
