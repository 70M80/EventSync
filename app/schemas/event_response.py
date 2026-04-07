from datetime import date
from pydantic import BaseModel, ConfigDict, model_validator
from app.schemas.user import UserRead


##############################
##### VALIDATION SCHEMAS #####
##############################


class EventResponseCreate(BaseModel):
    date_from: date
    date_to: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_to < self.date_from:
            raise ValueError("date_to must be after date_from")
        return self


###########################
#### RESPONSE SCHEMAS #####
###########################


class EventResponseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_from: date
    date_to: date
    user: UserRead


class EventResponsesRead(BaseModel):
    event_responses: list[EventResponseRead]
