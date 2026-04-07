from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session import get_db
from app.core.uow import UnitOfWork
from app.services.event_response_service import EventResponseService
from app.services.event_service import EventService
from app.services.user_service import UserService


def get_uow(db: AsyncSession = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(db)


def get_user_service(uow: UnitOfWork = Depends(get_uow)) -> UserService:
    return UserService(uow)


def get_event_service(uow: UnitOfWork = Depends(get_uow)) -> EventService:
    return EventService(uow)


def get_event_response_service(uow: UnitOfWork = Depends(get_uow)) -> EventResponseService:
    return EventResponseService(uow)
