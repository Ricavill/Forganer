from datetime import datetime

from pydantic import BaseModel


class MeetCreate(BaseModel):
    schedule_id: int
    meet_group_id: int


class MeetUpdate(BaseModel):
    schedule_id: int | None = None
    meet_group_id: int | None = None


class MeetOut(BaseModel):
    id: int
    schedule_id: int
    meet_group_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MeetInviteResult(BaseModel):
    sent_to: list[str]
