from datetime import datetime

from pydantic import BaseModel

from app.features.bot_agent.models import MessageDirection


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    session_id: int
    reply: str


class ChatMessageOut(BaseModel):
    id: int
    direction: MessageDirection
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}
