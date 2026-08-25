from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.features.auth.dependencies import get_current_user
from app.features.groups import service
from app.features.groups.schemas import GroupMemberAdd, GroupMemberOut, MeetGroupCreate, MeetGroupOut
from app.features.users.models import User

router = APIRouter(prefix="/groups", tags=["groups"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=MeetGroupOut, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: MeetGroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_group(db, payload, current_user.id)


@router.get("", response_model=list[MeetGroupOut])
def list_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.list_groups_for_user(db, current_user.id)


@router.get("/{group_id}", response_model=MeetGroupOut)
def get_group(group_id: int, db: Session = Depends(get_db)):
    return service.get_group(db, group_id)


@router.post("/{group_id}/members", response_model=GroupMemberOut, status_code=status.HTTP_201_CREATED)
def add_member(group_id: int, payload: GroupMemberAdd, db: Session = Depends(get_db)):
    service.get_group(db, group_id)
    return service.add_member(db, group_id, payload.user_id)


@router.get("/{group_id}/members", response_model=list[GroupMemberOut])
def list_members(group_id: int, db: Session = Depends(get_db)):
    service.get_group(db, group_id)
    return service.list_members(db, group_id)
