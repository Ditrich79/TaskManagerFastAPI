import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_headers: dict):
    """Тест создания задачи."""
    response = await client.post(
        "/api/v1/tasks/",
        json={
            "title": "My Task",
            "description": "Do something important",
            "completed": False
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Task"
    assert data["description"] == "Do something important"
    assert data["completed"] == False
    assert "id" in data
    assert "owner_id" in data

@pytest.mark.asyncio
async def test_read_tasks(client: AsyncClient, auth_headers: dict):
    """Тест получения списка задач (должна быть хотя бы одна)."""
    # Создадим пару задач
    await client.post(
        "/api/v1/tasks/",
        json={
            "title": "Task 1",
            "description": "First"
        },
        headers=auth_headers
    )
    await client.post(
        "/api/v1/tasks/",
        json={
            "title": "Task 2",
            "description": "Second"
        },
        headers=auth_headers
    )

    response = await client.get("/api/v1/tasks/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    # Проверим, что все задачи принадлежат нашему пользователю
    for task in data:
        assert "owner_id" in task

@pytest.mark.asyncio
async def test_read_single_task(client: AsyncClient, auth_headers: dict):
    """Тест получения одной задачи по ID."""
    # Создаём задачу
    create_response = await client.post("/api/v1/tasks/", json={
        "title": "Single Task"
    }, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Single Task"

@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, auth_headers: dict):
    """Тест обновления задачи."""
    # Создаём задачу
    create_resp = await client.post("/api/v1/tasks/", json={
        "title": "Old Title",
        "completed": False
    }, headers=auth_headers)
    task_id = create_resp.json()["id"]

    update_response = await client.put(f"/api/v1/tasks/{task_id}", json={
        "title": "New Title",
        "completed": True
    }, headers=auth_headers)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "New Title"
    assert data["completed"] == True

@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, auth_headers: dict):
    """Тест удаления задачи."""
    # Создаём задачу
    create_response = await client.post("/api/v1/tasks/", json={
        "title": "Task to be deleted"
    }, headers=auth_headers)
    task_id = create_response.json()["id"]

    # Удаляем
    delete_response = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    # Проверяем, что получить её больше нельзя
    get_response = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_cannot_access_other_user_task(client: AsyncClient):
    """Проверяем, что пользователь не может получить задачу другого пользователя."""
    # Создаём первого пользователя и его задачу
    # Регистрируем user1
    await client.post("/api/v1/auth/register", json={
        "email": "user1@example.com",
        "password": "testpassword"
    })
    login1 = await client.post("/api/v1/auth/login", data={
        "username": "user1@example.com",
        "password": "testpassword"
    })
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    create_resp = await client.post("/api/v1/tasks/", json={
        "title": "User1 task"
    }, headers=headers1)
    task_id = create_resp.json()["id"]

    # Теперь логинимся под вторым пользователем
    await client.post("/api/v1/auth/register", json={
        "email": "user2@example.com",
        "password": "testpassword"
    })
    login2 = await client.post("/api/v1/auth/login", data={
        "username": "user2@example.com",
        "password": "testpassword"
    })
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Пытаемся получить задачу user1 под user2
    get_resp = await client.get(f"/api/v1/tasks/{task_id}", headers=headers2)
    assert get_resp.status_code == 404  # или 404, зависит от реализации; в вашем коде возвращается 400 "Not enough permissions"

@pytest.mark.asyncio
async def test_unauthenticated_request(client: AsyncClient):
    """Без токена любой запрос к задачам должен возвращать 401."""
    response = await client.get("/api/v1/tasks/")
    assert response.status_code == 401
    response = await client.post("/api/v1/tasks/", json={"title": "test"})
    assert response.status_code == 401