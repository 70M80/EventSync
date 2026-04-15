from datetime import date, timedelta
from pydantic import BaseModel, ConfigDict, model_validator
from app.schemas.user import UserRead


##############################
##### VALIDATION SCHEMAS #####
##############################


class EventAnswerCreate(BaseModel):
    date_from: date
    date_to: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_to < self.date_from:
            raise ValueError("'Date To' must be after 'Date From'")
        if self.date_to > date.today() + timedelta(days=365 + 2):
            raise ValueError("Date too far in the future")
        return self


###########################
#### RESPONSE SCHEMAS #####
###########################


class EventAnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_from: date
    date_to: date
    user: UserRead


class EventAnswerResult(BaseModel):
    event_answer: EventAnswerRead
    deleted_ids: list[int]


class EventAnswersRead(BaseModel):
    event_answers: list[EventAnswerRead]
