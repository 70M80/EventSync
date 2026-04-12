from fastapi import APIRouter, Depends, status, Request
from app.schemas.user import UserCreate, UserReadWithAccessCode, UsersRead, UserRead
from app.services.user_service import UserService
from app.dependencies.auth import get_current_user
from app.dependencies.common import get_user_service
from app.dependencies.user import get_authorized_user
from app.models.user import User
from app.core.limiter import limiter

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserReadWithAccessCode, status_code=status.HTTP_201_CREATED)
@limiter.limit("2/minute")
async def create_user(
    request: Request,
    data: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.create_user(data)


@router.get("/me", response_model=UserReadWithAccessCode)
@limiter.limit("10/minute")
async def get_me(request: Request, user: User = Depends(get_current_user)):
    return user


@router.get("/", response_model=UsersRead)
@limiter.limit("10/minute")
async def get_event_users(
    request: Request,
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    users = await user_service.get_users_by_event_id(user.event_id)
    user_reads = [UserRead.model_validate(p) for p in users]
    return UsersRead(users=user_reads)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_user(
    request: Request,
    user: User = Depends(get_authorized_user),
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete_user(user)
