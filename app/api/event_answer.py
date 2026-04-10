from fastapi import APIRouter, Depends, status
from app.schemas.event_answer import (
    EventAnswerCreate,
    EventAnswerRead,
    EventAnswersRead,
    EventAnswerResult,
)
from app.services.event_answer_service import EventAnswerService
from app.dependencies.event_answer import (
    get_event_answer_service,
    get_authorized_event_answer,
)
from app.models.user import User
from app.models.event_answer import EventAnswer
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/event_answers", tags=["event_answers"])


@router.get("/", response_model=EventAnswersRead)
async def get_event_answers(
    current_user: User = Depends(get_current_user),
    event_answer_service: EventAnswerService = Depends(get_event_answer_service),
):
    event_answers = await event_answer_service.get_event_answers_by_event_id(current_user.event_id)
    event_answer_reads = [EventAnswerRead.model_validate(p) for p in event_answers]

    return EventAnswersRead(event_answers=event_answer_reads)


@router.post("/", response_model=EventAnswerResult, status_code=status.HTTP_201_CREATED)
async def create_event_answer(
    data: EventAnswerCreate,
    current_user: User = Depends(get_current_user),
    event_answer_service: EventAnswerService = Depends(get_event_answer_service),
):
    return await event_answer_service.create_event_answer(data, current_user)


@router.delete("/{event_answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_answer(
    event_answer: EventAnswer = Depends(get_authorized_event_answer),
    event_answer_service: EventAnswerService = Depends(get_event_answer_service),
):
    await event_answer_service.delete_event_answer(event_answer)
