from datetime import datetime

from pydantic import BaseModel

from app.features.opinions.models import Sentiment


class OpinionCreate(BaseModel):
    name: str
    description: str | None = None
    activity_id: int
    sentiment: Sentiment


class OpinionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    activity_id: int | None = None
    sentiment: Sentiment | None = None


class OpinionOut(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None
    activity_id: int
    sentiment: Sentiment
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
