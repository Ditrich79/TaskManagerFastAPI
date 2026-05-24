from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, task: TaskCreate, owner_id: int):
    db_task = Task(**task.model_dump(), owner_id=owner_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def get_tasks(db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Task)
        .where(Task.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_task(db: AsyncSession, task_id: int, owner_id: int):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
    )
    return result.scalars().first()

async def update_task(db: AsyncSession, task_id: int, owner_id: int, task_in: TaskUpdate):
    db_task = await get_task(db, task_id=task_id, owner_id=owner_id)
    if db_task:
        update_data = task_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        await db.commit()
        await db.refresh(db_task)
    return db_task

async def delete_task(db: AsyncSession, task_id: int, owner_id: int):
    db_task = await get_task(db, task_id=task_id, owner_id=owner_id)
    if db_task:
        await db.delete(db_task)
        await db.commit()
    return db_task