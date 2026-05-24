from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Annotated

from app.core.database import GetAsyncSession
from app.core.config import settings
from app.crud import crud_user
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
Oauth2Token = Annotated[str, Depends(oauth2_scheme)]

async def get_current_user(
    db: GetAsyncSession,
    token: Oauth2Token,  
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await crud_user.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


GetCurrentUser = Annotated[User, Depends(get_current_user)]