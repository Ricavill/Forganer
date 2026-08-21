from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import AuditMixin, Base


class Meet(Base, AuditMixin):
    __tablename__ = "meets"

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id"))
    meet_group_id: Mapped[int] = mapped_column(ForeignKey("meet_groups.id"))
