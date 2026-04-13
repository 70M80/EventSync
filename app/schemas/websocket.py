from enum import Enum
from pydantic import BaseModel


class WSMessageType(str, Enum):
    """Types of WebSocket messages that can be sent to clients."""

    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    EVENT_ANSWER_CREATED = "event_answer_created"
    EVENT_ANSWER_DELETED = "event_answer_deleted"
    AUTH_SUCCESS = "auth_success"


class WSMessage(BaseModel):
    """Base WebSocket message structure."""

    type: WSMessageType
    data: dict
