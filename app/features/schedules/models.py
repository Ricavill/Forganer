from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import AuditMixin, Base


class Schedule(Base, AuditMixin):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]
