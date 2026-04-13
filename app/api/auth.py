from fastapi import APIRouter, Depends, status, Request, Response
from app.schemas.user import UserReadWithAccessCode
from app.services.user_service import UserService
from app.dependencies.common import get_user_service
from app.core.limiter import limiter
from app.core.cookies import set_access_cookie
from app.schemas.auth import Login

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserReadWithAccessCode, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    data: Login,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_by_access_code(data.access_code)
    set_access_cookie(response, user.access_code)
    return user


@router.delete("/logout", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def logout(
    request: Request,
    response: Response,
):
    response.delete_cookie("access_code", path="/")
    return {"status": "ok"}
