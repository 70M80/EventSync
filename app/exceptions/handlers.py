from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from .base import CustomHTTPException
from app.core.logging import logger


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(CustomHTTPException)
    async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
        payload = {
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "error_code": (exc.detail.get("error_code") if isinstance(exc.detail, dict) else None),
        }

        if exc.status_code >= 500:
            logger.error("Application exception", extra={"extra_data": payload})
        elif exc.status_code >= 400:
            logger.warning("Client/business exception", extra={"extra_data": payload})
        else:
            logger.info("Handled exception", extra={"extra_data": payload})

        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
            headers=exc.headers or None,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Convert errors to JSON-serializable format
        errors = []
        for error in exc.errors():
            error_dict = {
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "type": error.get("type"),
            }
            # Extract input value if present (stringify if not basic type)
            if "input" in error:
                input_val = error["input"]
                if isinstance(input_val, (str, int, float, bool, list, dict, type(None))):
                    error_dict["input"] = input_val
                else:
                    error_dict["input"] = str(input_val)
            errors.append(error_dict)

        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "error_code": "VALIDATION_ERROR",
                "success": False,
                "details": errors,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled exception",
            exc_info=True,
            extra={
                "extra_data": {
                    "path": request.url.path,
                    "method": request.method,
                }
            },
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "success": False,
            },
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        payload = {
            "path": request.url.path,
            "method": request.method,
            "status_code": 429,
            "error_code": "RATE_LIMIT_EXCEEDED",
        }

        logger.warning("Rate limit exceeded", extra={"extra_data": payload})

        return JSONResponse(
            status_code=429,
            content={
                "error": "Too many requests",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "success": False,
                "details": str(exc),
            },
        )
