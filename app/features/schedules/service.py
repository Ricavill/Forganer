from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.features.schedules.models import Schedule
from app.features.schedules.schemas import ScheduleCreate, ScheduleUpdate

OVERLAP_DETAIL = "A schedule already exists for that time range"


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def has_overlapping_schedule(
    db: Session, start_date: datetime, end_date: datetime, exclude_schedule_id: int | None = None
) -> bool:
    query = select(Schedule).where(
        Schedule.deleted_at.is_(None),
        Schedule.start_date < end_date,
        Schedule.end_date > start_date,
    )
    if exclude_schedule_id is not None:
        query = query.where(Schedule.id != exclude_schedule_id)
    result = db.execute(query)
    return result.first() is not None


def any_schedule_overlaps(
    db: Session, schedule_ids: list[int], start_date: datetime, end_date: datetime
) -> bool:
    """Whether any of the given (non-deleted) schedules overlaps [start_date, end_date)."""
    if not schedule_ids:
        return False
    query = select(Schedule).where(
        Schedule.id.in_(schedule_ids),
        Schedule.deleted_at.is_(None),
        Schedule.start_date < end_date,
        Schedule.end_date > start_date,
    )
    result = db.execute(query)
    return result.first() is not None


def create_schedule(db: Session, payload: ScheduleCreate) -> Schedule:
    if has_overlapping_schedule(db, payload.start_date, payload.end_date):
        raise ConflictError(OVERLAP_DETAIL)

    schedule = Schedule(start_date=payload.start_date, end_date=payload.end_date)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def list_schedules(db: Session) -> list[Schedule]:
    result = db.execute(select(Schedule).where(Schedule.deleted_at.is_(None)))
    return list(result.scalars().all())


def get_schedule(db: Session, schedule_id: int) -> Schedule:
    result = db.execute(select(Schedule).where(Schedule.id == schedule_id, Schedule.deleted_at.is_(None)))
    schedule = result.scalar_one_or_none()
    if schedule is None:
        raise NotFoundError("Schedule not found")
    return schedule


def update_schedule(db: Session, schedule: Schedule, payload: ScheduleUpdate) -> Schedule:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)

    if _as_utc(schedule.start_date) >= _as_utc(schedule.end_date):
        raise ValidationError("start_date must be before end_date")

    if has_overlapping_schedule(db, schedule.start_date, schedule.end_date, exclude_schedule_id=schedule.id):
        raise ConflictError(OVERLAP_DETAIL)

    db.commit()
    db.refresh(schedule)
    return schedule


def delete_schedule(db: Session, schedule: Schedule) -> None:
    schedule.deleted_at = datetime.now(timezone.utc)
    db.commit()
