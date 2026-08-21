from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.features.auth.dependencies import get_current_user
from app.features.bot_agent import service
from app.features.bot_agent.schemas import ChatRequest, ChatResponse
from app.features.users.models import User

router = APIRouter(prefix="/bot-agent", tags=["bot-agent"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await service.chat(db, current_user.id, current_user.email, payload.message)
