from app.core.uow import UnitOfWork
from app.schemas.user import UserCreate
from app.core.security import verify_password
from app.models.user import User
from app.core.codegen import generate_unique_user_code


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_by_id(self, id: int) -> User:
        user = await self.uow.users.get_by_id(id)
        if not user:
            raise ValueError("User not found")
        return user

    async def get_by_access_code(self, access_code: str) -> User:
        user = await self.uow.users.get_by_access_code(access_code)
        if not user:
            raise ValueError("User not found")
        return user

    async def create_user(self, data: UserCreate) -> User:
        async with self.uow:
            data_dict = data.model_dump()
            event_code = data_dict.pop("event_code")
            event_password = data_dict.pop("event_password")

            event = await self.uow.events.get_by_code(event_code)
            if not event:
                raise ValueError("Event not found")

            if not verify_password(event_password, event.hashed_password):
                raise ValueError("Wrong password")

            if await self.uow.users.get_by_username_and_event_id(data_dict["username"], event.id):
                raise ValueError("User with that name already exists in event")

            # TODO: check max users per event

            code = await generate_unique_user_code(self.uow)
            user = await self.uow.users.create(
                User(username=data_dict["username"], event_id=event.id, access_code=code)
            )
            return user

    async def delete_user(self, user: User) -> None:
        async with self.uow:
            event = await self.uow.events.get_by_id(user.event_id)
            if not event:
                raise ValueError("Event not found")
            if event.admin_id == user.id:
                raise ValueError("Admin cannot remove themselves")
            await self.uow.users.delete(user)

    async def get_users_by_event_id(self, event_id: int) -> list[User]:
        return await self.uow.users.get_by_event_id(event_id)
