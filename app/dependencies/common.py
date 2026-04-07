from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session import get_db
from app.core.uow import UnitOfWork
from app.services.event_response_service import EventResponseService
from app.services.event_service import EventService
from app.services.user_service import UserService
from app.core.websocket_manager import WebSocketManagerProtocol, get_websocket_manager


def get_uow(db: AsyncSession = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(db)


def get_user_service(
    uow: UnitOfWork = Depends(get_uow),
    ws_manager: WebSocketManagerProtocol = Depends(get_websocket_manager),
) -> UserService:
    return UserService(uow, ws_manager=ws_manager)


def get_event_service(uow: UnitOfWork = Depends(get_uow)) -> EventService:
    return EventService(uow)


def get_event_response_service(
    uow: UnitOfWork = Depends(get_uow),
    ws_manager: WebSocketManagerProtocol = Depends(get_websocket_manager),
) -> EventResponseService:
    return EventResponseService(uow, ws_manager=ws_manager)
