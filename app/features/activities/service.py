from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.features.activities.models import Activity
from app.features.activities.schemas import ActivityCreate, ActivityUpdate


def create_activity(db: Session, payload: ActivityCreate) -> Activity:
    activity = Activity(name=payload.name, description=payload.description)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def list_activities(db: Session) -> list[Activity]:
    result = db.execute(select(Activity).where(Activity.deleted_at.is_(None)))
    return list(result.scalars().all())


def get_activity(db: Session, activity_id: int) -> Activity:
    result = db.execute(select(Activity).where(Activity.id == activity_id, Activity.deleted_at.is_(None)))
    activity = result.scalar_one_or_none()
    if activity is None:
        raise NotFoundError("Activity not found")
    return activity


def update_activity(db: Session, activity: Activity, payload: ActivityUpdate) -> Activity:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)
    db.commit()
    db.refresh(activity)
    return activity


def delete_activity(db: Session, activity: Activity) -> None:
    activity.deleted_at = datetime.now(timezone.utc)
    db.commit()
