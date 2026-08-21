from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.features.meetings.models import Meet
from app.features.meetings.schemas import MeetCreate, MeetUpdate
from app.features.schedules import service as schedules_service

INVALID_REFERENCE_DETAIL = "Invalid schedule_id or meet_group_id"
OVERLAP_DETAIL = "Another meeting already exists for that schedule's time range"


def _get_schedule_or_none(db: Session, schedule_id: int):
    try:
        return schedules_service.get_schedule(db, schedule_id)
    except NotFoundError:
        return None


def _other_active_schedule_ids(db: Session, exclude_meet_id: int | None = None) -> list[int]:
    query = select(Meet.schedule_id).where(Meet.deleted_at.is_(None))
    if exclude_meet_id is not None:
        query = query.where(Meet.id != exclude_meet_id)
    result = db.execute(query)
    return [row[0] for row in result.all()]


def _has_overlapping_meet(db: Session, schedule, exclude_meet_id: int | None = None) -> bool:
    other_schedule_ids = _other_active_schedule_ids(db, exclude_meet_id)
    return schedules_service.any_schedule_overlaps(db, other_schedule_ids, schedule.start_date, schedule.end_date)


def create_meet(db: Session, payload: MeetCreate) -> Meet:
    schedule = _get_schedule_or_none(db, payload.schedule_id)
    if schedule is None:
        raise ConflictError(INVALID_REFERENCE_DETAIL)

    if _has_overlapping_meet(db, schedule):
        raise ConflictError(OVERLAP_DETAIL)

    meet = Meet(schedule_id=payload.schedule_id, meet_group_id=payload.meet_group_id)
    db.add(meet)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(INVALID_REFERENCE_DETAIL)
    db.refresh(meet)
    return meet


def list_meets(db: Session) -> list[Meet]:
    result = db.execute(select(Meet).where(Meet.deleted_at.is_(None)))
    return list(result.scalars().all())


def get_meet(db: Session, meet_id: int) -> Meet:
    result = db.execute(select(Meet).where(Meet.id == meet_id, Meet.deleted_at.is_(None)))
    meet = result.scalar_one_or_none()
    if meet is None:
        raise NotFoundError("Meet not found")
    return meet


def update_meet(db: Session, meet: Meet, payload: MeetUpdate) -> Meet:
    data = payload.model_dump(exclude_unset=True)

    if "schedule_id" in data:
        schedule = _get_schedule_or_none(db, data["schedule_id"])
        if schedule is None:
            raise ConflictError(INVALID_REFERENCE_DETAIL)
        if _has_overlapping_meet(db, schedule, exclude_meet_id=meet.id):
            raise ConflictError(OVERLAP_DETAIL)

    for field, value in data.items():
        setattr(meet, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(INVALID_REFERENCE_DETAIL)
    db.refresh(meet)
    return meet


def delete_meet(db: Session, meet: Meet) -> None:
    meet.deleted_at = datetime.now(timezone.utc)
    db.commit()
