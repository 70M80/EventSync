from fastapi import APIRouter, Depends, status
from app.schemas.event_response import (
    EventResponseCreate,
    EventResponseRead,
    EventResponsesRead,
    EventResponseResult,
)
from app.services.event_response_service import EventResponseService
from app.dependencies.event_response import (
    get_event_response_service,
    get_authorized_event_response,
)
from app.models.user import User
from app.models.event_response import EventResponse
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/event_responses", tags=["event_responses"])


@router.get("/", response_model=EventResponsesRead)
async def get_event_responses(
    current_user: User = Depends(get_current_user),
    event_response_service: EventResponseService = Depends(get_event_response_service),
):
    event_responses = await event_response_service.get_event_responses_by_event_id(current_user.event_id)
    event_response_reads = [EventResponseRead.model_validate(p) for p in event_responses]

    return EventResponsesRead(event_responses=event_response_reads)


@router.post("/", response_model=EventResponseResult, status_code=status.HTTP_201_CREATED)
async def create_event_response(
    data: EventResponseCreate,
    current_user: User = Depends(get_current_user),
    event_response_service: EventResponseService = Depends(get_event_response_service),
):
    return await event_response_service.create_event_response(data, current_user)


@router.delete("/{event_response_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_response(
    event_response: EventResponse = Depends(get_authorized_event_response),
    event_response_service: EventResponseService = Depends(get_event_response_service),
):
    await event_response_service.delete_event_response(event_response)
