from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.session import engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    print("Starting application...")
    yield
    print("Shutting down application...")
    if engine:
        await engine.dispose()


app = FastAPI(title="EventSync", lifespan=lifespan)
