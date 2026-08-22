from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.features.auth.dependencies import get_current_user
from app.features.friends import service
from app.features.friends.schemas import (
    FriendInvitationOut,
    FriendOut,
    FriendRequestCreate,
    InterestedFriendOut,
)
from app.features.users.models import User

router = APIRouter(prefix="/friends", tags=["friends"], dependencies=[Depends(get_current_user)])


@router.post("/requests", response_model=FriendInvitationOut, status_code=status.HTTP_201_CREATED)
def send_request(
    payload: FriendRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.send_request(db, current_user.id, payload.to_user_id)


@router.get("/requests", response_model=list[FriendInvitationOut])
def list_incoming_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.list_incoming_requests(db, current_user.id)


@router.get("/requests/sent", response_model=list[FriendInvitationOut])
def list_sent_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.list_sent_requests(db, current_user.id)


@router.delete("/requests/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_request(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.cancel_request(db, invitation_id, current_user.id)


@router.post("/requests/{invitation_id}/accept", response_model=FriendInvitationOut)
def accept_request(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.accept_request(db, invitation_id, current_user.id)


@router.post("/requests/{invitation_id}/reject", response_model=FriendInvitationOut)
def reject_request(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.reject_request(db, invitation_id, current_user.id)


@router.get("", response_model=list[FriendOut])
def list_friends(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.list_friends(db, current_user.id)


@router.get("/interested", response_model=list[InterestedFriendOut])
def list_interested_friends(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.list_interested_friends(db, current_user.id, activity_id)
