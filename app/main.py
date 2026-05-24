from fastapi import FastAPI
from app.api.v1.endpoints import auth, tasks

app = FastAPI(title="Task Manager API")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])


@app.get("/")
async def read_root():
    return {"message": "Hello, Task Manager!"}