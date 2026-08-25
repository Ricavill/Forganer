from datetime import datetime

from pydantic import BaseModel, field_validator


def _capitalize_name(name: str) -> str:
    name = name.strip()
    return name[:1].upper() + name[1:] if name else name


class ActivityCreate(BaseModel):
    name: str
    description: str | None = None

    @field_validator("name")
    @classmethod
    def capitalize_name(cls, value: str) -> str:
        return _capitalize_name(value)


class ActivityUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def capitalize_name(cls, value: str | None) -> str | None:
        return _capitalize_name(value) if value is not None else value


class ActivityOut(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
