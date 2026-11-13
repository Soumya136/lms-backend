from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.auth.models import User
from app.domain.auth.schemas import UserCreate
from app.core.security import hash_password, verify_password


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Fetch a user by email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Fetch a user by database ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user in the database."""
    hashed_pwd = hash_password(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        name=user_in.name,
        is_active=True,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Verify user credentials and return the user if valid."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
