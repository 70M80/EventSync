from app.core.uow import UnitOfWork
from app.schemas.event_response import EventResponseCreate
from app.models.event_response import EventResponse
from app.models.user import User


class EventResponseService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_by_id(self, event_response_id: int) -> EventResponse:
        event_response = await self.uow.event_responses.get_by_id(event_response_id)
        if not event_response:
            raise ValueError("EventResponse not found")
        return event_response

    async def create_event_response(self, data: EventResponseCreate, user: User) -> EventResponse:
        async with self.uow:
            # TODO: check max reponses per user
            # TODO: check overlap with existing user responses and merge if needed
            # If there is an overlap, update the existing response here.
            # On FE, it always checks whether an response with that ID already exists and updates it as needed.
            event_response = EventResponse(**data.model_dump(), user_id=user.id, event_id=user.event_id)
            created_event_response = await self.uow.event_responses.create(event_response)
            return created_event_response

    async def delete_event_response(self, event_response: EventResponse) -> None:
        async with self.uow:
            await self.uow.event_responses.delete(event_response)

    async def get_event_responses_by_event_id(self, event_id: int) -> list[EventResponse]:
        event_responses = await self.uow.event_responses.get_by_event_id(event_id)
        return event_responses
