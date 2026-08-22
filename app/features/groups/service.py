from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.features.groups.models import MeetGroup, MeetGroupUser
from app.features.groups.schemas import MeetGroupCreate

INVALID_USER_DETAIL = "Invalid user_id"


def create_group(db: Session, payload: MeetGroupCreate) -> MeetGroup:
    group = MeetGroup(name=payload.name)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def list_groups(db: Session) -> list[MeetGroup]:
    result = db.execute(select(MeetGroup).where(MeetGroup.deleted_at.is_(None)))
    return list(result.scalars().all())


def get_group(db: Session, group_id: int) -> MeetGroup:
    result = db.execute(select(MeetGroup).where(MeetGroup.id == group_id, MeetGroup.deleted_at.is_(None)))
    group = result.scalar_one_or_none()
    if group is None:
        raise NotFoundError("Group not found")
    return group


def add_member(db: Session, group_id: int, user_id: int) -> MeetGroupUser:
    existing = db.execute(
        select(MeetGroupUser).where(
            MeetGroupUser.meet_group_id == group_id,
            MeetGroupUser.user_id == user_id,
            MeetGroupUser.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    member = MeetGroupUser(meet_group_id=group_id, user_id=user_id)
    db.add(member)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(INVALID_USER_DETAIL) from None
    db.refresh(member)
    return member


def list_members(db: Session, group_id: int) -> list[MeetGroupUser]:
    result = db.execute(
        select(MeetGroupUser).where(
            MeetGroupUser.meet_group_id == group_id, MeetGroupUser.deleted_at.is_(None)
        )
    )
    return list(result.scalars().all())
