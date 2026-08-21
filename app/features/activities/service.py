from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.features.activities.models import Activity
from app.features.activities.schemas import ActivityCreate, ActivityUpdate


def find_similar_activity(db: Session, name: str, exclude_id: int | None = None) -> Activity | None:
    query = (
        select(Activity)
        .where(
            Activity.deleted_at.is_(None),
            func.similarity(Activity.name, name) >= settings.activity_similarity_threshold,
        )
        .order_by(func.similarity(Activity.name, name).desc())
    )
    if exclude_id is not None:
        query = query.where(Activity.id != exclude_id)
    result = db.execute(query)
    return result.scalars().first()


def _raise_if_similar(db: Session, name: str, exclude_id: int | None = None) -> None:
    similar = find_similar_activity(db, name, exclude_id)
    if similar is not None:
        raise ConflictError(
            f"An activity too similar to '{name}' already exists: '{similar.name}' (id={similar.id})"
        )


def create_activity(db: Session, payload: ActivityCreate) -> Activity:
    _raise_if_similar(db, payload.name)

    activity = Activity(name=payload.name, description=payload.description)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def list_activities(db: Session) -> list[Activity]:
    result = db.execute(select(Activity).where(Activity.deleted_at.is_(None)))
    return list(result.scalars().all())


def search_activities(db: Session, query: str) -> list[Activity]:
    """Typo-tolerant activity search: exact substring matches plus trigram-similar
    names, ranked by relevance."""
    similarity_expr = func.similarity(Activity.name, query)
    result = db.execute(
        select(Activity)
        .where(
            Activity.deleted_at.is_(None),
            or_(
                Activity.name.ilike(f"%{query}%"),
                similarity_expr >= settings.activity_search_min_similarity,
            ),
        )
        .order_by(similarity_expr.desc())
        .limit(settings.activity_search_limit)
    )
    return list(result.scalars().all())


def get_activity(db: Session, activity_id: int) -> Activity:
    result = db.execute(select(Activity).where(Activity.id == activity_id, Activity.deleted_at.is_(None)))
    activity = result.scalar_one_or_none()
    if activity is None:
        raise NotFoundError("Activity not found")
    return activity


def update_activity(db: Session, activity: Activity, payload: ActivityUpdate) -> Activity:
    data = payload.model_dump(exclude_unset=True)

    if "name" in data and data["name"] != activity.name:
        _raise_if_similar(db, data["name"], exclude_id=activity.id)

    for field, value in data.items():
        setattr(activity, field, value)
    db.commit()
    db.refresh(activity)
    return activity


def delete_activity(db: Session, activity: Activity) -> None:
    activity.deleted_at = datetime.now(timezone.utc)
    db.commit()
