from pydantic import BaseModel, ConfigDict, StringConstraints
from typing import Annotated

UsernameStr = Annotated[str, StringConstraints(min_length=1, max_length=20, strip_whitespace=True)]
EventCodeStr = Annotated[str, StringConstraints(min_length=12, max_length=12, strip_whitespace=True)]
EventPasswordStr = Annotated[str, StringConstraints(min_length=5, max_length=20, strip_whitespace=True)]


class UserCreate(BaseModel):
    event_code: EventCodeStr
    event_password: EventPasswordStr
    username: UsernameStr


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class UsersRead(BaseModel):
    users: list[UserRead]


class UserReadWithAccessCode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    access_code: str
