from fastapi import HTTPException
from typing import Optional


class CustomHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": detail,
                "error_code": error_code,
                "success": False,
            },
            headers=headers,
        )


class NoFieldsToUpdate(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="No fields to update",
            error_code="NO_FIELDS_TO_UPDATE",
        )


class PermissionDenied(CustomHTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Permission denied", error_code="PERMISSION_DENIED")


class CodeGenFailed(CustomHTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Failed to generate unique code", error_code="CODE_GEN_FAIL")


class MissingAccessCode(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Missing access code. Please provide X-Access-Code header",
            error_code="MISSING_ACCESS_CODE",
        )


class UnknownAccessCode(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Unknown access code",
            error_code="UNKNOWN_ACCESS_CODE",
        )


class MaximumEventAnswersReached(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code=409,
            detail="Maximum answers reached",
            error_code="MAXIMUM_EVENT_ANSWERS_REACHED",
        )


class EventFull(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code=409,
            detail="Event full",
            error_code="EVENT_FULL",
        )


class InvalidEventPassword(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Invalid event password",
            error_code="INVALID_PASSWORD",
        )


class InvalidAdminDelete(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Admin can not remove themselves",
            error_code="INVALID_ADMIN_DELETE",
        )


class UserAlreadyExistsInEvent(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="User with this username already exists in this event",
            error_code="USER_ALREADY_EXISTS_IN_EVENT",
        )


class UserNotFound(CustomHTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found", error_code="USER_NOT_FOUND")


class EventNotFound(CustomHTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Event not found", error_code="EVENT_NOT_FOUND")


class EventAnswerNotFound(CustomHTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Event answer not found", error_code="EVENT_ANSWER_NOT_FOUND")
