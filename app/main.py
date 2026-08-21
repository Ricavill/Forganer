from fastapi import FastAPI

from app.core.config import settings
from app.features.auth import router as auth
from app.features.bot_agent import router as bot_agent
from app.features.health import router as health
from app.features.users import router as users

app = FastAPI(title=settings.app_name)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(bot_agent.router)
