from app.core.uow import UnitOfWork
from app.schemas.user import UserCreate, UserRead
from app.core.security import verify_password
from app.models.user import User
from app.core.codegen import generate_unique_user_code
from app.core.config import settings
from app.core.logging import logger
from app.schemas.websocket import WSMessageType
from app.core.websocket_manager import WebSocketManagerProtocol
from app.exceptions.base import (
    UserNotFound,
    UnknownAccessCode,
    EventNotFound,
    EventFull,
    UserAlreadyExistsInEvent,
    InvalidEventPassword,
    InvalidAdminDelete,
)


class UserService:
    def __init__(self, uow: UnitOfWork, ws_manager: WebSocketManagerProtocol):
        self.uow = uow
        self.ws_manager = ws_manager

    async def get_by_id(self, id: int) -> User:
        user = await self.uow.users.get_by_id(id)
        if not user:
            raise UserNotFound()
        return user

    async def get_by_access_code(self, access_code: str) -> User:
        user = await self.uow.users.get_by_access_code(access_code)
        if not user:
            logger.warning("Invalid access code", extra={"access_code_prefix": access_code[:8]})
            raise UnknownAccessCode()
        return user

    async def create_user(self, data: UserCreate) -> User:
        async with self.uow:
            data_dict = data.model_dump()
            event_code = data_dict.pop("event_code")
            event_password = data_dict.pop("event_password")

            event = await self.uow.events.get_by_code(event_code)
            if not event:
                raise EventNotFound()

            users_in_event = await self.uow.users.get_by_event_id(event.id)
            if len(users_in_event) >= settings.max_users_per_event:
                raise EventFull()

            if not verify_password(event_password, event.hashed_password):
                raise InvalidEventPassword()

            if await self.uow.users.get_by_username_and_event_id(data_dict["username"], event.id):
                raise UserAlreadyExistsInEvent()

            code = await generate_unique_user_code(self.uow)
            user = await self.uow.users.create(
                User(username=data_dict["username"], event_id=event.id, access_code=code)
            )
            logger.info("User created", extra={"user_id": user.id, "event_id": event.id})

        await self.ws_manager.broadcast_to_event(
            event.id,
            {
                "type": WSMessageType.USER_CREATED.value,
                "data": {"user": UserRead.model_validate(user).model_dump(mode="json")},
            },
        )
        return user

    async def delete_user(self, user: User) -> None:
        async with self.uow:
            event = await self.uow.events.get_by_id(user.event_id)
            if not event:
                raise EventNotFound()
            if event.admin_id == user.id:
                raise InvalidAdminDelete()
            await self.uow.users.delete(user)
            logger.info("User deleted", extra={"user_id": user.id, "event_id": user.event_id})

        await self.ws_manager.broadcast_to_event(
            user.event_id,
            {
                "type": WSMessageType.USER_DELETED.value,
                "data": {"user_id": user.id, "username": user.username},
            },
        )

    async def get_users_by_event_id(self, event_id: int) -> list[User]:
        return await self.uow.users.get_by_event_id(event_id)
