from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.features.users.models import User
from app.features.users.service import get_user_by_email


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None or user.hashed_password is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
