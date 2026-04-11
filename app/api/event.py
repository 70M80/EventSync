from fastapi import APIRouter, Depends, status, Request
from app.schemas.event import EventCreate, EventCreateResponse, EventRead, EventUpdate
from app.schemas.user import UserReadWithAccessCode
from app.services.event_service import EventService
from app.dependencies.event import (
    get_event_service,
    get_authorized_event,
    get_admin_event,
)
from app.models.event import Event
from app.main import limiter

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventCreateResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("2/minute")
async def create_event(
    request: Request,
    data: EventCreate,
    event_service: EventService = Depends(get_event_service),
):
    event, user = await event_service.create_event(data)
    return EventCreateResponse(
        event=EventRead.model_validate(event),
        user=UserReadWithAccessCode.model_validate(user),
    )


@router.get("/", response_model=EventRead)
@limiter.limit("10/minute")
async def get_event(request: Request, event: Event = Depends(get_authorized_event)):
    return event


@router.patch("/", response_model=EventRead)
@limiter.limit("5/minute")
async def update_event(
    request: Request,
    data: EventUpdate,
    event: Event = Depends(get_admin_event),
    event_service: EventService = Depends(get_event_service),
):
    return await event_service.update_event(event, data)
