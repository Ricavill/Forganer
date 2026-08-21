from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import create_access_token
from app.features.auth.schemas import Token
from app.features.users import service
from app.features.users.schemas import UserSignUp

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignUp, db: Session = Depends(get_db)):
    user = service.create_user(db, payload.name, payload.last_name, payload.email, payload.password)
    return Token(access_token=create_access_token(user.email))
