from pydantic import BaseModel, EmailStr, ConfigDict

# Схема для создания пользователя
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Схема для ответа с данными пользователя (без пароля)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)