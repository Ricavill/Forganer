from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.features.auth.dependencies import get_current_user
from app.features.meetings import service
from app.features.meetings.schemas import MeetCreate, MeetOut, MeetUpdate

router = APIRouter(prefix="/meets", tags=["meets"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=MeetOut, status_code=status.HTTP_201_CREATED)
def create_meet(payload: MeetCreate, db: Session = Depends(get_db)):
    return service.create_meet(db, payload)


@router.get("", response_model=list[MeetOut])
def list_meets(db: Session = Depends(get_db)):
    return service.list_meets(db)


@router.get("/{meet_id}", response_model=MeetOut)
def get_meet(meet_id: int, db: Session = Depends(get_db)):
    return service.get_meet(db, meet_id)


@router.patch("/{meet_id}", response_model=MeetOut)
def update_meet(meet_id: int, payload: MeetUpdate, db: Session = Depends(get_db)):
    meet = service.get_meet(db, meet_id)
    return service.update_meet(db, meet, payload)


@router.delete("/{meet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meet(meet_id: int, db: Session = Depends(get_db)):
    meet = service.get_meet(db, meet_id)
    service.delete_meet(db, meet)
