from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.features.users.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    result = db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def get_users_by_ids(db: Session, user_ids: list[int]) -> list[User]:
    if not user_ids:
        return []
    result = db.execute(select(User).where(User.id.in_(user_ids)))
    return list(result.scalars().all())


def create_user(db: Session, name: str, last_name: str, email: str, password: str) -> User:
    existing = get_user_by_email(db, email)
    if existing is not None:
        raise ConflictError("Email already registered")

    user = User(
        name=name,
        last_name=last_name,
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Email already registered") from None
    db.refresh(user)
    return user
