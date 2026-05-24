from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.database import GetAsyncSession
from app.schemas.user import UserCreate, UserResponse
from app.crud import crud_user
from app.core.security import verify_password, create_access_token
from typing import Annotated


router = APIRouter()

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: GetAsyncSession):
    user = await crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists.",
        )
    user = await crud_user.create_user(db=db, user=user_in)
    return user

@router.post("/login")
async def login(db: GetAsyncSession, form_data: OAuth2Form):
    user = await crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}