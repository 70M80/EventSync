from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_access_code(self, access_code: str) -> User | None:
        query = select(User).where(User.access_code == access_code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username_and_event_id(self, username: str, event_id: int) -> User | None:
        query = select(User).where(User.event_id == event_id).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_event_id(self, event_id: int) -> list[User]:
        query = select(User).where(User.event_id == event_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()
