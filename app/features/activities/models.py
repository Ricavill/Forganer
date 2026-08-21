from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import AuditMixin, Base


class Activity(Base, AuditMixin):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(String(1000))
