from app.core.uow import UnitOfWork
from app.schemas.event import EventCreate, EventUpdate, EventCreateResponse, EventRead
from app.schemas.user import UserReadWithAccessCode
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

    async def create(self, data: EventCreate) -> EventCreateResponse:
        async with self.uow:
            hashed_password = hash_password(data.password)
            code = await generate_unique_event_code(self.uow)
            event = Event(name=data.name, max_responses=data.max_responses, hashed_password=hashed_password, code=code)
            event = await self.uow.events.store(event)

            access_code = await generate_unique_user_code(self.uow)
            admin_user = User(username=data.username, event_id=event.id, access_code=access_code)
            admin_user = await self.uow.users.store(admin_user)

            event.admin_id = admin_user.id
            event = await self.uow.events.store(event)

            logger.info("Event created", extra={"event_id": event.id, "admin_id": admin_user.id})
            return EventCreateResponse(
                event=EventRead.model_validate(event),
                user=UserReadWithAccessCode.model_validate(admin_user),
            )

    async def update(self, event: Event, data: EventUpdate) -> Event:
        async with self.uow:
            update_dict = data.model_dump(exclude_unset=True)
            if not update_dict:
                raise NoFieldsToUpdate()

            for key, value in update_dict.items():
                setattr(event, key, value)

            await self.uow.events.store(event)
            logger.info("Event updated", extra={"event_id": event.id, "updated_fields": list(update_dict.keys())})
            return event
