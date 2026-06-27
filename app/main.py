from fastapi import FastAPI
from app.api.v1.endpoints import auth, tasks

from contextlib import asynccontextmanager
from app.events.producer import start_producer, stop_producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_producer()
    yield
    await stop_producer()

app = FastAPI(title="Task Manager API", lifespan=lifespan)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])


@app.get("/")
async def read_root():
    return {"message": "Hello, Task Manager!"}