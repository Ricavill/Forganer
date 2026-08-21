from datetime import datetime

from pydantic import BaseModel

from app.features.friends.models import InvitationStatus


class FriendRequestCreate(BaseModel):
    to_user_id: int


class FriendInvitationOut(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    status: InvitationStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class FriendOut(BaseModel):
    id: int
    name: str
    last_name: str
    email: str

    model_config = {"from_attributes": True}


class InterestedFriendOut(BaseModel):
    user_id: int
    name: str
    last_name: str
    sentiment: int
