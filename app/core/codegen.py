import string, secrets
from app.core.uow import UnitOfWork
from app.core.config import settings
from app.exceptions.base import CodeGenFailed


async def generate_code(length: int) -> str:
    alphabet = string.ascii_uppercase + string.digits  # A-Z + 0-9
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def generate_unique_user_code(uow: UnitOfWork, length: int = 12) -> str:
    for _ in range(settings.max_tries_code_generation):
        code = await generate_code(length)
        existing = await uow.users.get_by_access_code(code)
        if not existing:
            return code
    raise CodeGenFailed()


async def generate_unique_event_code(uow: UnitOfWork, length: int = 12) -> str:
    for _ in range(settings.max_tries_code_generation):
        code = await generate_code(length)
        existing = await uow.events.get_by_code(code)
        if not existing:
            return code
    raise CodeGenFailed()
