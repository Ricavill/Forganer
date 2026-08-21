from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import create_access_token
from app.features.auth.schemas import Token
from app.features.users import service
from app.features.users.schemas import UserSignUp

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserSignUp, db: AsyncSession = Depends(get_db)):
    existing = await service.get_user_by_email(db, payload.email)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = await service.create_user(db, payload.name, payload.last_name, payload.email, payload.password)
    return Token(access_token=create_access_token(user.email))
