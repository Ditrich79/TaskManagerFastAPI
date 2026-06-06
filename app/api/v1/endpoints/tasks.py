from fastapi import Depends, APIRouter, HTTPException, status
from app.utils.cache import get_redis, get_cache, set_cache, invalidate_user_tasks_cache
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
    task = await crud_task.create_task(db=db, task=task_in, owner_id=current_user.id)
    # Сбрасываем кеш этого пользователя
    await invalidate_user_tasks_cache(current_user.id)
    return task

@router.get("/", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
async def read_tasks(
    current_user: GetCurrentUser,
    db: GetAsyncSession,
    skip: int = 0,
    limit: int = 100,
):
    # Ключ кеша для данного пользователя
    cache_key = f"user:{current_user.id}:tasks:skip{skip}:limit{limit}"

    # Пробуем взять из кеша
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    # Если нет — запрашиваем БД
    tasks = await crud_task.get_tasks(db, owner_id=current_user.id, skip=skip, limit=limit)

    # Сериализуем объекты SQLAlchemy в Pydantic-схемы (чтобы в JSON корректно записать)
    tasks_response = [TaskResponse.model_validate(task) for task in tasks]

    # Сохраняем в кеш на 30 секунд
    await set_cache(cache_key, [item.model_dump() for item in tasks_response], expire=30)

    return tasks_response

@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def read_task(
    task_id: int,
    db: GetAsyncSession,
    current_user: GetCurrentUser,
):
    cache_key = f"user:{current_user.id}:task:{task_id}"

    cached = await get_cache(cache_key)
    if cached is not None:
        return cached
    
    db_task = await crud_task.get_task(db, task_id=task_id, owner_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_schema = TaskResponse.model_validate(db_task)
    task_dict = task_schema.model_dump()
    await set_cache(cache_key, task_dict, expire=30)

    return task_dict

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
    await invalidate_user_tasks_cache(current_user.id)
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
    await invalidate_user_tasks_cache(current_user.id)
    return