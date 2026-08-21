from datetime import datetime

from pydantic import BaseModel


class ActivityCreate(BaseModel):
    name: str
    description: str | None = None


class ActivityUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ActivityOut(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
