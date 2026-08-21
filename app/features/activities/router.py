from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.features.activities import service
from app.features.activities.schemas import ActivityCreate, ActivityOut, ActivityUpdate
from app.features.auth.dependencies import get_current_user

router = APIRouter(prefix="/activities", tags=["activities"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def create_activity(payload: ActivityCreate, db: Session = Depends(get_db)):
    return service.create_activity(db, payload)


@router.get("", response_model=list[ActivityOut])
def list_activities(db: Session = Depends(get_db)):
    return service.list_activities(db)


@router.get("/search", response_model=list[ActivityOut])
def search_activities(q: str, db: Session = Depends(get_db)):
    return service.search_activities(db, q)


@router.get("/{activity_id}", response_model=ActivityOut)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    return service.get_activity(db, activity_id)


@router.patch("/{activity_id}", response_model=ActivityOut)
def update_activity(activity_id: int, payload: ActivityUpdate, db: Session = Depends(get_db)):
    activity = service.get_activity(db, activity_id)
    return service.update_activity(db, activity, payload)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = service.get_activity(db, activity_id)
    service.delete_activity(db, activity)
