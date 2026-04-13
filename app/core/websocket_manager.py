import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Set, Protocol, Optional
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
from app.core.logging import logger
from app.core.config import settings


################################
#### PROTOCOL (INTERFACE) #####
################################
class WebSocketManagerProtocol(Protocol):
    async def connect(self, websocket: WebSocket, event_id: int, user_id: Optional[int] = None) -> None: ...
    def disconnect(self, websocket: WebSocket, event_id: Optional[int] = None) -> None: ...
    async def broadcast_to_event(self, event_id: int, message: dict) -> None: ...
    def update_activity(self, websocket: WebSocket) -> None: ...


#########################
#### IMPLEMENTATION #####
#########################
class InMemoryWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.connection_metadata: Dict[WebSocket, dict] = {}

        self.PING_INTERVAL = settings.ping_interval
        self.IDLE_TIMEOUT = settings.idle_timeout
        self.MAX_CONNECTIONS_PER_EVENT = settings.max_connections_per_event

    async def connect(self, websocket: WebSocket, event_id: int, user_id: Optional[int] = None) -> None:
        if len(self.active_connections.get(event_id, set())) >= self.MAX_CONNECTIONS_PER_EVENT:
            try:
                await websocket.close(code=1013, reason="Event is at maximum capacity")
            except Exception:
                pass
            return

        if event_id not in self.active_connections:
            self.active_connections[event_id] = set()

        self.active_connections[event_id].add(websocket)

        self.connection_metadata[websocket] = {
            "event_id": event_id,
            "user_id": user_id,
            "connected_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
        }

        logger.info(
            "WebSocket connected",
            extra={"event_id": event_id, "user_id": user_id, "connections": len(self.active_connections[event_id])},
        )

        asyncio.create_task(self._heartbeat(websocket, event_id))

    def update_activity(self, websocket: WebSocket) -> None:
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["last_activity"] = datetime.now(timezone.utc)

    def disconnect(self, websocket: WebSocket, event_id: Optional[int] = None) -> None:
        if event_id is None and websocket in self.connection_metadata:
            event_id = self.connection_metadata[websocket].get("event_id")

        if event_id and event_id in self.active_connections:
            self.active_connections[event_id].discard(websocket)
            if not self.active_connections[event_id]:
                del self.active_connections[event_id]

        self.connection_metadata.pop(websocket, None)
        logger.info("WebSocket disconnected", extra={"event_id": event_id})

    async def _heartbeat(self, websocket: WebSocket, event_id: int):
        try:
            while True:
                await asyncio.sleep(self.PING_INTERVAL)

                if websocket not in self.connection_metadata:
                    break

                try:
                    await asyncio.wait_for(websocket.send_json({"type": "ping"}), timeout=3.0)
                except Exception:
                    break

                last_activity = self.connection_metadata.get(websocket, {}).get("last_activity")
                if last_activity and datetime.now(timezone.utc) - last_activity > timedelta(seconds=self.IDLE_TIMEOUT):
                    logger.info("Idle timeout - disconnecting", extra={"event_id": event_id})
                    break

        finally:
            await self._safe_disconnect(websocket, event_id)

    async def _safe_disconnect(self, websocket: WebSocket, event_id: int):
        try:
            await websocket.close()
        except Exception:
            pass
        self.disconnect(websocket, event_id)

    async def broadcast_to_event(self, event_id: int, message: dict) -> None:
        if event_id not in self.active_connections:
            return

        connections = list(self.active_connections[event_id])

        async def _safe_send(ws: WebSocket):
            try:
                await ws.send_json(message)
                return None
            except WebSocketDisconnect:
                return ws
            except Exception:
                return ws

        results = await asyncio.gather(*[_safe_send(ws) for ws in connections], return_exceptions=False)
        disconnected = [ws for ws in results if ws is not None]

        for ws in disconnected:
            self.active_connections[event_id].discard(ws)

        if disconnected:
            logger.warning(f"Removed {len(disconnected)} dead connections", extra={"event_id": event_id})


##################################
#### SINGLETON INSTANCE + DI #####
##################################
ws_manager_instance = InMemoryWebSocketManager()


def get_websocket_manager() -> WebSocketManagerProtocol:
    """Dependency for FastAPI endpoints"""
    return ws_manager_instance
