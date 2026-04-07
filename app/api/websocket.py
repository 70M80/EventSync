from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from app.core.websocket_manager import WebSocketManagerProtocol, get_websocket_manager
from app.services.user_service import UserService
from app.dependencies.common import get_user_service
from app.core.logging import logger


router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    access_code: str = Query(...),
    user_service: UserService = Depends(get_user_service),
    ws_manager: WebSocketManagerProtocol = Depends(get_websocket_manager),
):
    """
    WebSocket endpoint for real-time event updates.

    Connect with: ws://host/ws?access_code=ACCESS_CODE

    The connection is tied to the user's event, and they will receive
    updates when:
    - A new user joins the event
    - A user leaves the event
    - A new event response is created
    - An event response is deleted
    """

    user = await user_service.get_by_access_code(access_code)
    event_id = user.event_id

    await ws_manager.connect(websocket, event_id)

    try:
        while True:
            try:
                data = await websocket.receive_json()
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.warning(f"Receive error: {e}")
                break

    finally:
        ws_manager.disconnect(websocket, event_id)
