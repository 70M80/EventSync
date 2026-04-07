from fastapi import Depends
from app.services.event_service import EventService
from app.dependencies.auth import get_current_user
from app.dependencies.common import get_event_service
from app.models.user import User


async def get_admin_event(
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
):
    """Get the current user's event and return it if the user is an administrator"""
    event = await event_service.get_by_id(current_user.event_id)
    if event.admin_id != current_user.id:
        raise ValueError("Permission denied")

    return event


async def get_authorized_event(
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
):
    """Get the current user's event"""
    return await event_service.get_by_id(current_user.event_id)
