from fastapi import APIRouter, Depends, status
from app.schemas.event import EventCreate, EventCreateResponse, EventRead, EventUpdate
from app.schemas.user import UserReadWithAccessCode
from app.services.event_service import EventService
from app.dependencies.event import (
    get_event_service,
    get_authorized_event,
    get_admin_event,
)
from app.models.event import Event

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: EventCreate,
    event_service: EventService = Depends(get_event_service),
):
    event, user = await event_service.create_event(data)
    return EventCreateResponse(
        event=EventRead.model_validate(event),
        user=UserReadWithAccessCode.model_validate(user),
    )


@router.get("/", response_model=EventRead)
async def get_event(event: Event = Depends(get_authorized_event)):
    return event


@router.patch("/", response_model=EventRead)
async def update_event(
    data: EventUpdate,
    event: Event = Depends(get_admin_event),
    event_service: EventService = Depends(get_event_service),
):
    return await event_service.update_event(event, data)
