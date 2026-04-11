from typing import Annotated
from fastapi import Depends, Path
from app.services.event_answer_service import EventAnswerService
from app.dependencies.common import get_event_answer_service
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.exceptions.base import PermissionDenied


async def get_authorized_event_answer(
    event_answer_id: Annotated[int, Path(gt=0)],
    current_user: User = Depends(get_current_user),
    event_answer_service: EventAnswerService = Depends(get_event_answer_service),
):
    event_answer = await event_answer_service.get_by_id(event_answer_id)

    if event_answer.user_id != current_user.id or event_answer.event_id != current_user.event_id:
        raise PermissionDenied()

    return event_answer
