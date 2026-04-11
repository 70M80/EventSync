from fastapi import Request
from slowapi import Limiter


def access_code_or_ip_key(request: Request):
    access_code = request.headers.get("X-Access-Code")
    if access_code:
        return access_code

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=access_code_or_ip_key)
