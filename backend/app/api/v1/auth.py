from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt

from app.infrastructure.database import get_db
from app.infrastructure.models import User
from app.domain.schemas import UserLogin, LoginResponse, UserResponse, Token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Generates a JWT access token encoding the user's role and email."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=LoginResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Unified Login endpoint for Web and Mobile clients.
    Verifies credentials and issues a JWT token.
    """
    # Fetch user from DB asynchronously
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalars().first()
    
    # Note: Using mock password check. In prod, use passlib bcrypt `pwd_context.verify()`
    if not user or credentials.password != "password": 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Issue token containing role to allow React/Flutter clients to apply RBAC
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}, 
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            full_name=user.full_name
        ),
        token=Token(access_token=access_token, token_type="bearer")
    )
