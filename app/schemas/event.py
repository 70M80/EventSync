from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    Field,
    model_validator,
    field_validator,
)
from typing import Annotated, Optional, Any
from app.core.config import settings
from app.schemas.user import UserReadWithAccessCode

NameStr = Annotated[str, StringConstraints(min_length=1, max_length=50, strip_whitespace=True)]
DescriptionStr = Annotated[str, StringConstraints(min_length=1, max_length=500, strip_whitespace=True)]
UsernameStr = Annotated[str, StringConstraints(min_length=1, max_length=20, strip_whitespace=True)]
MaxResponsesInt = Annotated[
    int,
    Field(
        ge=1,
        le=settings.max_responses_per_user,
        description="Maximum number of event responses per user",
    ),
]


# Helper function for password validation
def validate_password_strength(v: str) -> str:
    """Validate password strength. Always returns stripped password."""
    if not isinstance(v, str):
        raise ValueError("Password must be a string")

    stripped = v.strip()
    if len(stripped) < 5:
        raise ValueError("Password must be at least 5 characters long")
    if len(stripped) > 20:
        raise ValueError("Password must be no more than 20 characters long")

    return stripped


##############################
##### VALIDATION SCHEMAS #####
##############################


class EventCreate(BaseModel):
    name: NameStr
    username: UsernameStr
    password: str
    max_responses: MaxResponsesInt

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)


class EventUpdate(BaseModel):
    name: Optional[NameStr] = None
    description: Optional[DescriptionStr] = None
    max_responses: Optional[MaxResponsesInt] = None

    @model_validator(mode="before")
    @classmethod
    def handle_empty_values(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # Required fields:
        # If value is "" or null → remove from update
        # This prevents overwriting required fields with empty values
        for field in {"name"}:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    stripped = value.strip()
                    # ""
                    if stripped == "":
                        data.pop(field, None)
                    else:
                        data[field] = stripped
                # null
                elif value is None:
                    data.pop(field, None)

        # Optional fields:
        # If value is "" or null → convert to None (will be saved as NULL in DB)
        for field in {"description"}:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    stripped = value.strip()
                    data[field] = None if stripped == "" else stripped

        return data


###########################
#### RESPONSE SCHEMAS #####
###########################


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: Optional[str] = None
    admin_id: int
    max_responses: int


class EventCreateResponse(BaseModel):
    user: UserReadWithAccessCode
    event: EventRead
