import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.websocket_manager import WebSocketManagerProtocol, get_websocket_manager
from app.services.user_service import UserService
from app.dependencies.common import get_user_service
from app.core.logging import logger
from app.schemas.websocket import WSMessageType


router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_service: UserService = Depends(get_user_service),
    ws_manager: WebSocketManagerProtocol = Depends(get_websocket_manager),
):
    """
    WebSocket endpoint for real-time event updates.

    The connection is tied to the user's event, and they will receive
    updates when:
    - A new user joins the event
    - A user leaves the event
    - A new event response is created
    - An event response is deleted
    """

    access_code = websocket.cookies.get("access_code")
    await websocket.accept()
    logger.info(f"WebSocket accepted, access_code present: {bool(access_code)}")

    if not access_code:
        await websocket.close(code=4001, reason="Missing access_code")
        return

    user = await user_service.get_by_access_code(access_code)
    if not user:
        await websocket.close(code=4001, reason="Invalid or expired access code")
        return

    await ws_manager.connect(websocket, user.event_id, user.id)
    try:
        await websocket.send_json({"type": WSMessageType.AUTH_SUCCESS.value})
    except WebSocketDisconnect:
        return

    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=80.0)
                msg_type = data.get("type")
                if msg_type == "pong":
                    ws_manager.update_activity(websocket)
            except asyncio.TimeoutError:
                logger.info("WebSocket receive timeout", extra={"event_id": user.event_id})
                break
            except WebSocketDisconnect:
                logger.info("Client disconnected normally", extra={"event_id": user.event_id})
                break
            except Exception as e:
                logger.warning(f"WebSocket error: {e}", extra={"event_id": user.event_id})
                break
    finally:
        ws_manager.disconnect(websocket)
