from app.core.uow import UnitOfWork
from app.schemas.event_answer import EventAnswerCreate, EventAnswerRead, EventAnswerResult
from app.models.event_answer import EventAnswer
from app.models.user import User
from app.core.logging import logger
from app.schemas.websocket import WSMessageType
from app.exceptions.base import EventNotFound, EventAnswerNotFound, MaximumEventAnswersReached
from app.core.websocket_manager import WebSocketManagerProtocol
from datetime import date
from datetime import timedelta


class EventAnswerService:
    def __init__(self, uow: UnitOfWork, ws_manager: WebSocketManagerProtocol):
        self.uow = uow
        self.ws_manager = ws_manager

    async def get_by_id(self, event_answer_id: int) -> EventAnswer:
        event_answer = await self.uow.event_answers.get_by_id(event_answer_id)
        if not event_answer:
            raise EventAnswerNotFound()
        return event_answer

    async def create_event_answer(self, data: EventAnswerCreate, user: User) -> EventAnswerResult:
        async with self.uow:
            user_responses = await self.uow.event_answers.get_by_user_id_for_update(user.id)
            event = await self.uow.events.get_by_id(user.event_id)
            if not event:
                raise EventNotFound()

            final_start, final_end, to_delete = self._merge_intervals(user_responses, data.date_from, data.date_to)

            deleted_responses = []
            # delete old overlapping records
            for r in to_delete:
                await self.uow.event_answers.delete(r)
                deleted_responses.append(r)

            # enforce limit AFTER merge
            remaining_count = len(user_responses) - len(to_delete)
            if remaining_count >= event.max_responses:
                raise MaximumEventAnswersReached()

            # create new merged response
            event_answer = EventAnswer(
                date_from=final_start,
                date_to=final_end,
                user_id=user.id,
                event_id=user.event_id,
            )

            created_event_answer = await self.uow.event_answers.create(event_answer)

        await self.ws_manager.broadcast_to_event(
            user.event_id,
            {
                "type": WSMessageType.EVENT_ANSWER_CREATED.value,
                "data": {
                    "event_answer": EventAnswerRead.model_validate(created_event_answer).model_dump(mode="json"),
                    "username": user.username,
                },
            },
        )

        for r in deleted_responses:
            await self.ws_manager.broadcast_to_event(
                user.event_id,
                {
                    "type": WSMessageType.EVENT_ANSWER_DELETED.value,
                    "data": {
                        "event_answer_id": r.id,
                        "user_id": r.user_id,
                    },
                },
            )
        deleted_ids = [deleted_response.id for deleted_response in deleted_responses]

        return EventAnswerResult(
            event_answer=EventAnswerRead.model_validate(created_event_answer), deleted_ids=deleted_ids
        )

    async def delete_event_answer(self, event_answer: EventAnswer) -> None:
        async with self.uow:
            await self.uow.event_answers.delete(event_answer)
            logger.info("Event response deleted", extra={"event_answer_id": event_answer.id})

        await self.ws_manager.broadcast_to_event(
            event_answer.event_id,
            {
                "type": WSMessageType.EVENT_ANSWER_DELETED.value,
                "data": {"event_answer_id": event_answer.id, "user_id": event_answer.user_id},
            },
        )

    async def get_event_answers_by_event_id(self, event_id: int) -> list[EventAnswer]:
        event_answers = await self.uow.event_answers.get_by_event_id(event_id)
        return event_answers

    def _merge_intervals(
        self, existing: list[EventAnswer], new_start: date, new_end: date
    ) -> tuple[date, date, list[EventAnswer]]:
        """
        Merges the newly requested interval with all existing intervals that overlap
        or are adjacent (touching) to it.

        Logic:
            1. Start with the new interval as the base merged range.
            2. For every existing response:
            - If it overlaps or touches the current merged range → expand the range
                to cover both and mark the old response for deletion.
            3. Return the final merged range + list of responses that need to be deleted.

        Why + timedelta(days=1)?
            Because we want to merge adjacent days (e.g. 5-10 and 11-15 → should become 5-15).
        """
        if not existing:
            return new_start, new_end, []

        min_start = new_start
        max_end = new_end
        to_delete: list[EventAnswer] = []

        for resp in existing:
            # Check for overlap or adjacency (including touching at the boundary)
            if resp.date_from <= max_end + timedelta(days=1) and resp.date_to >= min_start - timedelta(days=1):
                min_start = min(min_start, resp.date_from)
                max_end = max(max_end, resp.date_to)
                to_delete.append(resp)

        return min_start, max_end, to_delete
