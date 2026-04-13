from pydantic import BaseModel, StringConstraints
from typing import Annotated

CodeStr = Annotated[str, StringConstraints(min_length=12, max_length=12, strip_whitespace=True)]


class Login(BaseModel):
    access_code: CodeStr
