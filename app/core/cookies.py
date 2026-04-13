from fastapi import Response
from app.core.config import settings


def set_access_cookie(response: Response, access_code: str) -> None:
    """
    Cookie used in websockets
    """
    secure = settings.env == "production"
    response.set_cookie(
        key="access_code",
        value=access_code,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )
