from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.features.auth.dependencies import get_current_user
from app.features.opinions import service
from app.features.opinions.schemas import OpinionCreate, OpinionOut, OpinionUpdate
from app.features.users.models import User

router = APIRouter(prefix="/opinions", tags=["opinions"])


@router.post("", response_model=OpinionOut, status_code=status.HTTP_201_CREATED)
def create_opinion(
    payload: OpinionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_opinion(db, current_user.id, payload)


@router.get("", response_model=list[OpinionOut])
def list_opinions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.list_opinions(db, current_user.id)


@router.get("/{opinion_id}", response_model=OpinionOut)
def get_opinion(
    opinion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_opinion(db, current_user.id, opinion_id)


@router.patch("/{opinion_id}", response_model=OpinionOut)
def update_opinion(
    opinion_id: int,
    payload: OpinionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    opinion = service.get_opinion(db, current_user.id, opinion_id)
    return service.update_opinion(db, opinion, payload)


@router.delete("/{opinion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opinion(
    opinion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    opinion = service.get_opinion(db, current_user.id, opinion_id)
    service.delete_opinion(db, opinion)
