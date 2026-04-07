from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.exceptions.handlers import register_exception_handlers
from app.core.session import engine
from app.core.logging import logger
from app.api import user, event, event_response


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting application...")
    yield
    logger.info("Shutting down application...")
    if engine:
        await engine.dispose()


app = FastAPI(title="EventSync", lifespan=lifespan)

# Exception handler
register_exception_handlers(app)

# API routers
app.include_router(user.router)
app.include_router(event.router)
app.include_router(event_response.router)
