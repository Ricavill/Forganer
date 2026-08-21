from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.features.activities import router as activities
from app.features.auth import router as auth
from app.features.bot_agent import router as bot_agent
from app.features.health import router as health
from app.features.meetings import router as meetings
from app.features.opinions import router as opinions
from app.features.schedules import router as schedules
from app.features.users import router as users

app = FastAPI(title=settings.app_name)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": exc.detail})


@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.detail})


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(bot_agent.router)
app.include_router(activities.router)
app.include_router(schedules.router)
app.include_router(opinions.router)
app.include_router(meetings.router)
