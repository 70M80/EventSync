from fastapi import Cookie, Depends
from typing import Annotated
from app.services.user_service import UserService
from app.dependencies.common import get_user_service
from app.models.user import User
from app.exceptions.base import MissingAccessCode


async def get_access_code(
    access_code: Annotated[str | None, Cookie()] = None,
) -> str:
    """
    Get access_code from cookie
    """
    if not access_code:
        raise MissingAccessCode()

    return access_code


async def get_current_user(
    access_code: Annotated[str, Depends(get_access_code)],
    user_service: UserService = Depends(get_user_service),
) -> User:
    return await user_service.get_by_access_code(access_code)
