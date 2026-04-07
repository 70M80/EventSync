from typing import Annotated
from fastapi import Depends, Path
from app.services.user_service import UserService
from app.services.event_service import EventService
from app.dependencies.auth import get_current_user
from app.dependencies.common import get_user_service
from app.dependencies.common import get_event_service
from app.models.user import User


async def get_authorized_user(
    user_id: Annotated[int, Path(gt=0)],
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Only event admin can manipulate with users in event"""

    # check if current user is admin in his event
    event = await event_service.get_by_id(current_user.event_id)
    if event.admin_id != current_user.id:
        raise ValueError("Permission denied")

    # check if user that we want get is in same event as current user(admin)
    user = await user_service.get_by_id(user_id)
    if user.event_id != event.id:
        raise ValueError("Permission denied")

    return user
