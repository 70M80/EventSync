from enum import Enum
from pydantic import BaseModel


class WSMessageType(str, Enum):
    """Types of WebSocket messages that can be sent to clients."""

    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    EVENT_RESPONSE_CREATED = "event_response_created"
    EVENT_RESPONSE_DELETED = "event_response_deleted"


class WSMessage(BaseModel):
    """Base WebSocket message structure."""

    type: WSMessageType
    data: dict
