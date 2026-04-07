from typing import Annotated
from fastapi import Depends, Path
from app.services.event_response_service import EventResponseService
from app.dependencies.common import get_event_response_service
from app.dependencies.auth import get_current_user
from app.models.user import User


async def get_authorized_event_response(
    event_response_id: Annotated[int, Path(gt=0)],
    current_user: User = Depends(get_current_user),
    event_response_service: EventResponseService = Depends(get_event_response_service),
):
    event_response = await event_response_service.get_by_id(event_response_id)

    if event_response.user_id != current_user.id:
        raise ValueError("Permission denied")

    return event_response
