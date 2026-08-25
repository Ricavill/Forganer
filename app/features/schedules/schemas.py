from datetime import datetime, timezone

from pydantic import BaseModel, model_validator


class ScheduleCreate(BaseModel):
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def check_date_order(self) -> "ScheduleCreate":
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self

    @model_validator(mode="after")
    def check_not_in_past(self) -> "ScheduleCreate":
        start = self.start_date if self.start_date.tzinfo else self.start_date.replace(tzinfo=timezone.utc)
        if start < datetime.now(timezone.utc):
            raise ValueError("start_date cannot be in the past")
        return self


class ScheduleUpdate(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None


class ScheduleOut(BaseModel):
    id: int
    start_date: datetime
    end_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
