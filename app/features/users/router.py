from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.exceptions import NotFoundError
from app.core.security import create_access_token
from app.features.auth.dependencies import get_current_user
from app.features.auth.schemas import Token
from app.features.users import service
from app.features.users.models import User
from app.features.users.schemas import UserOut, UserSignUp

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignUp, db: Session = Depends(get_db)):
    user = service.create_user(db, payload.name, payload.last_name, payload.email, payload.password)
    return Token(access_token=create_access_token(user.email))


@router.get("/lookup", response_model=UserOut, dependencies=[Depends(get_current_user)])
def lookup_user_by_email(email: str, db: Session = Depends(get_db)):
    user = service.get_user_by_email(db, email)
    if user is None:
        raise NotFoundError("No user found with that email")
    return user


@router.get("/search", response_model=list[UserOut])
def search_users(
    q: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.search_users(db, q, exclude_user_id=current_user.id)
