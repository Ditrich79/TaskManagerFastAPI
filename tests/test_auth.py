import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient): 
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    # Сначала зарегистрируем пользователя, чтобы он был в базе
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "testpassword"
    })
    # Теперь логинимся, передавая данные как форму
    response = await client.post("/api/v1/auth/login", data={
        "username": "login@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"