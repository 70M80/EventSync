from app.core.uow import UnitOfWork
from app.schemas.event import EventCreate, EventUpdate
from app.models.event import Event
from app.models.user import User
from app.core.security import hash_password
from app.core.codegen import generate_unique_user_code, generate_unique_event_code
from app.core.logging import logger
from app.exceptions.base import EventNotFound, NoFieldsToUpdate


class EventService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_by_id(self, event_id: int) -> Event:
        event = await self.uow.events.get_by_id(event_id)
        if not event:
            raise EventNotFound()
        return event

    async def create_event(self, data: EventCreate) -> tuple[Event, User]:
        async with self.uow:
            data_dict = data.model_dump()
            username = data_dict.pop("username")
            data_dict["hashed_password"] = hash_password(data_dict["password"])
            data_dict.pop("password")

            code = await generate_unique_event_code(self.uow)
            data_dict["code"] = code
            event = Event(**data_dict)
            created_event = await self.uow.events.create(event)

            access_code = await generate_unique_user_code(self.uow)

            user = await self.uow.users.create(
                User(
                    username=username,
                    event_id=created_event.id,
                    access_code=access_code,
                )
            )

            event_with_admin_id = await self.uow.events.update(created_event, {"admin_id": user.id})
            logger.info("Event created", extra={"event_id": event_with_admin_id.id, "admin_id": user.id})
            return event_with_admin_id, user

    async def update_event(self, event: Event, data: EventUpdate) -> Event:
        async with self.uow:
            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                raise NoFieldsToUpdate()

            updated_event = await self.uow.events.update(event, update_data)
            logger.info("Event updated", extra={"event_id": event.id, "updated_fields": list(update_data.keys())})
            return updated_event
