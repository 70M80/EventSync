from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.exceptions.handlers import register_exception_handlers
from app.core.session import engine
from app.core.logging import logger
from app.api import event_answer, user, event
from app.api.websocket import router as websocket_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting application...")
    yield
    logger.info("Shutting down application...")
    if engine:
        await engine.dispose()


app = FastAPI(title="EventSync", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Access-Code"],
)

# Exception handler
register_exception_handlers(app)

# API routers
app.include_router(user.router)
app.include_router(event.router)
app.include_router(event_answer.router)
app.include_router(websocket_router)
