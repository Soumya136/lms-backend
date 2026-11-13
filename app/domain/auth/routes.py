from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.domain.auth.models import User
from app.domain.auth.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
)
from app.domain.auth.service import (
    get_user_by_email,
    create_user,
    authenticate_user,
)
from app.domain.auth.deps import get_current_active_user

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    existing_user = await get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    user = await create_user(db, user_in=user_in)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login with email & password (JSON body)",
)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Standard JSON login endpoint for web and mobile frontends."""
    user = await authenticate_user(db, email=user_in.email, password=user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email,
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )


@router.post(
    "/login/access-token",
    response_model=Token,
    summary="OAuth2 compatible form login (for Swagger UI Authorize button)",
)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """OAuth2 form-based login for interactive API docs (Swagger /docs)."""
    user = await authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email,
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current logged-in user profile",
)
async def read_current_user(
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve details of the currently authenticated user."""
    return current_user
