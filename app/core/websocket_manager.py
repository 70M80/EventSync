import asyncio
from typing import Dict, Set, Protocol
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
from app.core.logging import logger


################################
#### PROTOCOL (INTERFACE) #####
################################
class WebSocketManagerProtocol(Protocol):
    async def connect(self, websocket: WebSocket, event_id: int) -> None: ...
    def disconnect(self, websocket: WebSocket, event_id: int) -> None: ...
    async def broadcast_to_event(self, event_id: int, message: dict) -> None: ...
    def get_connection_count(self, event_id: int) -> int: ...


#########################
#### IMPLEMENTATION #####
#########################
class InMemoryWebSocketManager:
    """
    In-memory WebSocket manager (single-instance only).
    Ready to be swapped with Redis implementation.
    """

    def __init__(self) -> None:
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, event_id: int) -> None:
        await websocket.accept()
        if event_id not in self.active_connections:
            self.active_connections[event_id] = set()

        self.active_connections[event_id].add(websocket)
        logger.info(
            "WebSocket connected",
            extra={"event_id": event_id, "connections": len(self.active_connections[event_id])},
        )

    def disconnect(self, websocket: WebSocket, event_id: int) -> None:
        if event_id not in self.active_connections:
            return

        self.active_connections[event_id].discard(websocket)
        remaining = len(self.active_connections[event_id])
        logger.info(
            "WebSocket disconnected",
            extra={"event_id": event_id, "remaining_connections": remaining},
        )
        if remaining == 0:
            del self.active_connections[event_id]

    async def broadcast_to_event(self, event_id: int, message: dict) -> None:
        if event_id not in self.active_connections:
            return

        connections = list(self.active_connections[event_id])  # safe copy

        async def _safe_send(ws: WebSocket):
            try:
                await ws.send_json(message)
                return None
            except WebSocketDisconnect:
                return ws
            except Exception as e:
                logger.warning(f"WebSocket send failed: {e}")
                return ws

        results = await asyncio.gather(
            *[_safe_send(ws) for ws in connections],
            return_exceptions=False,
        )
        disconnected = [ws for ws in results if ws is not None]

        for ws in disconnected:
            self.active_connections[event_id].discard(ws)

        if disconnected:
            logger.warning(
                f"Removed {len(disconnected)} dead WebSocket connections",
                extra={"event_id": event_id},
            )

    def get_connection_count(self, event_id: int) -> int:
        return len(self.active_connections.get(event_id, set()))


##################################
#### SINGLETON INSTANCE + DI #####
##################################
ws_manager_instance = InMemoryWebSocketManager()


def get_websocket_manager() -> WebSocketManagerProtocol:
    """Dependency for FastAPI endpoints"""
    return ws_manager_instance
