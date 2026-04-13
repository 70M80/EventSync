from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from app.core.config import settings
from app.exceptions.handlers import register_exception_handlers
from app.core.session import engine
from app.core.limiter import limiter
from app.core.logging import logger
from app.api import event_answer, user, event, auth
from app.api.websocket import router as websocket_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting application...")
    yield
    logger.info("Shutting down application...")
    if engine:
        await engine.dispose()


app = FastAPI(title="EventSync", lifespan=lifespan)
app.state.limiter = limiter

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Access-Code"],
)
app.add_middleware(SlowAPIMiddleware)

# Exception handler
register_exception_handlers(app)

# API routers
app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(event.router, prefix="/api")
app.include_router(event_answer.router, prefix="/api")
app.include_router(websocket_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
