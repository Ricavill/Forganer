from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.features.opinions.models import UserOpinion
from app.features.opinions.schemas import OpinionCreate, OpinionUpdate

INVALID_ACTIVITY_DETAIL = "Invalid activity_id"


def create_opinion(db: Session, user_id: int, payload: OpinionCreate) -> UserOpinion:
    opinion = UserOpinion(
        user_id=user_id,
        name=payload.name,
        description=payload.description,
        activity_id=payload.activity_id,
        sentiment=payload.sentiment,
    )
    db.add(opinion)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(INVALID_ACTIVITY_DETAIL)
    db.refresh(opinion)
    return opinion


def list_opinions(db: Session, user_id: int) -> list[UserOpinion]:
    result = db.execute(
        select(UserOpinion).where(UserOpinion.user_id == user_id, UserOpinion.deleted_at.is_(None))
    )
    return list(result.scalars().all())


def get_opinion(db: Session, user_id: int, opinion_id: int) -> UserOpinion:
    result = db.execute(
        select(UserOpinion).where(
            UserOpinion.id == opinion_id,
            UserOpinion.user_id == user_id,
            UserOpinion.deleted_at.is_(None),
        )
    )
    opinion = result.scalar_one_or_none()
    if opinion is None:
        raise NotFoundError("Opinion not found")
    return opinion


def update_opinion(db: Session, opinion: UserOpinion, payload: OpinionUpdate) -> UserOpinion:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(opinion, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(INVALID_ACTIVITY_DETAIL)
    db.refresh(opinion)
    return opinion


def delete_opinion(db: Session, opinion: UserOpinion) -> None:
    opinion.deleted_at = datetime.now(timezone.utc)
    db.commit()
