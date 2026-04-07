from fastapi import HTTPException, status, Header
from fastapi import Depends
from typing import Annotated
from app.services.user_service import UserService
from app.dependencies.common import get_user_service
from app.models.user import User


async def get_access_code(
    x_access_code: Annotated[str | None, Header(alias="X-Access-Code")] = None,
) -> str:
    """
    Get access_code from `X-Access-Code` header
    """
    if not x_access_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access code. Please provide X-Access-Code header.",
        )

    return x_access_code


async def get_current_user(
    access_code: Annotated[str, Depends(get_access_code)],
    user_service: UserService = Depends(get_user_service),
) -> User:
    return await user_service.get_by_access_code(access_code)
