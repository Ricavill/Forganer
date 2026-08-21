from datetime import datetime

from pydantic import BaseModel


class MeetGroupCreate(BaseModel):
    name: str


class MeetGroupOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GroupMemberAdd(BaseModel):
    user_id: int


class GroupMemberOut(BaseModel):
    id: int
    user_id: int
    meet_group_id: int

    model_config = {"from_attributes": True}
