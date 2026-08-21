from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.features.users.models import User
from app.features.users.service import get_user_by_email


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or user.hashed_password is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
