from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.session import engine
from app.api import user, event, event_response


@asynccontextmanager
async def lifespan(_app: FastAPI):
    print("Starting application...")
    yield
    print("Shutting down application...")
    if engine:
        await engine.dispose()


app = FastAPI(title="EventSync", lifespan=lifespan)

# API routers
app.include_router(user.router)
app.include_router(event.router)
app.include_router(event_response.router)
