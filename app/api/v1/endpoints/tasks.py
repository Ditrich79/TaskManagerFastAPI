from fastapi import Depends, APIRouter, HTTPException, status

from app.core.database import GetAsyncSession
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.crud import crud_task
from app.api.v1.dependencies import GetCurrentUser

router = APIRouter()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    task_in: TaskCreate,
    db: GetAsyncSession,
    current_user: GetCurrentUser,
):
    return await crud_task.create_task(db=db, task=task_in, owner_id=current_user.id)

@router.get("/", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
async def read_tasks(
    current_user: GetCurrentUser,
    db: GetAsyncSession,
    skip: int = 0,
    limit: int = 100,
):
    tasks = await crud_task.get_tasks(db, owner_id=current_user.id, skip=skip, limit=limit)
    return tasks

@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def read_task(
    task_id: int,
    db: GetAsyncSession,
    current_user: GetCurrentUser,
):
    db_task = await crud_task.get_task(db, task_id=task_id, owner_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def update_existing_task(
    task_id: int,
    task_in: TaskUpdate,
    db: GetAsyncSession,
    current_user: GetCurrentUser,
):
    db_task = await crud_task.update_task(db, task_id=task_id, task_in=task_in, owner_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_task(
    task_id: int,
    db: GetAsyncSession,
    current_user: GetCurrentUser,
):
    db_task = await crud_task.delete_task(db, task_id=task_id, owner_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return